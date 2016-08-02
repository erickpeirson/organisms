import networkx as nx
import csv
import numpy as np
import pandas as pd
from itertools import chain


graph_rebase = nx.read_graphml('/Users/erickpeirson/modelorganisms/ncbi/taxonomy.graphml')

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


lineage = lambda n: nx.shortest_path(graph_rebase, ROOT, n)[::-1]
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
                return graph_rebase.node[i]['rank']


def get_rank(u):
    return graph_rebase.node[u]['rank']


def dist_value(i, j):
    rank = lowest_shared_node(i, j)

    value = distance(index_of(rank))
    if get_rank(i) == rank or get_rank(j) == rank:
        value /= 2.
    return value
