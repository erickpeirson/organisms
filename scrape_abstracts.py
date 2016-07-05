from util import build_path

import os, codecs
import xml.etree.ElementTree as ET


if __name__ == '__main__':
    DATAPATH = '/Users/erickpeirson/modelorganisms/ncbi/abstracts/diseases'
    OPATH = '/Users/erickpeirson/modelorganisms/ncbi/abstracts_raw/diseases'
    MESH_TERMS = 'mesh_diseases.txt'
    START_YEAR = 1975   # Starting in this year.
    END_YEAR = 2016    # Up to but not including this year.

    with open(MESH_TERMS, 'r') as f:
        terms = [line.strip() for line in f.readlines() if len(line) > 1]

    for term in terms:
        for year in xrange(START_YEAR, END_YEAR):
            # NCBI permits no more than 3 requests per second.
            time.sleep(0.5)
            sys.stdout.flush()
            for fname in os.listdir(os.path.join(DATAPATH, term, year)):
                if not fname.endswith('xml'):
                    continue

                r = ET.parse(build_path(term, year, fname, DATAPATH, make=False)).getroot()
                aparts = r.findall('.//AbstractText')

                if len(aparts) == 0:
                    continue

                abstext = '\n\n'.join([apart.text for apart in aparts])

                opath = build_path(term, year, fname.replace('.xml', '.txt'), OPATH, make=True)
                with codecs.open(opath, 'w', encoding="utf-8") as f:
                    f.write(opath)

                print '\r', term, year, fname,
