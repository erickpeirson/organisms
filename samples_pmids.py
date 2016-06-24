import numpy as np
import pandas as pd
import os
DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/data/diseases'

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


if __name__ == '__main__':
    with open('mesh_diseases.txt', 'r') as f:
        diseases = [line.strip() for line in f.readlines() if len(line) > 1]


    for term in diseases:
        for year in xrange(1975, 2016):
            dpath = build_path(term, year, 'pmids.txt', DATAPATH)
            with open(dpath, 'r') as f:
                pmids = [line.strip() for line in f.readlines() if len(line) > 1]
            df = pd.DataFrame(data=pmids, columns=['PMID'])
            if df.size == 0:
                print 'no results for', term, year
                continue
            elif df.size < 1000:
                print 'small set for', term, year, 'with', df.size 
            dfpath = build_path(term, year, 'sample.csv', DATAPATH)
            df.sample(min(1000, df.size)).to_csv(dfpath)
            
