#!/bin/sh
#Written by Gideon Lapidoth glapidoth@gmail.com


# 1. removes all non resideu lines but leaves metals and modified AA's if present
# 2. removes multiple rotamers
# 3. renumbers the PDB
for var in "$@"
do
	grep "^ATOM\|^HETATM.*ALA\|^HETATM.*ARG\|^HETATM.*ASN\|^HETATM.*ASP\|^HETATM.*CSH\|^HETATM.*CYS\|^HETATM.*GLN\|^HETATM.*GLU\|^HETATM.*GLY\|^HETATM.*HIS\|^HETATM.*ILE\|^HETATM.*LEU\|^HETATM.*LYS\|^HETATM.*MET\|^HETATM.*MSE\|^HETATM.*ORN\|^HETATM.*PHE\|^HETATM.*PRO\|^HETATM.*SER\|^HETATM.*THR\|^HETATM.*TRP\|^HETATM.*TYR\|^HETATM.*VAL\|^HETATM.*ACE\|^HETATM.*FOR\|^HETATM.*ABA\|^HETATM.*BOC\|^HETATM.*BMT\|^HETATM.*SAR\|^HETATM.*MLE\|^HETATM.*MVA\|^HETATM.*IVA\|^HETATM.*DFO\|^HETATM.*NME\|^HETATM.*AHT\|^HETATM.*PTR\|^HETATM.*PCA\|^HETATM.*HYP\|^HETATM.*INI\|^HETATM.*NLE\|^HETATM.*TYS\|^HETATM.*CGU\|^HETATM.*STA\|^HETATM.*ILG\|^HETATM.*OCS\|^HETATM.*KCX\|^HETATM.*SAH\|^HETATM.*SAM\|^HETATM.*SEP\|^HETATM.*LLP\|^HETATM.*5HP\|^HETATM.*CSO\|^HETATM.*ETA\|^HETATM.*TFA\|^HETATM.*ANI\|^HETATM.*MPR\|^HETATM.*DAM\|^HETATM.*ACB\|^HETATM.*ADD\|^HETATM.*CXM\|^HETATM.*DIP\|^HETATM.*BAL\|AL  \|^HETATM.*AS \|^HETATM.*BA\|^HETATM.*BR\|^HETATM.*CA  \|^HETATM.*CD\|^HETATM.*CL\|^HETATM.*CO \|^HETATM.*CS\|^HETATM.*CU\|^HETATM.*FE\|^HETATM.*HG\|^HETATM.*KR\|^HETATM.*LA\|^HETATM.*LI\|^HETATM.*MG\|^HETATM.*MN\|^HETATM.*NA\|^HETATM.*NI\|^HETATM.*PB\|^HETATM.*PR\|^HETATM.*PT\|^HETATM.*SE\|^HETATM.*SM\|^HETATM.*ZN" $var |grep -v [B-D][A-Z][A-Z][A-Z] |grep -v "SEQRES\|REMARK\|HELIX\|SHEET\|TITLE\|JRNL\|SITE\|LINK" |grep -v "HETATM.*CX.*KCX\|HETATM.*OQ1.*KCX\|HETATM.*OQ2.*KCX" >tmp

	cat tmp |sed -e "s/\(HETATM\)\(.*\)\(KCX\)/ATOM  \2LYS/g" >tmp1 #replace KCX with LYS
	cat tmp1 |sed -e "s/\(HETATM\)\(.*\)\(MSE\)/ATOM  \2MET/g" >tmp #replace MSE with MET
	cat tmp |sed -e "s/\(ATOM   .*\)SE \(  MET\)/\1 SD\2/g" >tmp1 #replace SE ATOM with SD in MET
	grep "^ATOM\|^HETATM" tmp1 >  tmp #remove any non atmo lines
	grep -v "^HETATM" tmp >  tmp1 #remove any non atmo lines
	mv tmp1 tmp


	awk 'BEGIN {num=0}
		{
		if( $var=="ATOM" || $var=="HETATM" ){
			if( substr($0,14,3)=="N  " || substr($0,13,1)!=" ") ++num;
			printf substr( $0, 1, 22 );
			printf "%4d ",num
			print substr( $0,28,10000);
		}
		else print $0
		}' tmp > tmp1


	
		mv tmp1 `basename $var`
	rm tmp
done

#list of modified aa's taken from: http://www.ccp4.ac.uk/html/refmac5/dictionary/list-of-ligands.html

