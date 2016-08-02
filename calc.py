import networkx as nx
import csv
import numpy as np
import pandas as pd
from itertools import chain


NIH_MODEL_ORGANISMS = [
    '10114',   # Rattus
    '10090',   # Mus musculus
    '7215',    # Drosophila
    '3701',    # Arabidopsis
    '9030',    # Gallus
    '7955',    # Danio rerio
    '4932',    # Saccharomyces cerevisiae
    '8353',    # Xenopus
    '4896',    # Schizosaccharomyces pombe
    '5140',    # Neurospora
    '6668',    # Daphnia
    '6239',    # Caenorhabditis elegans
    '44689',   # Dictyostelium discoideum
]

TAXONOMY_GRAPH = nx.read_graphml('/Users/erickpeirson/modelorganisms/ncbi/taxonomy.graphml')

ROOT = "-1"

ranks_in_order = [
    'Root',
    'superkingdom',
    'kingdom',
    'subkingdom',
    'phylum',
    'subphylum',
    'superclass',
    'class',
    'subclass',
    'infraclass',
    'superorder',
    'order',
    'suborder',
    'infraorder',
    'parvorder',
    'superfamily',
    'family',
    'subfamily',
    'tribe',
    'subtribe',
    'genus',
    'subgenus',
    'species group',
    'species subgroup',
    'species',
    'subspecies'][::-1]

rank_idx = np.arange(0, len(ranks_in_order))


lineage = lambda n: nx.shortest_path(TAXONOMY_GRAPH, ROOT, n)[::-1]
distance = lambda l: np.arange(1. + l).sum()*2.
distance_vect = np.vectorize(distance)

index_of = lambda rank: ranks_in_order.index(rank) if rank in ranks_in_order else 0


def lowest_shared_node(u, v):
    u_lineage = lineage(u)
    v_lineage = lineage(v)
    if 9605 in set(u_lineage) | set(v_lineage):
        raise ValueError('No humans alowed!')
    for i in u_lineage:
        for j in v_lineage:
            if i == j:
                return TAXONOMY_GRAPH.node[i]['rank']


def get_rank(u):
    return TAXONOMY_GRAPH.node[u]['rank']


def dist_value(i, j):
    rank = lowest_shared_node(i, j)

    value = distance(index_of(rank))
    if get_rank(i) == rank or get_rank(j) == rank:
        value /= 2.
    return value


def is_a_model_organism(u):
    u_lineage = lineage(u)
    for org in NIH_MODEL_ORGANISMS:
        if org in u_lineage:
            return org
    return False
