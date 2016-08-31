#!/usr/bin/python
import os
from os.path import basename
import csv

#This script allows me after choosing positions on two objcets to do pairwise alignmnet between them on a click
def pair_wise():
	#spli selection into two objects
	objects=cmd.get_object_list("sele")
	cmd.select("object_one","sele and %s and name CA+O+N+C"%objects[0])
	cmd.select("object_two","sele and %s and name CA+O+N+C"%objects[1])
	rms=cmd.pair_fit("object_two","object_one")
	cmd.show("sticks","object_one and name C+CA+O+N")
	cmd.show("sticks","object_two and name C+CA+O+N")	
	cmd.orient("object_one",animate=-1)
	cmd.scene('message', 'store', "rms value is: "+str(rms))
	cmd.scene("message","recall")
	return  
	
def pair_wise_atoms():
	#spli selection into two objects
	objects=cmd.get_object_list("sele")
	cmd.select("object_one","sele and %s"%objects[0])
	cmd.select("object_two","sele and %s"%objects[1])
	rms=cmd.pair_fit("object_two","object_one")
	#cmd.show("sticks","object_one and name C+CA+O+N")
	#cmd.show("sticks","object_two and name C+CA+O+N")	
	cmd.orient("object_one",animate=-1)
	cmd.scene('message', 'store', "rms value is: "+str(rms))
	cmd.scene("message","recall")
	return  	
cmd.set_key( 'CTRL-P' ,pair_wise)
cmd.set_key( 'CTRL-Q' ,pair_wise_atoms)



