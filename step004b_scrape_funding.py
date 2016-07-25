from util import build_path

import os, codecs, sys
import xml.etree.ElementTree as ET
import pandas as pd


if __name__ == '__main__':
    DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/abstracts/diseases'
    OPATH = '/Users/erickpeirson/modelorganisms/ncbi/funding.csv'
    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    df = pd.DataFrame(columns=['PMID', 'Year', 'Term', 'GrantID', 'Acronym', 'Agency', 'Country'])

    for term in terms:
        for year in xrange(START_YEAR, END_YEAR):
            sys.stdout.flush()
            ty_dirpath = os.path.join(DATAPATH, term, str(year))
            if not os.path.exists(ty_dirpath):
                print '\r skipping', term, year, ' (no PubMed response)',
                continue

            for fname in os.listdir(ty_dirpath):
                if not fname.endswith('xml'):
                    continue

                pmid = fname.split('.')[0]

                r = ET.parse(build_path(term, year, fname, DATAPATH, make=False)).getroot()
                grantlist = r.find('.//GrantList')
                if not grantlist:
                    continue

                for grant in grantlist.findall('.//Grant'):
                    grant_id = getattr(grant.find('.//GrantID'), 'text', None)
                    acronym = getattr(grant.find('.//Acronym'), 'text', None)
                    agency = getattr(grant.find('.//Agency'), 'text', None)
                    country = getattr(grant.find('.//Country'), 'text', None)

                    i = df.shape[0] + 1
                    df[i] = [pmid, year, term, grant_id, acronym, agency, country]


                print '\r', term, year, fname,
    df.to_csv(OPATH, sep='\t')
