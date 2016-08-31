"""
"""

import MSA
import sys
import argparse
import os 
import shutil 


def parse_args():
    desc = "creates trunacted pdbs acording to alignment and templates"
    parser = argparse.ArgumentParser(description = 
               ("creates trunacted pdbs acording to alignment and  "
	         "template's limits"))
    parser.add_argument('MSA_file', help = 'path to MSA file')
    limits_help = 'file of format <blade# s_limit e_limit>'
    parser.add_argument('limits_file', help = limits_help)
    args = parser.parse_args()
    return args

def parse_limits(file_name):
    """parses limits file.
    Args:
    	file_name: path to a file with the format- blade# s_limit e_limit
    returns a dictionay of [blade] = (s_limit, e_limit)
    """
    f = open(file_name, 'r')
    limits = dict()
    for line in f:
        (blade, s_limit, e_limit) = line.split()
	limits[int(blade)] = (int(s_limit), int(e_limit))
    return limits

def create_truncated_pdb(original, limits):
    """creates a new pdb file containig only residues within limits in a folder
    named truncated_pdb.
    Args:
    	original: path to original pdb file
	limits: list of tuples of limits
    """
    dir = 'truncated_pdb'
    if dir not in os.listdir('.'):
        os.mkdir(dir)
    shutil.copy(original, dir)
    file = '{}/{}'.format(dir, 
                  original[original.rfind('/') + 1 if '/' in original else o:])
    f = open(file, 'rw').readlines()
    f = filter( lambda x: x.startswith('ATOM'), f)
    #from pprint import pprint as pp
    #pp(f)
    pdb_save_lines = list()
    for s_limit, e_limit in limits:
	blade_lines = [line for line in f if int(line[22:26]) >= s_limit
                                             and int(line[22:26]) <= e_limit]
	pdb_save_lines += blade_lines
    open(file, 'w').writelines(pdb_save_lines)

def _get_aligned_template_limits(seq, limits):
    """converts input template's blades indicesto the aligend indices. returns
    as list of tuples (s_limit, e_limit).
    Args: 
    	seq: template's sequence
	limits: dictionary od [blade] = (s, e)
    """
    map = MSA.get_index_map(seq)
    final = list()
    for blade in limits:
        (s_limit, e_limit) = limits[blade]
	final.append((map[s_limit], map[e_limit]))
    return final

def find_values_key(dictionary, val, step = 1):
    """returns the key of val in the dictionary"""
    #return dictionary.keys()[dictionary.values().index(val)]
    key = -1
    if val > max(dictionary.values()):
    	val = max(dictionary.values())
	print 'changed to max'
    elif val < min(dictionary.values()):
        val = min(dictionary.values())
	print 'changed to min'
    while key == -1:
        for k in dictionary:
	    if dictionary[k] == val:
	        return k
	val += step
    

def main():
    """"""
    args = parse_args()
    limits = parse_limits(args.limits_file)
    alignment = MSA.parse_MSA(args.MSA_file)
    aligned_limits = _get_aligned_template_limits(alignment[0].seq._data,
    						  limits)
    for record in alignment:
	record_map = MSA.get_index_map(record.seq._data)
        record_limits = list()
	for s, e in aligned_limits:
	    s_limit = find_values_key(record_map, s, -1)
	    e_limit = find_values_key(record_map, e, 1)
	    record_limits.append((s_limit, e_limit))
	path = 'pdb/' + record.name + '.pdb'
	print path
	create_truncated_pdb(path, record_limits)

if __name__ == "__main__":
    main()
