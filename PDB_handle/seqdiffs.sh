#!/bin/sh
#output the sequence differences between two pdb files
#structures must be aligned
#USAGE: seqdiffs.sh <PDB native> <PDB design>

pdb1=$1
pdb2=$2

awk '$1=="ATOM" && $3=="CA"{print $4,substr($0,23,5)+0}' $pdb1 > seq1.TMP
awk '$1=="ATOM" && $3=="CA"{print $4,substr($0,23,5)+0}' $pdb2 > seq2.TMP

echo "lengths of chains 1, 2: " `wc seq1.TMP | awk '{print $1}'`"," ` wc seq2.TMP | awk '{print $1}'`

paste seq1.TMP seq2.TMP | awk '$1!=$3{print $1 $2 $3}'
echo -n pymol command: select mutations, resi " "
paste seq1.TMP seq2.TMP	| awk '$1!=$3{printf $2"+"}'
mutations=`paste seq1.TMP seq2.TMP | awk '$1!=$3' | wc | awk '{print $1}'`
echo
echo "mutations: "$mutations
rm -f seq1.TMP seq2.TMP
