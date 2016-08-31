### use: pymol -c <path to pdbs *.pdb> <path to this script
### change at the alignto line the path to the source structure

alignto 3w24_relax
for i in cmd.get_object_list("all"): cmd.save(i+".pdb",i)
