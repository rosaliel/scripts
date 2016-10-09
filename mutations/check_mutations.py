import sys
import os
import argparse
import rosetta_job
def parse_args():
    """"""
    desc = 'creates jobs for a list of mutations'
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('pdb', help='pdb to mutate')
    parser.add_argument(
           'mutations', 
            help='list of mutations in format, e.g. 215A LEU (A is the chain)')
    parser.add_argument('template', help='path to template pdb')
    parser.add_argument('chelating_residues', 
	                 help='path to file with comma-separated residue list')
    return parser.parse_args()

	
def prepare_single_mutation(general_path, pose, id, source, template, chel_res):
    """prepares files to run a signle mutation"""
    name = '{}_{}'.format(pose, id)
    job_args = ['@flags']
    job_args.append('-parser:script_vars place="{}"'.format(pose))
    job_args.append('-parser:script_vars new_res="{}"'.format(id))
    job_args.append('-parser:script_vars template="{}"'.format(template))
    job_args.append('-parser:script_vars chel_res="{}"'.format(chel_res))
    job_args.append('-s ' + source)
    job_args.append('-out:prefix "{}_"'.format(name))
    rosetta_job.create_job(name=name, path=general_path, args=job_args)
def main():
    args = parse_args()
    path = os.getcwd() 
    source = os.path.abspath(args.pdb)
    template = os.path.abspath(args.template)
    chel_res = open(args.chelating_residues, 'r').read().strip()
    f = open(args.mutations, 'r')
    for mutation in f:
        pose, id = mutation.split()
	prepare_single_mutation(path, pose, id, source, template, chel_res)      
        
	
if __name__ == '__main__':
    main()
