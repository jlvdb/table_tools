import os
import sys

import astropandas as apd
import numpy as np

from .utils import astropy_auto_extension


def read_pointing_file(fpath, verbose=True):
    """
    Read a file containing a list of pointings. These must be provided in five
    columns: pointing_name RAmin RAmax DECmin DECmax
    All angles are expected in degrees.

    Parameters
    ----------
    fpath : string
        Input file path to read.
    verbose : boolean
        Whether to display the loaded file path.

    Returns
    -------
    table : list of lists
        List of pointings with numerical values converted float. Each item
        has the same input format as the input file:
        pointing_name RAmin RAmax DECmin DECmax
    """
    if verbose:
        print("load pointing file: %s" % fpath)
    pointings = []
    with open(fpath) as f:
        for n, rawline in enumerate(f, 1):
            if len(rawline.strip()) == 0:
                continue
            try:
                # get the RA-DEC bounds
                line = rawline.strip()
                pname, ra_decs = line.split(None, 1)
                RAmin, RAmax, DECmin, DECmax = [
                    float(s) for s in ra_decs.split()]
                pointings.append((pname, RAmin, RAmax, DECmin, DECmax))
            except (ValueError, IndexError):
                sys.exit(
                    ("ERROR: invalid format in line %d, " % n) +
                    "expected: name RAmin RAmax DECmin DECmax (in degrees)")
    return pointings


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
        apd.to_auto(multi_table, multi_path, ext="." + o_format)


def pointings_no_matches(table, pointing_masks, o_folder, o_format, write):
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
    write : boolean
        whether to write out the remainder table
    """
    global_mask = pointing_masks.sum(axis=0)
    mask_no_match = global_mask == 0  # no match
    n_no_match = np.count_nonzero(mask_no_match)
    if n_no_match > 0:
        print("WARNING: %d objects have no matching pointing" % n_no_match)
        if write:
            # create a table for inspection
            remainder_path = os.path.join(
                o_folder, "remainder.%s" % astropy_auto_extension(o_format))
            print("writing remaining objects to: %s" % remainder_path)
            remainder_table = table[mask_no_match]
            apd.to_auto(remainder_table, remainder_path, ext="." + o_format)


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
        apd.to_auto(pointing_table, table_path, ext="." + o_format)
