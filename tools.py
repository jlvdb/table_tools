import os
import subprocess
import sys

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
