#!/bin/env python

import sys
import argparse
import os
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.Polypeptide import PPBuilder

def parse_args():
    """"""
    desc = 'Cuts the blades\'s lines from original pssm (of the full protein).'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('pdbs', 
                        help=('Path to directory containing the blade\'s pdbs. '
                              'The blades should come from a renumbered pdb!!'))
    parser.add_argument('PSSMs', help='Path to directory containing the PSSMs')

    return parser.parse_args()

def check_path(path):
    return os.path.exists(path)   

def find_pdb_limits(pdb_path):
    """Returns the first and last resseq of a pdb file, and the sequence of the
    peptide.
    """
    pdb = PDBParser().get_structure('',pdb_path)
    # takes the first (and only) polypeptide
    pp = PPBuilder().build_peptides(pdb)[0] 
    start =  pp[0].get_id()[1]
    end = pp[-1].get_id()[1]
    seq = pp.get_sequence()
    return (start, end, seq)

def get_pssm_sequence(pssm):
    """pssm is a list of lines of a pssm file. Returns the sequence (second 
    column of each line).
    """
    return ''.join([line.split()[1] for line in pssm])
    
def cut_pssm(pdb_path, pssm_path, output_path):
    """Cuts the pssm in pssm_path to the limits of the pdb in pdb_path. Ensures
    that the sequence is identical in pdb_path and the output pssm. Checks in
    offsets between  -+10.
    """
    start, end, pdb_seq = find_pdb_limits(pdb_path)
    
    full_pssm = open(pssm_path, 'r').readlines()
    header = full_pssm[0:3]
    full_pssm = full_pssm[3:] # removes header
    
    pssm = full_pssm[start-1: end]   
    pssm_seq = get_pssm_sequence(pssm)
    offset = range(-10,11)
    i_offset = -1
    
    while (pssm_seq != pdb_seq) and i_offset < len(offset):
        i_offset += 1
        pssm = full_pssm[start - 1 + offset[i_offset]: end + offset[i_offset]] 
        pssm_seq = get_pssm_sequence(pssm)
    
    name = os.path.basename(output_path)[:-5]    
    if pssm_seq == pdb_seq:
        if i_offset > -1:
            print name, ': offset was', offset[i_offset] 
        output = open(output_path, 'a')
        output.writelines(header)
        output.writelines(pssm)
    else:
        print 'Sequences of pdb and pssm did not match for ', name   
    


def main():
    args = parse_args()
    output_path = os.getcwd() + '/blade_pssm'
    os.mkdir(output_path)    
    for pdb in os.listdir(args.pdbs):
        pdb = args.pdbs + '/' + pdb
        if not pdb.endswith('.pdb'):
            continue        
        name = os.path.basename(pdb)[:-4]
        pssm = '{}/{}.pssm'.format(args.PSSMs, name)
        if not check_path(pssm):
            pssm = pssm.replace('pssm', 'PSSM')
            if not check_path(pssm):
                print 'No pssm file for ', name
                continue
        cut_pssm(pdb, pssm, '{}/{}.pssm'.format(output_path, name))
           
        

if __name__ == '__main__':
    main()
