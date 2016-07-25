import os
import pandas as pd
import numpy as np
from multiprocessing import Pool
import cPickle as pickle
import time
import sys


def calculate_diversity(df, term, year, nih):
    import networkx as nx
    from calc import dist_value
    from util import parse_ner_hit
    from itertools import combinations

    calculated = {}

    samples = []
    if df.shape[0] > 0:
        for i_full, j_full in combinations(df['#entity'].values, 2):
            i = parse_ner_hit(i_full)
            j = parse_ner_hit(j_full)

            value = calculated.get((i, j), None)
            if value is None:
                value = dist_value(i, j)
                calculated[(i, j)] = value
            samples.append((i, j, value))

    return term, year, samples, nih


def _save_result(result):
    RESULTS_BASE = '/Users/erickpeirson/modelorganisms/ncbi/diversity_raw_funding'
    term, year, samples, nih = result
    result_path = os.path.join(RESULTS_BASE, '%s_%i_%s.pickle' % (term, year, nih))
    with open(result_path, 'w') as f:
        pickle.dump(result, f)
    return


if __name__ == '__main__':
    NER_BASE = '/Users/erickpeirson/modelorganisms/ncbi/ner'
    FUNDING_BASE = '/Users/erickpeirson/modelorganisms/ncbi/funding/'

    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.
    p = Pool(16)

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    jobs = []
    for term in terms:
        term_path = os.path.join(NER_BASE, '%s_updated.csv' % term)
        df_term = pd.read_csv(term_path, sep='\t')

        funding_path = os.path.join(FUNDING_BASE, '%s.csv' % term)
        df_funding = pd.read_csv(funding_path, sep='\t', encoding='utf-8')

        is_nih = np.vectorize(lambda v: 'NIH' in v)
        NIH_Agencies = np.array(df_funding.Agency.unique())[is_nih(np.array(df_funding.Agency.unique()))]
        agency_is_nih = np.vectorize(lambda v: v in NIH_Agencies)
        nih_pmids = df_funding[agency_is_nih(df_funding)].PMID.values
        pmid_is_nih = np.vectorize(lambda v: v in nih_pmids)
        pmid_is_not_nih = np.vectorize(lambda v: v not in nih_pmids)

        for year in xrange(START_YEAR, END_YEAR):
            df_year = df_term[df_term.year == year]
            if df_year.shape[0] == 0:
                continue

            try:
                df_year_nih = df_year[pmid_is_nih(df_year.document.values)]
                df_year_not_nih = df_year[pmid_is_not_nih(df_year.document.values)]
            except IndexError:
                df_year_nih = None
                df_year_not_nih = df_year

            if df_year_nih:
                p.apply_async(calculate_diversity,
                              (df_year_nih, term, year, 'nih'),
                               callback=_save_result)
            p.apply_async(calculate_diversity,
                          (df_year_not_nih, term, year, 'not_nih'),
                           callback=_save_result)
