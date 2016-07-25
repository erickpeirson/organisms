import pandas as pd
import os

from util import build_path


if __name__ == '__main__':
    DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/data/diseases'
    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    for term in terms:
        for year in xrange(START_YEAR, END_YEAR):
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
