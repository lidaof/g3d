#!/bin/env/python

'''
main program of g3d
combine predicted 3d structure files to 1 binary file
significance:
    * one file for whole genome make storage easier
    * remote and range access
    * structure data are compressed to save space
'''

import random
import pickle

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

def test():
    uncompressed_dic = {'a': 1, 'b': (2, 3, 4), 'c': 'text'}  # Sample data.

    with open('UCIndex.txt', 'wb') as f:
        UncompressedLookup = {}
        offset = 0

        for key, value in uncompressed_dic.items():
            pkldata = pickle.dumps(value)
            size = len(pkldata)
            UncompressedLookup[key] = {'offset': offset, 'size': size}
            f.write(pkldata)
            offset += size


    # Read items back in random order using UncompressedLookup dict.
    keys = list(uncompressed_dic.keys())
    random.shuffle(keys)

    i = 0
    while keys:
        if i >= 5:
            break
        key = keys.pop()
        offset = UncompressedLookup[key]['offset']
        size = UncompressedLookup[key]['size']
        with open('UCIndex.txt', 'rb') as f:
            f.seek(offset)
            pkldata = f.read(size)
            value = pickle.loads(pkldata)
        print((key, value))

if __name__ == '__main__':
    test()
