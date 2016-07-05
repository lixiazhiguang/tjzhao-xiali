# import networkx as nx
from time import clock
import numpy as np
import itertools
import pprint
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


alpha = 0.3
beta = 0.49
epsilon = 1e-10

community_num = 6
alpha = 0.3
S_num = 2 ** community_num
betas = np.array([get_beta(count_bit(S)) for S in xrange(0, S_num)])
C_indexes = [[S for S in xrange(S_num) if S & (1<<c)] for c in xrange(community_num)]


def use_pagerank(read_file_name, write_file_name):
	G = nx.Graph()

	with open(read_file_name) as fp:
		for num, line in enumerate(fp):
			if num < 4:
				continue
			items = line.split('\t')
			i = int(items[0])
			j = int(items[1])
			G.add_edge(i, j)
			if num % 100000 == 0:
				print 'line', num

	pr = nx.pagerank(G)
	
	with open(write_file_name, 'w') as fp:
		for id, rank in pr.items():
			fp.write(str(id) + ',' + str(rank) + '\n')


class Node:
	def __init__(self):
		self.rank = 0.0
		self.P_array = np.zeros(community_num)
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

	def initial(self):
		self.H_array[0] = 1e100
		for c in xrange(community_num):
			if self.community & (1<<c):
				self.I_array[c] = self.rank
		
	def update_P(self):
		beta_H = np.array([betas[S] * self.H_array[S] for S in xrange(S_num)])
		exp_inf = np.array([max(beta_H[C_indexes[c]]) for c in xrange(community_num)])
		self.P_array = alpha * self.I_array + exp_inf

	def update_I(self, node_list):
		if len(self.neighbors) == 0:
			return 0

		diff_abs = 0.0
		for c, I_value in enumerate(self.I_array):
			all_P_u = [node_list[neighbor].P_array[c] for neighbor in self.neighbors]
			max_P = max(all_P_u)
			if max_P > I_value:
				self.I_array[c] = max_P
				diff_abs += abs(I_value - max_P)

		return diff_abs

	def update_H(self):
		c = 0
		for S in xrange(1, S_num):
			if not (S & (1<<c)): # c not in S
				c += 1
			self.H_array[S] = min(self.I_array[c], self.H_array[S ^ (1<<c)])

	def get_str(self, id):
		s2 = max(self.H_array * betas)
		s3 = sum(self.I_array)
		weight = int(s2 * 1e5) + int(s3 * 1e5 / community_num) / 1e5 + len(self.neighbors) / 1e9
		
		return str(id) + ',' + str(weight) + '\n'


def read_file(community_file, neighbor_file, rank_file):
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
		for id, node in enumerate(node_list):
			fp.write(node.get_str(id))


def main():
	community_file = 'dblp_community.txt'
	neighbor_file = 'dblp_graph.txt'
	rank_file = 'dblp_rank.txt'
	result_file = 'result/dblp_his.csv'

	node_list = read_file(community_file, neighbor_file, rank_file)

	start = clock()
	print 'initial'
	for node in node_list:
		node.initial()
		node.update_H()

	while 1:
		diff_count = 0.0

		print 'update P'
		for node in node_list:
			node.update_P()
		
		print 'update I, H'
		for node in node_list:
			diff_count += node.update_I(node_list)
			node.update_H()

		print 'difference', diff_count
		if diff_count < epsilon:
			break

	end = clock()
	print 'HIS:', end - start

	write_file(result_file, node_list)


if __name__ == '__main__':
	main()