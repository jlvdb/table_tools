import os
import subprocess


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
