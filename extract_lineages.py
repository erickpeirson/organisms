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
    graph = nx.Graph()
    for fname in os.listdir(TAXONOMY_BASE):
        if not fname.endswith('xml'):
            continue

        lineage = extract_lineage(ET.parse(os.path.join(TAXONOMY_BASE, fname)))
        for i, node in enumerate(lineage):
            if i == len(lineage) - 1:
                break
            graph.add_edge(node, lineage[i+1])

    nx.write_graphml(graph, GRAPH_PATH)
