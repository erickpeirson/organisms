import os
import pandas as pd
import numpy as np


if __name__ == '__main__':
    MESH_TERMS = 'mesh_diseases.txt'
    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    base_abs = "/Users/erickpeirson/modelorganisms/ncbi/abstracts_raw/diseases"
    base_ner = "/Users/erickpeirson/modelorganisms/ncbi/ner"

    for term in terms:
        base_terms = os.path.join(base_abs, term)
        ner_terms = os.path.join(base_ner, '%s.csv' % term)
        ner_terms_out = os.path.join(base_ner, '%s_updated.csv' % term)

        pmid_dates = {}
        for year in os.listdir(base_terms):
            ypath = os.path.join(base_terms, year)
            for fname in os.listdir(ypath):
                if not fname.endswith('txt'):
                    continue
                pmid = int(fname.split('.')[0])
                pmid_dates[pmid] = int(year)

        df = pd.read_csv(ner_terms, sep='\t')
        df.year = pd.Series(np.zeros(df.document.shape[0]), index=df.index)
        df.year = df.apply(lambda row: pmid_dates[row.document], axis=1)
        df.to_csv(ner_terms_out, sep='\t')
        print '\r', term,
