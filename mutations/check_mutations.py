import sys
import os
import argparse
import rosetta_job
import shutil
import glob

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

def _parse_mutations(path):
    """reads the list of mutations file and returns it as a list of tuples"""
    f = open(path, 'r')
    mutations = [(mut.split()[0], mut.split()[1]) for mut in f]
    return mutations
	
def prepare_single_mutation(general_path, pose, id, source, template, chel_res):
    """prepares files to run a signle mutation"""
    name = '{}_{}'.format(pose, id)
    # job_args = ['@flags']
    job_args = ['@flags']
    job_args.append('-parser:script_vars place="{}"'.format(pose))
    job_args.append('-parser:script_vars new_res="{}"'.format(id))
    job_args.append('-parser:script_vars template="{}"'.format(template))
    job_args.append('-parser:script_vars chel_res="{}"'.format(chel_res))
    job_args.append('-s ' + source)
    job_args.append('-out:prefix "{}_"'.format(name))
    rosetta_job.create_job(name=name, path=general_path, args=job_args)
    return name

def _check_structure_energy(path):
    """Looks for the `pose` line and returns the last energy.
    Args:
    path -- path to the pdb file
    """
    f = open(path, 'r').readlines()
    for line in f:
        if line.startswith('pose'):
            return float(line.split()[-1])
    
def _parse_results(path):
    """Parses energies of the output pdbs
    Args:
    path -- path to directory with err/ out/ job/ ect.
    Returns dictionary of [mutation name] = energy
    """
    energies = dict()
    for pdb in glob.glob(path + '/pdb/*pdb'):
        energy = _check_structure_energy(pdb)
        name =  os.path.basename(pdb)[:-4] 
        energies[name] = energy
    return energies  
    
# Functions for creating the baseline

def find_first_res(source):
    """Finds first residue of the pdb"""
    first_ATOM_line = filter(lambda x: x.startswith('ATOM'), 
                             open(source, 'r').readlines())[0]
    res_name = first_ATOM_line[17:20]
    chain = first_ATOM_line[21]
    seq_number = first_ATOM_line[22:26].strip()
    return (res_name, chain, seq_number)
    
def create_baseline(path, source, template, chel_res):
    """
    Returns the path to the baseline file and the null mutation it used
    """
    # res_name, chain, seq_number = find_first_res(source)
    name = 'baseline'
    job_args = ['@flags_baseline']
    job_args.append('-parser:script_vars template="{}"'.format(template))
    job_args.append('-parser:script_vars chel_res="{}"'.format(chel_res))
    job_args.append('-s ' + source)
    job_args.append('-out:prefix "{}_"'.format(name))
    rosetta_job.create_job(name=name, path=path, args=job_args)    

    os.system(path + '/command')
    rosetta_job.wait_jobs(path, [name])
    besaline_name = [pdb for pdb in glob.glob(path + '/pdb/*pdb')
                     if 'baseline' in pdb][0]    
    os.rename(besaline_name, path + '/pdb/baseline.pdb')
    os.remove(path + '/command')
    return path + '/pdb/baseline.pdb'
    
# main functions running this script   
def check_mutations(path, source, template, chel_res, mutations_path):
    """Main function for running from a different module
    Args:
    path -- where to run the jobs and create all files
    template -- path to template structure
    chel_res -- a string of the chelating residues, comma separated
    mutations_path -- path to mutations file
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) # path of script file
    shutil.copy(dir_path + '/flags', path)
    shutil.copy(dir_path + '/flags_baseline', path)
    shutil.copy(dir_path + '/mutate.xml', path)
    shutil.copy(dir_path + '/relax_baseline.xml', path)
    
    source = create_baseline(path, source, template, chel_res)
    print 'done baseline'
    
    # adds a null mutation 
    res_name, chain, seq_number = find_first_res(source)
    open(mutations_path, 'a').write('{}{} {}\n'.format(seq_number, chain, 
                                                       res_name))
    mutations = _parse_mutations(mutations_path)
    
    jobs = list()
    for pose, id in mutations:
        jobs.append(prepare_single_mutation(path, pose, id, 
                                            source, template, chel_res))
    os.system(path + '/command')
    rosetta_job.wait_jobs(path, jobs)
    
    results = _parse_results(path)
    summary = open(path + '/summary', 'w')
    summary.writelines(['{:<30}{}\n'.format(name, results[name]) 
                       for name in results.keys()])
    
    
def main():
    args = parse_args()
    path = os.getcwd() 
    source = os.path.abspath(args.pdb)
    template = os.path.abspath(args.template)
    chel_res = open(args.chelating_residues, 'r').read().strip()
    mutations_path = args.mutations
    check_mutations(path, source, template, chel_res, mutations_path)

if __name__ == '__main__':
    main()
