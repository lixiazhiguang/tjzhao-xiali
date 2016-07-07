import os
import networkx as nx


def compute_betweeness(file_path):
	G = nx.Graph()
	with open(file_path) as fp:
		first_line = fp.readline()
		for line in fp:
			nodes = line.split(' ')
			fm = int(nodes[0])
			to = int(nodes[1])
			G.add_edge(fm, to)

	score_dict = nx.betweenness_centrality(G)

	prefix = file_name.split('_')[0]
	new_file_path = 'betweeness/' + prefix + '.txt'

	with open(new_file_path, 'w') as fp:
		for id, betweeness in score_dict.items():
			fp.write(str(id) + ',' + str(betweeness) + '\n')


def get_top(file_path, k):
	with open(file_path) as fp:
		pairs = []
		for i, line in enumerate(fp):
			items = line[:-1].split(',')
			id = int(items[0])
			score = float(items[1])
			pairs.append([score, id])
		pairs.sort(reverse=True)

	file_name = file_path.split('/')[1]
	prefix = file_name.split('.')[0]
	new_file_path = 'top_k/' + prefix + '_' + str(k) + '.txt'

	with open(new_file_path, 'w') as fp:
		for pair in pairs[:k]:
			fp.write(str(pair[1]) + ',' + str(pair[0]) + '\n')

def main():
	path = os.getcwd()
	files = os.listdir(path)
	for file_name in files:
		if (file_name.find('graph') > -1):
			print file_name
			compute_betweeness(file_name)


if __name__ == '__main__':
	main()