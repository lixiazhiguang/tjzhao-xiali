import networkx as nx
import numpy as np
from time import clock
import heapq
import csv


beta_table = [0, 0, 0.17, 0.25, 0.29, 0.30, 0.35]
def get_beta(length):
	try:
		return beta_table[length]
	except IndexError, e:
		return 0.35


def count_bit(num):
	count = 0
	while num > 0:
		num &= (num - 1)
		count += 1
	return count


eps = 1e-13
community_num = 6
alpha = 0.3
S_num = 2 ** community_num
betas = np.array([get_beta(count_bit(S)) for S in xrange(0, S_num)])
C_indexes = [[S for S in xrange(S_num) if S & (1<<c)] for c in xrange(community_num)]


def use_pagerank(read_file_name, write_file_name):
	G = nx.Graph()

	with open(read_file_name) as fp:
		first_line = fp.readline()
		for line in fp:
			items = line.split(' ')
			i = int(items[0])
			j = int(items[1])
			G.add_edge(i, j)

	print 'Running PageRank'
	start = clock()
	rank = nx.pagerank(G)
	end = clock()
	print 'PageRank running time:', end - start
	
	with open(write_file_name, 'w') as fp:
		for id, rank in rank.items():
			fp.write(str(id) + ',' + str(rank) + '\n')

	del G


class Node:
	def __init__(self):
		self.rank = 0.0
		self.I_array = np.zeros(community_num)
		self.H_array = np.zeros(S_num)
		self.neighbors = []
		self.community = 0

	def add_neighbor(self, neighbor):
		self.neighbors.append(neighbor)

	def set_community(self, community):
		self.community = community

	def set_page_rank(self, pagerank):
		self.rank = pagerank

	def get_str(self, id):
		s2 = max(self.H_array * betas)
		s3 = sum(self.I_array)
		weight = int(s2 * 1e5) + int(s3 * 1e5 / community_num) / 1e5 + len(self.neighbors) / 1e9
		
		return str(id) + ',' + str(weight) + '\n'
		

def read_file(rank_file, community_file, neighbor_file):
	with open(neighbor_file) as fp:
		first_line = fp.readline()
		items = first_line.split(' ')
		node_num = int(items[0])
		node_list = [Node() for i in xrange(node_num)]

		for i, line in enumerate(fp):
			items = line.split(' ')
			fm = int(items[0])
			to = int(items[1])
			node_list[fm].add_neighbor(to)
			node_list[to].add_neighbor(fm)
	
			if i % 100000 == 0:
				print 'neighbor file line', i

	with open(community_file) as fp:
		for i, line in enumerate(fp):
			try:
				community = int(line[:-1])
			except:
				print i, line
			node_list[i].set_community(community)

			if i % 100000 == 0:
				print 'community file line', i

	with open(rank_file) as fp:
		reader = csv.reader(fp, delimiter=',')
		for i, line in enumerate(reader):
			node_id = int(line[0])
			rank = float(line[1])
			node_list[node_id].set_page_rank(rank)

			if i % 100000 == 0:
				print 'rank file line', i

	return node_list


def write_file(result_file, node_list):
	with open(result_file, 'w') as fp:
		for id, node in node_list:
			fp.write(node.get_str(id))


def main():
	community_file = 'dblp_community.txt'
	neighbor_file = 'twitter_graph.txt'
	rank_file = 'twitter_rank.txt'
	result_file = 'result/dblp_his.csv'

	# use_pagerank(neighbor_file, rank_file)
	# return

	use_times = []
	for i in range(3):
		node_list = read_file(rank_file, community_file, neighbor_file)
	
		print 'Running HIS'
		start = clock()
	
		# inital I
		for node in node_list:
			for c in xrange(community_num):
				if node.community & (1<<c):
					node.I_array[c] = node.rank
	
		# initial heap
		heap_list = []
		entry_finder = {}
		for node in node_list:
			entry = [-node.rank, node]
			entry_finder[node] = entry
			heap_list.append(entry)
		heapq.heapify(heap_list)
	
		while heap_list:
			rank, node = heapq.heappop(heap_list)
			del entry_finder[node]
	
			H_array = node.H_array
			I_array = node.I_array
	
			# update H
			H_array[0] = 1e100
			c = 0
			for S in xrange(1, S_num):
				if not (S & (1<<c)): # c not in S
					c += 1
				H_array[S] = min(I_array[c], H_array[S ^ (1<<c)])
	
			# update P
			beta_H = np.array([betas[S] * H_array[S] for S in xrange(S_num)])
			exp_inf = np.array([max(beta_H[C_indexes[c]]) for c in xrange(community_num)])
			P_array = alpha * I_array + exp_inf
	
			# update node's neighbors
			for node_id in node.neighbors:
				node_v = node_list[node_id]
				for c in xrange(community_num):
					P_u_c = P_array[c]
					if P_u_c > node_v.I_array[c] + eps:
						node_v.I_array[c] = P_u_c  # update neighbor's I
	
						if P_u_c > node_v.rank + eps:
							node_v.rank = P_u_c
	
							if node_v in entry_finder:
								entry_finder[node_v][0] = -P_u_c
							else:
								entry = [-P_u_c, node_v]
								entry_finder[node_v] = entry
								heapq.heappush(heap_list, entry)
	
		end = clock()
		print 'HIS:', end - start
		use_times.append(end - start)

	print 'mean time', np.mean(use_times)

	write_file(result_file, node_list)


if __name__ == '__main__':
	main()
