import os
import pandas as pd
import numpy as np
from multiprocessing import Pool
import cPickle as pickle
import time
import sys
import networkx as nx
from calc import dist_value
from util import parse_ner_hit
from itertools import combinations, islice, izip
import multiprocessing as mp


def _save_result(result):
    RESULTS_BASE = '/Users/erickpeirson/modelorganisms/ncbi/diversity_raw_funding'
    term, year, nih, m, v, s = result
    result_path = os.path.join(RESULTS_BASE, '' % (term, year, nih))
    with open(result_path, 'w') as f:
        pickle.dump(result, f)
    return


def calculate_diversity(pool, df, chunk_size=10000):
    if df.shape[0] == 0:
        return 0.

    subsets = []
    value_counts = df['#entity'].value_counts()
    combos = combinations(izip(value_counts.keys(), value_counts.values), 2)

    while True:
        result = pool.map(calculate_diversity_pair, islice(combos, chunk_size))
        if result:
            subsets.extend(result)
        else:
            break
    sums, counts = zip(*subsets)
    return np.sum(sums)/np.sum(counts)

def calculate_diversity_pair(pair):
    (i_full, N_i), (j_full, N_j) = pair
    i = parse_ner_hit(i_full)
    j = parse_ner_hit(j_full)

    N = N_i * N_j
    d = dist_value(i, j)
    values = np.repeat(d, N)
    return values.sum(), values.shape[0]

def calculate_diversity_chunk(iterator):
    from calc import dist_value
    from util import parse_ner_hit
    import numpy as np

    diversity = np.array([])
    for (i_full, N_i), (j_full, N_j) in iterator:
        i = parse_ner_hit(i_full)
        j = parse_ner_hit(j_full)

        N = N_i * N_j
        d = dist_value(i, j)
        diversity = np.concatenate((diversity, np.repeat(d, N)))
    return diversity.sum(), diversity.shape[0]


if __name__ == '__main__':
    NER_BASE = '/Users/erickpeirson/modelorganisms/ncbi/ner'
    FUNDING_BASE = '/Users/erickpeirson/modelorganisms/ncbi/funding/'
    RESULTS_BASE = '/Users/erickpeirson/modelorganisms/ncbi/diversity_raw_funding'


    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.
    pool = mp.Pool(processes=16)

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    df_results = pd.DataFrame(columns=['term', 'year', 'mean', 'nih'])
    jobs = []
    for year in xrange(START_YEAR, END_YEAR):
        df_combined_nih = pd.DataFrame()
        df_combined_not_nih = pd.DataFrame()
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

            df_year = df_term[df_term.year == year]
            if df_year.shape[0] == 0:
                continue

            try:
                df_year_nih = df_year[pmid_is_nih(df_year.document.values)]
                df_year_not_nih = df_year[pmid_is_not_nih(df_year.document.values)]
                print term, year, df_year_nih.shape[0]
            except IndexError:
                df_year_nih = None
                df_year_not_nih = df_year

            if df_year_nih is not None:
                df_combined_nih = df_combined_nih.append(df_year_nih)
            df_combined_not_nih = df_combined_not_nih.append(df_year_not_nih)

        print year
        d_nih = calculate_diversity(pool, df_combined_nih, chunk_size=5000)
        d_notnih = calculate_diversity(pool, df_combined_nih, chunk_size=5000)
        idx = d_nih.shape[0]
        df_results.loc[idx] = ('all', year, d_nih, 'nih')
        idx = d_nih.shape[0]
        df_results.loc[idx] = ('all', year, d_notnih, 'notnih')

        df_combined_nih.to_csv(os.path.join(RESULTS_BASE, 'all_%i_nih.csv' % year), sep='\t')
        df_combined_not_nih.to_csv(os.path.join(RESULTS_BASE, 'all_%i_notnih.csv' % year), sep='\t')
