import sys
import os
import argparse
import rosetta_job
import shutil
import glob
from numpy import mean
baseline_name = 'baseline'
to_compare = 'to_compare'

def parse_args():
    """"""
    desc = ('Creates a summary file describing the energy for each mutation.\n'
            'You should compare the mutation\'s energy with the energy in line'
            '"to_compare".\nPlease use the structure pdb/_baseline__.pdb to '
            'insert your final mutations.')            
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
    Returns the path to the baseline file 
    """
    jobs = list()
    for i in range(1,6):
        name = 'baseline_' + str(i)
        job_args = ['@flags_baseline']
        job_args.append('-parser:script_vars template="{}"'.format(template))
        job_args.append('-parser:script_vars chel_res="{}"'.format(chel_res))
        job_args.append('-s ' + source)
        job_args.append('-out:prefix "{}_"'.format(name))
        rosetta_job.create_job(name=name, path=path, args=job_args) 
        jobs.append(name)        

    os.system(path + '/command')
    rosetta_job.wait_jobs(path, jobs)
    
    # parse baseline's output
    energies = _get_energies(path)
    best_baseline = energies.keys()[0]
    for pdb in energies:
        if pdb == best_baseline:
            continue
        elif energies[pdb] < energies[best_baseline]:
            os.remove('{}/pdb/{}.pdb'.format(path, best_baseline))
            best_baseline = pdb
        else:
            os.remove('{}/pdb/{}.pdb'.format(path, pdb))

    # besaline_name = [pdb for pdb in glob.glob(path + '/pdb/*pdb')
                     # if 'baseline' in pdb][0]    
    # os.rename(besaline_name, path + '/pdb/baseline.pdb')
    os.rename('{}/pdb/{}.pdb'.format(path, best_baseline), 
              path + '/pdb/_{}__.pdb'.format(baseline_name))
    os.remove(path + '/command')
    return path + '/pdb/_{}__.pdb'.format(baseline_name)
 
# parsing results
def _check_structure_energy(path):
    """Looks for the `pose` line and returns the last energy.
    Arguments:
    path -- path to the pdb file
    """
    f = open(path, 'r').readlines()
    for line in f:
        if line.startswith('pose'):
            return float(line.split()[-1])
    
def _get_energies(path):
    """Parses energies of the output pdbs
    Arguments:
    path -- path to directory with err/ out/ job/ ect.
    Returns dictionary of [mutation name] = energy
    """
    energies = dict()
    for pdb in glob.glob(path + '/pdb/*pdb'):
        energy = _check_structure_energy(pdb)
        name =  os.path.basename(pdb)[:-4] 
        energies[name] = energy
    return energies  

def parse_output(path):
    """
    Creates a summary file with the best energy for every mutation
    Arguments:
    path -- general path to where out/ pdb/ err etc. are
    """
    energies = _get_energies(path)
    
    # energy_to_compare = mean([energies[i] 
                              # for i in energies.keys() 
                              # if to_compare in i])
    # print energies
    # energies = {k: v for k, v in energies if to_compare not in k}
    # print energies
    
    
    
    best_energies = dict()
    for mut in energies.keys():
        number = mut[: mut.find('_')]
        name = mut[mut.find('_') + 1: mut.find('__')]
        if name not in best_energies.keys():
            best_energies[name] = energies[mut]
        else:
            best_energies[name] = min(energies[mut], best_energies[name])
    
    summary = open(path + '/summary', 'w')
    summary.writelines(['{:<30}{}\n'.format(mut, best_energies[mut]) 
                       for mut in sorted(best_energies.keys())])    
      
# main functions running this script   
def check_mutations(path, source, template, chel_res, mutations_path):
    """Main function for running from a different module
    Arguments:
    path -- where to run the jobs and create all files
    template -- path to template structure
    chel_res -- a string of the chelating residues, comma separated
    mutations_path -- path to mutations file
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) # path of script file
    shutil.copy(dir_path + '/flags', path)
    shutil.copy(dir_path + '/flags_baseline', path)
    shutil.copy(dir_path + '/mutate.xml', path)
    # shutil.copy(dir_path + '/relax_baseline.xml', path)
    shutil.copy(dir_path + '/relax_baseline.xml', path)
    
    source = create_baseline(path, source, template, chel_res)
    print 'done baseline'
    
    # add a null mutation 
    res_name, chain, seq_number = find_first_res(source)
    mutations = _parse_mutations(mutations_path)
    mutations.append((seq_number + chain, res_name))

    # running the script 5 times and kipping the lowest energy for each mutation
    jobs = list()
    for i in range(1,6):
        for pose, id in mutations:
            if (pose == seq_number + chain) and (id == res_name): # null mut
                name = str(i) + '_to_compare'
            else:
                name = '{}_{}_{}'.format(i, pose, id)
            job_args = ['@flags']
            job_args.append('-parser:script_vars place="{}"'.format(pose))
            job_args.append('-parser:script_vars new_res="{}"'.format(id))
            job_args.append('-parser:script_vars template="{}"'.format(
                                                                      template))
            job_args.append('-parser:script_vars chel_res="{}"'.format(
                                                                      chel_res))
            job_args.append('-s ' + source)
            job_args.append('-out:prefix "{}__"'.format(name))
            rosetta_job.create_job(name=name, path=path, args=job_args)
            jobs.append(name)

    os.system(path + '/command')
    rosetta_job.wait_jobs(path, jobs)
        
    parse_output(path)
    
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
