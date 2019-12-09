import os

import numpy as np


def pointings_multi_matches(table, pointing_masks, o_folder, o_format):
    """
    Identify objects that are assigend to multiple pointings.

    Parameters
    ----------
    table : astropy.table.Table
        Input data table to be split in pointings.
    pointing_masks : array_like of bools
        Table of shape (n_pointings, len(table)) specifiying to which of the
        pointings an object belongs.
    o_folder : string
        Path to folder in which all output is collected.
    o_format : string
        astropy.table.Table format specifier.
    """
    global_mask = pointing_masks.sum(axis=0)
    mask_multi_match = global_mask > 1  # more than one match
    n_multi_match = np.count_nonzero(mask_multi_match)
    if n_multi_match > 0:
        print(
            ("WARNING: there are %d objects assigned to " % n_multi_match) +
            "multiple pointings")
        # create a table for inspection
        multi_path = os.path.join(
            o_folder, "multi_match.%s" % astropy_auto_extension(o_format))
        print("writing remaining objects to: %s" % multi_path)
        multi_table = table[mask_multi_match]
        multi_table.write(multi_path, format=o_format, overwrite=True)


def pointings_no_matches(table, pointing_masks, o_folder, o_format):
    """
    Identify objects that are assigend to no pointing.

    Parameters
    ----------
    table : astropy.table.Table
        Input data table to be split in pointings.
    pointing_masks : array_like of bools
        Table of shape (n_pointings, len(table)) specifiying to which of the
        pointings an object belongs.
    o_folder : string
        Path to folder in which all output is collected.
    o_format : string
        astropy.table.Table format specifier.
    """
    global_mask = pointing_masks.sum(axis=0)
    mask_no_match = global_mask == 0  # no match
    n_no_match = np.count_nonzero(mask_no_match)
    if n_no_match > 0:
        print("WARNING: %d objects have no matching pointing" % n_no_match)
        # create a table for inspection
        remainder_path = os.path.join(
            o_folder, "remainder.%s" % astropy_auto_extension(o_format))
        print("writing remaining objects to: %s" % remainder_path)
        remainder_table = table[mask_no_match]
        remainder_table.write(
            remainder_path, format=o_format, overwrite=True)


def pointings_write_tables(
        table, pointing_masks, pointing_names,
        o_folder, o_format, min_objects):
    """
    Write the pointing data tables, omitting empty ones.

    Parameters
    ----------
    table : astropy.table.Table
        Input data table to be split in pointings.
    pointing_masks : array_like of bools
        Table of shape (n_pointings, len(table)) specifiying to which of the
        pointings an object belongs.
    pointing_names : list of strings
        List of pointing names used for output file names.
    o_folder : string
        Path to folder in which all output is collected.
    o_format : string
        astropy.table.Table format specifier.
    min_objects : int
        Minimum number of objects a pointing must contain.
    """
    print("writing pointing catalogues to: %s" % o_folder)
    for i, mask in enumerate(pointing_masks):
        # throw out pointings with too few objects
        n_data = np.count_nonzero(mask)
        if n_data <= min_objects:
            print(
                ("WARNING: pointing %s rejected: " % pointing_names[i]) +
                ("insufficient objects (%d)" % n_data))
            continue
        # write the pointing data table
        pointing_table = table[mask]
        table_path = os.path.join(
            o_folder, "%s.%s" % (
                pointing_names[i], astropy_auto_extension(o_format)))
        pointing_table.write(table_path, format=o_format, overwrite=True)
