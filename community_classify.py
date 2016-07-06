import csv
import louvain
import igraph as ig
import networkx as nx


def read_file(file_name):
    edge_list = []
    with open(file_name) as fp:
        for line in fp:
            nodes = line[:-1].split(',')
            edge_list.append((int(nodes[0]), int(nodes[1])))
    return edge_list


def writefile(file_name, graph_dict):
    with open(file_name, "w") as fp:
        for node in graph_dict.items():
            print node


def main(read_file_name, write_file_name):
    edge_list = read_file(read_file_name)
    gra = ig.Graph(0, edge_list)
    gra.es['weight'] = 1.0
    part = louvain.find_partition(graph=gra, method="Modularity", weight='weight')

    #print louvain.quality(gra, part, method='Significance')
    print gra.summary()
    print pa


if __name__ == '__main__':
    read_file_name = 'egp.ungraph.csv'
    write_file_name = 'new_community.csv'
    main(read_file_name,write_file_name)