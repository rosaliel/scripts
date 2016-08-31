#!/usr/bin/env python
"""this script filters from a clustering only the best structure out of every
cluster (in terms of lowest energy). 
input:
1. max_clust from maxcluster output. looks like that:
       INFO  :    40 :       12                        1ta3B_ppk_2491.pdb
2. the pdb's with the score at the line starting with "pose". takes into acount
only the last score 
"""
from pprint import pprint
file =  open('max_clust')
d = dict()
for i in file:
	l = i.split()
	cluster  = l[4]
	name = l[5]
	if cluster not in d.keys():
		d[cluster]=list()
	d[cluster].append(name)
l = list()
for k in d.keys():
	if len(d[k]) == 1:
		l.append(d[k][0])
	else:
		scores = []
		for i in d[k]:
			pdb = open(i)
			line = ((filter(lambda x : ~x.find("pose"), 
			         pdb.readlines()))[0]).strip()
			scores.append(float(line.split()[-1]))
		l.append(d[k][scores.index(min(scores))])
for i in l:
	print i

