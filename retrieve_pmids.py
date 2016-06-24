from ncbi import esearch

import os
import sys
import time


def pubmed_for_mesh(term, year, retmax=10000):
    """
    Executes a PubMed search for a MeSH term limited to a single year.

    Parameters
    ----------
    term : str
        A MeSH term.
    year : int
        The publiation year to which results will be limited.
    retmax : int
        Maximum number of records to return. The maximum allowable value is
        10,000 (default: 10,0000).

    Returns
    -------
    str
        Raw XML response.
    """
    params = {
        'db': 'pubmed',
        'retmax': retmax,    # Number of results.
        'term': term,
        'field': 'Mesh',
        'mindate': year,
        'maxdate': year,    # Ranges are inclusive in NCBI.
        'datetype': 'pdat',    # Publication date.
    }
    return esearch(**params)


def build_path(term, year, datafile, base='data'):
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
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return os.path.join(dirpath, datafile)


if __name__ == '__main__':
    DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/data/diseases'
    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    for term in terms:
        for year in xrange(START_YEAR, END_YEAR):
            # NCBI permits no more than 3 requests per second.
            time.sleep(0.5)
            print '\rterm:', term, 'year:', year,
            sys.stdout.flush()
            pmids = pubmed_for_mesh(term, year)
            outpath = build_path(term, year, 'pmids.txt', DATAPATH)
            with open(outpath, 'w') as f:
                f.write('\n'.join(pmids))
