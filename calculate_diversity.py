import os
import pandas as pd
from multiprocessing import Pool
import cPickle as pickle
import time


def calculate_diversity(df, term, year):
    import networkx as nx
    from calc import *
    from util import parse_ner_hit
    from itertools import combinations

    graph_rebase = nx.read_graphml('graph_rebase.graphml')

    samples = []
    for i_full, j_full in combinations(df['#entity'].values, 2):
        i = parse_ner_hit(i_full)
        j = parse_ner_hit(j_full)

        samples.append(i, j, dist_value(i, j))

    return term, year, samples


def _save_result(result):
    RESULTS_BASE = '/Users/erickpeirson/modelorganisms/ncbi/diversity_raw'
    term, year, samples = result
    result_path = os.path.join(RESULTS_BASE, '%s_%i.pickle' % (term, year))
    with open(result_path, 'w') as f:
        pickle.dump(result, f)
    print term, year
    return


if __name__ == '__main__':
    NER_BASE = '/Users/erickpeirson/modelorganisms/ncbi/ner'

    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.
    p = Pool(8)

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    jobs = []
    for term in terms[:1]:
        term_path = os.path.join(NER_BASE, '%s_updated.csv' % term)
        df_term = pd.read_csv(term_path, sep='\t')
        for year in xrange(START_YEAR, START_YEAR + 2): # END_YEAR
            df_year = df_term[df_term.year == year]
            r = p.apply_async(calculate_diversity,
                              (df_year, term, year),
                              callback=_save_result)
            jobs.append(r)

    while True:
        time.sleep(0.5)
        done = 1. * sum([r for r in jobs if r.ready()])/len(jobs)
        print '\r', done,
        if done == 1:
            break
