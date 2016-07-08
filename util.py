import os


parse_ner_hit = lambda hit: hit.split('|')[0].split('?')[0].split(':')[-1]


def build_path(term, year, datafile, base='data', make=False):
    """
    Generate a path to a datafile for a specific term and year.

    Will attempt to recursively create any missing directories.

    Parameters
    ----------
    term : str
    year : int
    datafile : str
        E.g. 'pmids.txt'
    base : str
        Base directory for data. Defaults to ./data.

    Returns
    -------
    str
        Path to output file.
    """
    dirpath = os.path.join(base, term, str(year))
    if make and not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return os.path.join(dirpath, datafile)
