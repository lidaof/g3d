#!/bin/env/python

'''
main program of g3d
combine predicted 3d structure files to 1 binary file
significance:
    * one file for whole genome make storage easier
    * remote and range access
    * structure data are compressed to save space
'''

import sys, struct

def main():
    files = ['test/chr1.pdb','test/chr2.pdb']
    magic = '8G3D2019'
    genome = 'hg19'
    sample = 'GM12878'
    resolution = ''
    version = 1
    with open('test.g3d', 'wb') as fout:
        fout.write(magic.encode('utf8'))
        fout.write(genome.encode('utf8'))
        fout.write(sample.encode('utf8'))
        for f in files:
            with open(f, 'rU') as fin:
                fout.write(fin.read().encode('utf8'))            
    return 0

if __name__ == '__main__':
    main()
