import os
import subprocess
import sys

import numpy as np
from astropy.table import Table


def stilts_available():
    """
    Check whether stilts / topcat -stilts is definied in the environment and
    return it's invocation command if it exists.

    Returns
    -------
    stilts_path : string
        Working STILTS invoking command, if STILTS not available in environment
        the string is empty.
    """
    with open(os.devnull, 'w') as devnull:
        try:
            subprocess.call(["stilts"], stdout=devnull, stderr=devnull)
            stilts_path = "stilts"
        except FileNotFoundError:
            try:
                subprocess.call(
                    ["topcat", "-stilts"], stdout=devnull, stderr=devnull)
                stilts_path = "topcat -stilts"
            except FileNotFoundError:
                stilts_path = ""
        return stilts_path


def load_table(fpath, format, check_columns=[], tabinfo=""):
    """
    Wrapper for astropy.table.Table to load tables of various formats and
    checking the existance of required columns. Exiting python if a column does
    not exist. Convenience method for most scripts in ./data_table

    Parameters
    ----------
    fpath : string
        Data table file path.
    format : string
        Data table format description (see astropy.table for details).
    check_columns : list
        Check the existance of these column in the table.
    tabinfo : string
        Optional suffix to standard message to discriminate between multiple
        input table.

    Returns
    -------
    table : astropy.table.Table
        Successfully loaded data table
    """
    if not os.path.exists(fpath):
        sys.exit("ERROR: input file not found: " + fpath)
    # load table
    print("load input table%s: %s" % (tabinfo, fpath))
    table = Table.read(fpath, format=format)
    # check columns
    for col in check_columns:
        if col not in table.colnames:
            sys.exit("ERROR: table does not contain column '%s'" % col)
    return table


def read_pointing_file(fpath):
    """
    Read a file containing a list of pointings. These must be provided in five
    columns: pointing_name RAmin RAmax DECmin DECmax
    All angles are expected in degrees.

    Parameters
    ----------
    fpath : string
        Input file path to read.

    Returns
    -------
    table : list of lists
        List of pointings with numerical values converted float. Each item
        has the same input format as the input file:
        pointing_name RAmin RAmax DECmin DECmax
    """
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


def astropy_auto_extension(astropy_format_key):
    """
    Automatically find a good file extension name for a given
    astropy.table.Table format specifier.

    Parameters
    ----------
    astropy_format_key : string
        astropy.table.Table format specifier.

    Returns
    -------
    ext : string
        Proposed file extension name.
    """
    if "tex" in astropy_format_key:
        ext = "tex"
    elif "." in astropy_format_key:
        ext = astropy_format_key.split(".")[0]
    else:
        ext = astropy_format_key
    return ext


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
