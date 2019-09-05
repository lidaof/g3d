#!/bin/env/python

'''
main program of g3d
combine predicted 3d structure files to 1 binary file
significance:
    * support any format
    * one file for whole genome make storage easier
    * remote and range access
    * structure data are compressed to save space
'''

import sys
import os
import pickle
import zlib
import json

# FIXED header size 64000 bytes
HEADER_LENGTH = 64000

def structure_files_to_g3d_file():
    '''convert many text stucture files to g3d format'''
    files = ['test/chr1.pdb','test/chr2.pdb']
    magic = 'G3D'
    genome = 'hg19'
    sample = 'GM12878'
    # resolution = ''
    version = 1
    header = bytearray(HEADER_LENGTH)
    offset = HEADER_LENGTH
    with open('gm.g3d', 'wb') as fout:
        fout.seek(HEADER_LENGTH)
        offsets = {}
        for f in files:
            with open(f, 'rU') as fin:
                pkldata = pickle.dumps(fin.read(), protocol=3)
                compressed = zlib.compress(pkldata)
                size = len(compressed)
                fn = os.path.basename(f)
                offsets[fn] = {'offset': offset, 'size': size}
                fout.write(compressed)
                offset += size
        meta = {
            'magic': magic,
            'version': version,
            'genome': genome,
            'sample': sample,
            'offsets': offsets
        }
        fout.seek(0)
        meta_pkl = pickle.dumps(meta, protocol=3)
        meta_pkl_len = len(meta_pkl)
        for i in range(0, meta_pkl_len):
            header[i] = meta_pkl[i]
        fout.write(header)


def read_header(fh):
    '''return the header of a g3d file'''
    header_pkl = fh.read(HEADER_LENGTH)
    return pickle.loads(header_pkl)

def g3d_file_to_structure_files(g3d_filename):
    '''convert g3d to many text stucture files.'''
    with open(g3d_filename, 'rb') as fin:
        header = read_header(fin)
        offsets = header['offsets']
        for fn in offsets:
            file_name = fn
            file_offset = offsets[fn]['offset']
            file_size = offsets[fn]['size']
            fin.seek(file_offset)
            file_pkl = fin.read(file_size)
            with open('testOut/'+file_name, 'w') as fout:
                fout.write(pickle.loads(zlib.decompress(file_pkl)))

def g3d_file_query_stucture(g3d_filename, fn):
    '''query a stucture from a g3f file.'''
    with open(g3d_filename, 'rb') as fin:
        header = read_header(fin)
        offsets = header['offsets']
        if fn not in offsets:
            print('error: %s not exits in %s', fn, g3d_filename)
        else:
            file_offset = offsets[fn]['offset']
            file_size = offsets[fn]['size']
            fin.seek(file_offset)
            file_pkl = fin.read(file_size)
            print(pickle.loads(zlib.decompress(file_pkl)))

def get_meta(g3d_filename):
    '''convert g3d to many text stucture files.'''
    with open(g3d_filename, 'rb') as fin:
        header = read_header(fin)
    json.dump(header, sys.stdout, indent=4)
    print()

if __name__ == '__main__':
    structure_files_to_g3d_file()
    g3d_file_to_structure_files('gm.g3d')
    g3d_file_query_stucture('gm.g3d','chr2.pdb')
    get_meta('gm.g3d')
