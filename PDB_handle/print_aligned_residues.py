#!/usr/bin/env python
from pymol_ import alignment
import sys

NAME = ('/home/labs/fleishman/rosaliel/tools/scripts/PDB_handle/print_aligned_'
        'residues.py')

def parse_args():
    """"""
    if len(sys.argv) < 3:
        raise Exception(('use: pymol -cq %s -- <path to template> <path to ' 
                          'structure> <comma separated list of residues in '
                          'template' % NAME))
    args = dict()
    args['template'] = sys.argv[1]
    args['mobile'] = sys.argv[2]
    args['res'] = ''.join(sys.argv[3:]).split(',')
    return args

def main():
    args = parse_args()
    
    template_name = os.path.basename(args['template'])[:-4]   
    mobile_name = os.path.basename(args['mobile'])[:-4]

    cmd.load(args['template'])
    cmd.load(args['mobile'])
    
    raw_alignment = alignment.get_alignment(mobile_name, template_name)
    target_index = 0 if raw_alignment[0][0][0] == template_name else 1
    # print 'target_index', target_index
    # print 'raw_alignment[0][target_index][0]', raw_alignment[0][target_index][0]
    residues_aln = alignment.atom_aln2resi_aln(raw_alignment, target_index)
    # print residues_aln
    print reduce(lambda x, y: x + ', ' + y,
                 [str(residues_aln[int(res)]) for res in args['res']])
    
main()
