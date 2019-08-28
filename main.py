#!/bin/env/python

'''
main program of g3d
combine predicted 3d structure files to 1 binary file
significance:
    * one file for whole genome make storage easier
    * remote and range access
    * structure data are compressed to save space
'''

import sys, binascii, codecs

def main():
    files = ['test/chr1.pdb','test/chr2.pdb']
    magic = '8G3D4515'
    genome = 'hg19'
    sample = 'GM12878'
    resolution = ''
    version = 1
    with open('gm.g3d', 'wb') as fout:
        # fout.write(binascii.hexlify(magic.encode()))
        # fout.write(binascii.hexlify(genome.encode()))
        # fout.write(binascii.hexlify(sample.encode()))
        for f in files:
            with open(f, 'rU') as fin:
                content = fin.read()
                encoded = codecs.encode(content.encode(), 'hex_codec')
                print(type(encoded))
                bcontent = bytearray.fromhex(str(encoded))
                # bcontent = binascii.unhexlify(encoded)
                # binarray = ' '.join(format(ch, 'b') for ch in bytearray(fin.read()))
                fout.write(bcontent)
    return 0

if __name__ == '__main__':
    main()
