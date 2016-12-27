#!/bin/env python

from programsIO import max_cluster as mc
import argparse
from pprint import pprint as pp

def parse_args():
    """"""
    desc = "prints a list of the best energy' structures for every cluster"
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('maxcluster_output', 
                        help = 'path to maxcluster output')
    return parser.parse_args()

def main():
    """"""
    args = parse_args()
    clust = mc.MaxCluster(args.maxcluster_output)
    best_E = clust.filter_best_energy()
    for cluster, pdb in best_E:
        print pdb



if __name__ == '__main__':
    main()
