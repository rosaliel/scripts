from pymol import cmd
from pprint import pprint as pp

def main(design_path, original_pdbs_directory = 'pdb'):
    """loads to the pymol session the original blades of the design.
    Args:
        design_path: path to the wanted design
	original_pdbs_directory: path to directory where all  pdbs are 
    """
    segment_count = 0
    for line in open(design_path):
        if line.startswith('segment_') and 'frm' not in line:
	    segment_count += 1
	    original = line.split()[-1]
	    name = '{}_{}'.format(segment_count, original)
	    print name
	    cmd.load('{}/{}.pdb'.format(original_pdbs_directory, original))
	    cmd.set_name(original, name)
	   
cmd.extend("show_org", main) 
