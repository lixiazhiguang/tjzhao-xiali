# coding:utf-8
from __future__ import division
import numpy as np
from numpy.random import random_sample
import logging
from time import clock
from numpy import mean
from copy import deepcopy

__author__ = 'Isaac Lee'


class Node:
	def __init__(self, index, neighbors):
		self.sum_2 = 0.0
		self.index = index
		self.weight = 0.5

		self.mutual_neighbor = {}
		if len(neighbors):
			self.to_edge_weights = dict(zip(neighbors, [1 / len(neighbors)] * len(neighbors)))
		else:
			self.to_edge_weights = {}
		self.neighbor_set = set(neighbors)

	def initial(self, node_list):
		for k in self.neighbor_set:
			mutual_neighbor = node_list[k].neighbor_set & self.neighbor_set
			if len(mutual_neighbor) > 0:
				self.mutual_neighbor[k] = mutual_neighbor

		neighbor_num = len(self.neighbor_set)

		denominator = 0
		for nn in self.mutual_neighbor.values():
			denominator += len(nn)

		self.sum_2 = (1 + neighbor_num * (neighbor_num - 1)) / (1 + denominator)

	# use in undirected graph
	def update_node_weight(self, node_list):
		sum_1 = 0.0
		for j in self.to_edge_weights.keys():
			sum_temp = self.to_edge_weights[j]
			try:
				k_set = self.mutual_neighbor[j]
				for k in k_set:
					sum_temp += self.to_edge_weights[k] * node_list[k].to_edge_weights[j]
			except KeyError, e:
				pass
			sum_1 += sum_temp ** 2

		self.weight = sum_1 * self.sum_2

	# use in directed graph
	# def update_node_weight(self, node_list):
		# temp_dict = deepcopy(self.to_edge_weights)
		# for k in self.to_edge_weights.keys():
		# 	try:
		# 		j_set = self.mutual_neighbor[k]
		# 		temp_edge_weight = self.to_edge_weights[k]
		# 		for j in j_set:
		# 			temp_dict[j] += temp_edge_weight * node_list[k].to_edge_weights[j]
		# 	except KeyError, e:
		# 		pass

		# sum_1 = 0.0
		# for count_weight in temp_dict.values():
		# 	sum_1 += count_weight ** 2

		# self.weight = sum_1 * self.sum_2

	def update_edge_weight(self, node_list):
		neighbor_weight_sum = 0
		for node_id in self.to_edge_weights.keys():
			neighbor_weight_sum += node_list[node_id].weight

		diff_list = []
		for node_id in self.to_edge_weights.keys():
			if neighbor_weight_sum == 0:
				new_weight = 0
			else:
				new_weight = node_list[node_id].weight / neighbor_weight_sum
			diff_list.append(new_weight - self.to_edge_weights[node_id])
			self.to_edge_weights[node_id] = new_weight

		return diff_list

	def __str__(self):
		list_ = [self.index, self.weight]
		# for index, weight in self.to_edge_weights.items():
		# 	list_.append(index)
		# 	list_.append(str(weight))

		return ','.join(map(str, list_))


def read_data_file(file_name):
	with open(file_name) as fp:
		first_line = fp.readline()
		items = first_line.split(' ')
		node_num = int(items[0])
		neighbor_list = [[] for i in xrange(node_num)]

		for i, line in enumerate(fp):
			items = line[:-1].split(' ')
			fm = int(items[0])
			to = int(items[1])
			neighbor_list[fm].append(to)
			neighbor_list[to].append(fm)

			if i % 100000 == 0:
				print 'line', i

	node_list = [Node(node_id, neighbors) for node_id, neighbors in enumerate(neighbor_list)]

	return node_list


def write_data_file(file_name, node_list):
	with open(file_name, 'w') as fp:
		for node in node_list:
			if node.weight > 0:
				fp.write(str(node))
				fp.write('\n')


def main(read_file, write_file):
	nums = []
	node_list = read_data_file(read_file)
	print 'Initialing'
	c = clock()
	for node in node_list:
		node.initial(node_list)

	while 1:
		a = clock()
		for node in node_list:
			node.update_node_weight(node_list)
		diff_list = []
		for node in node_list:
			diff_list.extend(node.update_edge_weight(node_list))

		# score = paired_distances(node_weight_array, temp_node_weight_array, metric='cosine')
		score = np.sqrt((np.array(diff_list) ** 2).sum())
		# print score
		if score < 1e-10:
			break
		b = clock()
		print b - a, score
		nums.append(b - a)
	print 'mean', mean(nums), len(nums)
	d = clock()
	print 'all', d - c

	write_data_file(write_file, node_list)


if __name__ == '__main__':
	read_file = 'dblp_graph.txt'
	write_file = 'result/dblp_new.csv'
	main(read_file, write_file)