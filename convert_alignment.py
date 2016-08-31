"""converts alignment file formats"""

import sys
import argparse
import MSA

def parse_args():
    desc = "converts between different alignment formats"
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('alignment_file', help = 'path to MSA file')
    parser.add_argument('from_format', help = 'starting format')
    parser.add_argument('to_format', help = 'wanted end format')
    args = parser.parse_args()
    return args

def main():
    """"""
    args = parse_args()
    MSA.convert_format(args.alignment_file, args.from_format, args.to_format)
    

if __name__ == "__main__":
    main()
