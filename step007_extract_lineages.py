import xml.etree.ElementTree as ET
import networkx as nx
import os


def extract_lineage(root):
    thisTaxId = int(root.find('.//TaxId').text)
    thisName = root.find('.//ScientificName').text
    thisRank = root.find('.//Rank').text


    # Build list of nodes (exclude no-rank nodes).
    lineage = []
    for taxon in root.find('.//LineageEx').findall('.//Taxon'):
        rank = taxon.find('.//Rank').text
        if rank == 'no rank':
            continue
        taxid = int(taxon.find('.//TaxId').text)

        name = taxon.find('.//ScientificName').text
        lineage.append((taxid, name, rank))

    lineage.append((thisTaxId, thisName, thisRank))
    return lineage


if __name__ == '__main__':
    TAXONOMY_BASE = '/Users/erickpeirson/modelorganisms/ncbi/taxonomy'
    GRAPH_PATH = '/Users/erickpeirson/modelorganisms/ncbi/taxonomy.graphml'
    REBASE_PATH = '/Users/erickpeirson/modelorganisms/ncbi/taxonomy_rebase.graphml'
    ONTOGRAPH_PATH = '/Users/erickpeirson/modelorganisms/ncbi/ontotaxonomy.graphml'
    graph = nx.DiGraph()
    graph_rebase = nx.DiGraph()
    ontograph = nx.DiGraph()
    for fname in os.listdir(TAXONOMY_BASE):
        print '\r', fname,
        if not fname.endswith('xml'):
            continue

        taxon_id = fname.split('.')[0]

        lineage = extract_lineage(ET.parse(os.path.join(TAXONOMY_BASE, fname)))
        graph.add_edge((-1, 'Root', 'Root'), lineage[0])
        graph_rebase.add_edge('-1', str(lineage[0]))
        for i, node in enumerate(lineage):
            if i == len(lineage) - 1:
                break
            graph.add_edge(node, lineage[i+1])
            graph_rebase.add_edge(str(node[0]), str(lineage[i+1][0]))
            ontograph.add_edge(node[2], lineage[i+1][2])

        if str(lineage[-1][0]) != taxon_id:
            graph.add_edge(node, (int(taxon_id), lineage[-1][1], lineage[-1][2]))
            graph_rebase.add_edge(str(lineage[-2][0]), taxon_id)

    nx.write_graphml(graph, GRAPH_PATH)
    nx.write_graphml(graph_rebase, REBASE_PATH)
    nx.write_graphml(ontograph, ONTOGRAPH_PATH)
