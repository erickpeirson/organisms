from ncbi import efetch
from util import build_path

import copy
import xml.etree.ElementTree as ET
import pandas as pd
import sys
import time




if __name__ == '__main__':
    DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/data/diseases'
    OPATH = '/Users/erickpeirson/modelorganisms/ncbi/abstracts/diseases'
    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    # We need this in here, since we want to use names from this namespace.
    def process_efetch_result(raw_result):
        """
        Metadata for each article should be stored in its own XML file.
        """
        root = ET.fromstring(raw_result.encode('utf-8'))
        for article in root.findall('PubmedArticle'):
            newTree = ET.ElementTree(element=copy.deepcopy(article))
            pmid = article.find('MedlineCitation/PMID').text
            treePath = build_path(term, year, '%s.xml' % pmid, OPATH, make=True)
            newTree.write(treePath, encoding='utf-8')

    for term in terms:
        for year in xrange(START_YEAR, END_YEAR):
            # NCBI permits no more than 3 requests per second.
            time.sleep(0.5)
            print '\rterm:', term, 'year:', year,
            sys.stdout.flush()

            df = pd.read_csv(build_path(term, year, 'sample.csv', DATAPATH))

            for i in xrange(0, df.size, 200):
                pmids = list(df.PMID[i:i+200])
                efetch(id=pmids, db='pubmed', rettype='xml',
                       handler=process_efetch_result)
