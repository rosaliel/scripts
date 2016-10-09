import sys
import argparse
def parse_args():
    """"""
    desc = 'prints all structures having a blade from the original template'
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('template_to_search', 
                        help = 'pattern to search for the trmplate')
    parser.add_argument('designs', 
                        help = 'list of designs pdb',
			nargs = '+',
			action = 'store')
    return parser.parse_args()

def main():
    args = parse_args()    
    print 'template', args.template_to_search
    for i in args.designs:
        file = open(i)
        lines = [line[-6:-2] for line in file if line.startswith('segment') and
	                                         'frm' not in line]
        flag = True
        for j in lines:
            if j.startswith(args.template_to_search):
    	        flag = False
        if not flag:
            print i, '\n'

if __name__ == '__main__':
    main()
