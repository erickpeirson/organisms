import numpy as np
import cPickle as pickle
import csv

if __name__ == '__main__':
    RESULTS_BASE = '/Users/erickpeirson/modelorganisms/ncbi/diversity_raw'
    MEANS_PATH = '/Users/erickpeirson/modelorganisms/ncbi/diversity.csv'

    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    means = []
    for term in terms:
        for year in xrange(START_YEAR, END_YEAR):
            result_path = os.path.join(RESULTS_BASE, '%s_%i.pickle' % (term, year))
            print '\r', term, year
            with open(result_path, 'r') as f:
                _, _, samples = pickle.load(f)
                means.append([term, year, np.mean(samples), np.std(samples)])

    with open(MEANS_PATH, 'w') as f:
        writer = csv.writer(f)
        for row in means:
            writer.writerow(row)
