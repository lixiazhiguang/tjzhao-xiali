from __future__ import division
from time import clock
from numpy import mean


class Node:
	def __init__(self):
		self.neighbor_set = set()
		self.ES = 0.0
		
	def add_neighbor(self, neighbor):
		self.neighbor_set.add(neighbor)

	def compute_ES(self, node_list):
		t = 0
		for k in self.neighbor_set:
			t += len(node_list[k].neighbor_set & self.neighbor_set)

		n = len(self.neighbor_set)
		try:
			self.ES = n - t / n
		except ZeroDivisionError, e:
			self.ES = 0


def read_file(file_name):
	with open(file_name) as fp:
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
				print 'Reading file line', i

	return node_list


def write_file(file_name, node_list):
	with open(file_name, 'w') as fp:
		for id, node in enumerate(node_list):
			fp.write(str(id) + ',' + str(node.ES) + '\n')


def main():
	read_file_name = 'dblp_graph.txt'
	write_file_name = 'result/dblp_es.csv'
	
	results = []
	for i in range(20):
		node_list = read_file(read_file_name)

		a = clock()
		for node in node_list:
			node.compute_ES(node_list)
		b = clock()

		results.append(b - a)
		print "%.10f" % (b - a)

	print 'mean', "%.10f" % mean(results)
	write_file(write_file_name, node_list)


if __name__ == '__main__':
	main()
