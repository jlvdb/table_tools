import os
import subprocess
import sys
from collections import OrderedDict

from astropy.table import Table


def read_footprint_file(fpath):
    """
    Read a footprint file with a list of survey names with corresponding RA/DEC
    limits and its footprint area.

    Parameters
    ----------
    fpath : string
        Data table file path.

    Returns
    -------
    surveys : OrderedDict
        Dictionary with survey names as keys and (RAmin, RAmax, DECmin, DECmax,
        area) as values.
    """
    print("load footprint list: %s" % fpath)
    surveys = OrderedDict()
    with open(fpath) as f:
        for n, rawline in enumerate(f, 1):
            if len(rawline.strip()) == 0 or rawline.startswith("#"):
                continue
            try:
                # get the RA-DEC bounds
                line = rawline.strip()
                ra_decs_area, survey_name = line.rsplit(None, 1)
                RAmin, RAmax, DECmin, DECmax, area = [
                    float(s) for s in ra_decs_area.split()]
                surveys[survey_name] = (RAmin, RAmax, DECmin, DECmax, area)
            except (ValueError, IndexError):
                sys.exit(
                    ("ERROR: invalid format in line %d, " % n) +
                    "expected: RAmin RAmax DECmin DECmax area name")
    return surveys


def load_table(fpath, format, check_columns=[], tabinfo="", verbose=True):
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
    if verbose:
        print("load input table%s: %s" % (tabinfo, fpath))
    table = Table.read(fpath, format=format)
    # check columns
    for col in check_columns:
        if col not in table.colnames:
            sys.exit("ERROR: table does not contain column '%s'" % col)
    return table


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
