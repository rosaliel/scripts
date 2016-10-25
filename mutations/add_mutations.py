import sys
import os
import argparse
import rosetta_job
import shutil

MOVER = 'MutateResidue'
TARGET = '%%place%%'
NEW_RES = '%%new_res%%'

def parse_args():
    """"""
    desc = 'creates the files to run multiple mutations on a pose'
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('pdb', help='pdb to mutate')
    parser.add_argument(
           'mutations', 
            help='list of mutations in format, e.g. 215A LEU (A is the chain)')
    parser.add_argument('template', help='path to template pdb')
    parser.add_argument('chelating_residues', 
	                 help='path to file with comma-separated residue list')
    return parser.parse_args()

def _parse_mutations(path):
    """reads the list of mutations file and returns it as a list of tuples"""
    f = open(path, 'r')
    mutations = [(mut.split()[0], mut.split()[1]) for mut in f]
    return mutations

def _read_mutate_xml(path):
    """returns the xml and the line the mutation mover is in"""
    f = open(path, 'r').readlines()
    mover_line = -1
    for i in range(0, len(f)):
        if MOVER in f[i]:
            return (f, i)
            
def _create_new_xml(path_to_xml, mutations):
    """"""
    xml, mut_line_i = _read_mutate_xml(path_to_xml)
    final_xml = xml[:mut_line_i]
    mut_line = xml[mut_line_i]
    final_xml += [mut_line.replace('%%place%%', pose).replace('%%new_res%%', id)
                  for pose, id in mutations]
    final_xml += xml[mut_line_i + 1 :]
    return final_xml
             
def main():
    # parse input 
    args = parse_args()
    path = os.getcwd() 
    source = os.path.abspath(args.pdb)
    template = os.path.abspath(args.template)
    chel_res = open(args.chelating_residues, 'r').read().strip()
    mutations = _parse_mutations(args.mutations)
    
    # create new xml
    dir_path = os.path.dirname(os.path.realpath(__file__)) # path of script file
    xml = _create_new_xml(dir_path + '/mutate.xml', mutations)
    open(path + '/mutate.xml', 'w').writelines(xml)
    
    # create files to run Rosetta
    shutil.copy(dir_path + '/flags', path)
    job_name = 'insert_mut'
    job_args = ['@flags']
    job_args.append('-parser:script_vars template="{}"'.format(template))
    job_args.append('-parser:script_vars chel_res="{}"'.format(chel_res))
    job_args.append('-s ' + source)
    rosetta_job.create_job(name=job_name, path=path, args=job_args)
    os.system(path + '/command')
            
if __name__ == '__main__':
    main()
