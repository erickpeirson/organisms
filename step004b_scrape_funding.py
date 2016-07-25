from util import build_path

import os, codecs, sys
import xml.etree.ElementTree as ET
import pandas as pd


if __name__ == '__main__':
    DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/abstracts/diseases'
    OPATH = '/Users/erickpeirson/modelorganisms/ncbi/funding/'
    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]



    found = 0.    # Monitoring.
    tried = 0.
    idx = 0
    for term in terms:
        df = pd.DataFrame(columns=['PMID', 'Year', 'Term', 'GrantID',
                                   'Acronym', 'Agency', 'Country'])
        for year in xrange(START_YEAR, END_YEAR):
            sys.stdout.flush()    # Monitoring.
            ty_dirpath = os.path.join(DATAPATH, term, str(year))
            if not os.path.exists(ty_dirpath):
                # Some term-year combinations yielded no records.
                print '\r skipping', term, year, ' (no PubMed response)',
                continue

            for fname in os.listdir(ty_dirpath):
                tried += 1.    # For monitoring only.

                if not fname.endswith('xml'):    # Skip hidden/unrelated files.
                    continue

                pmid = fname.split('.')[0]

                # PubMed XML records are already on disk, separated into
                #  separate files for each record.
                rec_path = build_path(term, year, fname, DATAPATH, make=False)
                r = ET.parse(rec_path).getroot()

                # Only around 20% of records actually have grant information.
                #  This improves as we move forward to more recent publications.
                grantlist = r.find('.//GrantList')
                if grantlist is None:
                    continue

                # There can be several grants per publication.
                for grant in grantlist.findall('.//Grant'):
                    # Grant records vary in their level of completeness.
                    grant_id = getattr(grant.find('.//GrantID'), 'text', None)
                    acronym = getattr(grant.find('.//Acronym'), 'text', None)
                    agency = getattr(grant.find('.//Agency'), 'text', None)
                    country = getattr(grant.find('.//Country'), 'text', None)

                    # New row in the dataframe.

                    df.loc[idx] = [pmid, year, term, grant_id, acronym, agency, country]
                    found += 1.
                    idx += 1

            print '\r', term, year, fname, found/tried
        df.to_csv(os.path.join(OPATH, '%s.csv' % term), sep='\t')
