import networkx as nx
import numpy as np
import community as cm
import pprint


def read_file(file_name):
	with open(file_name) as fp:
		G = nx.Graph()

		first_line = fp.readline()
		for line in fp:
			nodes = map(int, line[:-1].split(' '))
			G.add_edge(nodes[0], nodes[1])

	return G


def write_file(G, file_name):
	partition = cm.best_partition(G)

	with open(file_name, 'w') as fp:
		for node_id, c_id in partition.items():
			fp.write(str(node_id) + ',' + str(c_id) + '\n')

	return

	community_num = max(partition.values())
	hist, bin_edges = np.histogram(partition.values(), bins=range(community_num))
	indexes = bin_edges[hist>5]
	index_set = set(indexes)

	with open(file_name, 'w') as fp:
		for node_id, c_id in partition.items():
			if c_id in index_set:
				fp.write(str(node_id) + ',' + str(c_id) + '\n')


def main():
	read_file_name = 'dblp_graph.txt'
	write_file_name = 'dblp_community2.txt'
	G = read_file(read_file_name)
	write_file(G, write_file_name)


if __name__ == '__main__':
	main()
