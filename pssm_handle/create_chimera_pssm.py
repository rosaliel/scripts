#!/bin/env python

import sys
import argparse
import re
import os
from pprint import pprint
import xml.etree.ElementTree as ET

def parse_args():
    """"""
    desc = ''
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('pdb', 
      help=('Path to chimera. Make sure it has segment comments starting with '
            '##Begin comments## and ends with ##End comments##.'))
    parser.add_argument('xml', help='xml with a `segment` tag')        
    parser.add_argument('pssms', nargs = '+', action = 'store',
      help=('Paths to the frames\' pssms and the directories of the blades\' '
            'pssms, in the right order. For example, a design with two frames '
            'and 1 chimera should look like: <path to frame1> <path to '
            'directory with chimara 1 pssms> <path to frame2>'))
    return parser.parse_args()
 
def extract_pssm_lines(pssm_path):
    """Returns a list of the lines of the pssm, not including header or last 
    lines.
    Args:
    pssm_path -- path to pssm file
    Return:
    list of the lines of the pssm 
    """
    pssm = open(pssm_path, 'r').readlines()
    lines =  [line for line in pssm if not (re.search('[a-zA-Z]{2,}', line) or 
                                            line == '\n' or 
                                            not re.search('\d', line))]
    if not lines[-1].endswith('\n'):
        lines[-1] += '\n'
    return lines

def get_comments(pdb_path):
    """Returns comment lines from the pdb"""
    pdb = open(pdb_path, 'r').readlines()
    indes_b = [i for i in range(len(pdb)) if '##Begin comments##' in pdb[i]][0]
    indes_e = [i for i in range(len(pdb)) if '##End comments##' in pdb[i]][0]
    return pdb[indes_b + 1: indes_e]
    
def get_source_blades(pdb_path):
    """Returns a dictionary of [blade#] = source_pdb_code"""
    comments = get_comments(pdb_path)
    return {comment.split()[0].replace('segment_', ''): comment.split()[1]
            for comment in comments}
    
def get_blades_names(xml_path):
    """Returns an ordered list of the blades"""
    xml = open(xml_path, 'r').readlines()
    segments_lines = [i for i in range(len(xml)) if 'Segments' in xml[i]]
    return [blade.split()[0].replace('<', '') 
            for blade in xml[segments_lines[0] + 1: segments_lines[1]]]   
                   
def get_file(dir, name):
    """Returns the path of the first file that contains name"""
    file = [file for file in os.listdir(dir) if name in file][0]
    return '/'.join([dir, file])
                   
def pssms_locations(pdb_path, xml_path, pssms):
    """Returns an ordered list of the pssm of each frame and blade"""
    blades = get_blades_names(xml_path)
    sources = get_source_blades(pdb_path)
    if len(pssms) != len(blades) or len(pssms) != len(sources):
        raise Exception('mismatch in blade number') 
        
    locations = []
    for i in range(len(pssms)):
        if os.path.isfile(pssms[i]):
            locations.append(pssms[i])
        else:
            source = sources[blades[i]]
            path = get_file(pssms[i], source)
            locations.append(path)
    return locations

def create_chimera_pssm(pdb_path, xml_path, pssms):
    locations =  pssms_locations(pdb_path, xml_path, pssms)
    name = os.path.basename(pdb_path)[:-4] + '.pssm'
    final_pssm = open(name, 'a')
    for location in locations:
        clean_pssm = extract_pssm_lines(location)
        final_pssm.writelines(clean_pssm)
        
    final_pssm.close()
    
def main():
    args = parse_args()
    create_chimera_pssm(args.pdb, args.xml, args.pssms)   

    
if __name__ == '__main__':
    main()
