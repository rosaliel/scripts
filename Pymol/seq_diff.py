from pymol import cmd
from pprint import pprint as pp
#import alignment

def get_alignment( mobile, target, cutoff=2):
    """alignes mobile to target (both are loaded protein's names).
    returns the alignment object - list of lists of pairs of tuples:
    [(prot_a, index), (prot_b, index)]
    """
    cmd.select('ca_mobile', '{} and name CA'.format(mobile))
    cmd.select('ca_target', '{} and name CA'.format(target))
    aln_object = 'aln_{}_{}'.format(mobile, target)
    cmd.align(mobile, target, cutoff=cutoff, object=aln_object)
    raw_aln = cmd.get_raw_alignment(aln_object)
    return raw_aln 
 
def index2resi(prot):
    """returns a dictionary of [index] = resi"""
    res = {'res_i': dict()}
    cmd.iterate(prot, 'res_i[index] = resv', space = res)
    return res['res_i']  

def atom_aln2resi_aln(raw_aln, target_ind = 1):
    """converts a raw_aln (parsed alignment object) to a dictionary mapping 
    aligned residues between the target and the mobile protein.
    Args:
    target index - 0 if target's atoms are the first tuple of every list in 
               raw_aln, else 1
    returns a dictionary [ target residue ] = mobile residue
    """
    target_resi = index2resi(prot = raw_aln[0][target_ind][0])
    mobile_resi = index2resi(prot = raw_aln[0][1 ^ target_ind][0])
    resi_pairs = dict()
    for i in raw_aln:
        # X_r is the index's residue in X in the current position in raw_aln
        target_r = target_resi[i[target_ind][1]]
        mobile_r = mobile_resi[i[1 ^ target_ind][1]]
        if ((target_r in resi_pairs.keys()) 
               and (mobile_r != resi_pairs[target_r])):
            print 'conflict: target={:5<} mobile1={:5<} mobile2={:5<}'.format(
                  target_r, 
              resi_pairs[target_r], 
              mobile_r)
        else:
            resi_pairs[target_r] = mobile_r
    return resi_pairs
    
def get_resi_resn(prot):
    """returns a list of (resi, resn) of prot
    """    
    res = {'res_name': list()}
    cmd.iterate(prot, 'res_name.append((resi, resn))', space = res)
    return sorted(list(set(res['res_name'])), key = lambda res: int(res[0]))
    
def get_resi_resn_dict(prot):
    """returns a dictionary of [resi] = resn of prot
    """    
    res = {'res_name': dict()}
    cmd.iterate(prot, 'res_name[resi] = resn', space = res)
    return res['res_name']

def create_selection(name, selection, color='purple'):
    """"""
    cmd.select(name, selection)
    cmd.show('stick', selection)
    cmd.color(color, selection)
    
def seq_diff_alignment(prot1, prot2, cutoff=5):
    """creates selection groups of different residues (mutations) between 2 
    structures, only for aligned positions!! (good for splice output)
    """
    aln = get_alignment(prot1, prot2, cutoff)
    # alignment object doesn't keep sending order
    index_prot2 = 0 if aln[0][0][0] == prot2 else 1 
    aligned_res = atom_aln2resi_aln(aln, index_prot2)
    
    prot1_resn_dict = get_resi_resn_dict(prot1)
    prot2_resn_dict = get_resi_resn_dict(prot2)
    diff_prot1 = ''
    diff_prot2 = ''
    for prot2_resi in aligned_res.keys():
        prot1_resi = aligned_res[prot2_resi] 
        prot1_resn = prot1_resn_dict[str(prot1_resi)]        
        prot2_resn = prot2_resn_dict[str(prot2_resi)]
        if prot1_resn != prot2_resn:
            diff_prot1 += str(prot1_resi) + '+'       
            diff_prot2 += str(prot2_resi) + '+'
    
    sele_prot1 = 'mutations_' + prot1
    sele_prot2 = 'mutations_' + prot2
    create_selection(sele_prot1, 'resi {} and {}'.format(diff_prot1, prot1))
    create_selection(sele_prot2, 'resi {} and {}'.format(diff_prot2, prot2))
    cmd.disable('aln*')
    cmd.delete('ca* ')   

def seq_diff(prot1, prot2):
    """creates selection groups of different residues (mutations) between 2 
    structures.
    """ 
    prot1_resn = get_resi_resn(prot1)
    prot2_resn = get_resi_resn(prot2)    
    diff1 = '0+'
    diff2 = '0+'
    length = (len(prot1_resn) if len(prot1_resn) < len(prot2_resn) 
                else len(prot2_resn))
    for i in range(0, length):
        resi1, resn1 =  prot1_resn[i]
        resi2, resn2 =  prot2_resn[i]
        if resn1 != resn2:
	    print 'in if'
            diff1 += str(resi1 + '+')
            diff2 += str(resi2 + '+')
    create_selection('mutations_{}_{}'.format(prot1, prot2), 
                     'resi {} and {}'.format(diff1, prot1),
                     'wheat')
    create_selection('mutations_{}_{}'.format(prot2, prot1), 
                     'resi {} and {}'.format(diff2, prot2),
                     'marine')        

cmd.extend("seq_diff_aln", seq_diff_alignment) 
cmd.extend("seq_diff", seq_diff) 
