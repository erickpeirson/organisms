"""
Given a list of NCBI Taxonomy IDs, retrieve data from the Taxonomy database.
"""

import argparse, codecs, time, os
import pandas as pd
from itertools import repeat

from ncbi import efetch


def retrieve_taxon(taxon_id, taxa_datapath):
    """
    Executes a PubMed search for a MeSH term limited to a single year.

    Parameters
    ----------
    taxon_id : int
    taxa_datapath : str or unicode
    skip : bool

    Returns
    -------

    """

    _taxon_handler = lambda raw: raw.encode('utf-8')

    taxon_path = os.path.join(taxa_datapath, '%i.xml' % taxon_id)
    if os.path.exists(taxon_path):
        return

    raw_result = efetch(handler=_taxon_handler, id=taxon_id, db='taxonomy', rettype='xml')
    with codecs.open(taxon_path, 'w', encoding='utf-8') as f:
        f.write(raw_result)
    time.sleep(0.4)    # Don't overload NCBI.
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Retrieve NCBI Taxonomy data for LINNAEUS NER results')
    parser.add_argument('--linnaeus', dest='nerpath', action='store',
                        help='Path to LINNAEUS NER results (CSV)')
    parser.add_argument('--results', dest='taxa_datapath', action='store',
                        help='Location to store Taxonomy XML results')

    args = parser.parse_args()

    if not os.path.exists(args.nerpath):
        raise IOError('No such file: %s' % args.nerpath)

    ner_df = pd.read_csv(args.nerpath, sep='\t')

    taxa = set()
    for entity in ner_df['#entity'].values:
        ents = [e.split('?')[0] for e in entity.split('|')]
        for ent in ents:
            taxa.add(ent.split(':')[-1])

    map(retrieve_taxon, list(taxa), repeat(args.taxa_datapath, len(taxa)))
