from util import build_path

import os, codecs, sys
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
            sys.stdout.flush()
            ty_dirpath = os.path.join(DATAPATH, term, str(year))
            if not os.path.exists(ty_dirpath):
                print '\r skipping', term, year, ' (no PubMed response)',
                continue

            for fname in os.listdir(ty_dirpath):
                if not fname.endswith('xml'):
                    continue

                opath = build_path(term, year, fname.replace('.xml', '.txt'), OPATH, make=True)
                # if os.path.exists(opath):    # Already done.
                #     print '\r skipping', term, year, ' (already done)',
                #     continue

                r = ET.parse(build_path(term, year, fname, DATAPATH, make=False)).getroot()
                aparts = r.findall('.//AbstractText')

                if len(aparts) == 0:
                    continue

                abstext = u'\n\n'.join([apart.text for apart in aparts if apart.text]).strip()
                if len(abstext) < 2:
                    continue

                with codecs.open(opath, 'w', encoding="utf-8") as f:
                    f.write(abstext)

                print '\r', term, year, fname,
