#!/bin/env/python

'''
main program of g3d
combine predicted 3d structure files to 1 binary file
significance:
    * one file for whole genome make storage easier
    * remote and range access
    * structure data are compressed to save space
'''

import pickle, os

# fixed header size 1000 bytes
HEADER_LENGTH = 1000

def structureFilesToG3dFile():
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
                pkldata = pickle.dumps(fin.read())
                size = len(pkldata)
                fn = os.path.basename(f)
                offsets[fn] = {'offset': offset, 'size': size}
                fout.write(pkldata)
                offset += size
        meta = {
            'magic': magic,
            'version': version,
            'genome': genome,
            'sample': sample,
            'offsets': offsets
        }
        fout.seek(0)
        metapkl = pickle.dumps(meta)
        metapklLen = len(metapkl)
        for i in range(0, metapklLen):
            header[i] = metapkl[i]
        fout.write(header)


def readHeader(fh):
    headerpkl = fh.read(HEADER_LENGTH)
    return pickle.loads(headerpkl)

def G3dFileToStructureFiles(g3dFileName):
    '''convert g3d to many text stucture files.'''
    with open(g3dFileName, 'rb') as fin:
        header = readHeader(fin)
        offsets = header['offsets']
        for fn in offsets:
            fileName = fn
            fileOffset = offsets[fn]['offset']
            fileSize = offsets[fn]['size']
            fin.seek(fileOffset)
            filepkl = fin.read(fileSize)
            with open('testOut/'+fileName, 'w') as fout:
                fout.write(pickle.loads(filepkl))

def G3dFileQueryStucture(g3dFileName, fn):
    '''query a stucture from a g3f file.'''
    with open(g3dFileName, 'rb') as fin:
        header = readHeader(fin)
        offsets = header['offsets']
        if fn not in offsets:
            print('error: %s not exits in %s', fn, g3dFileName)
        else:
            fileName = fn
            fileOffset = offsets[fn]['offset']
            fileSize = offsets[fn]['size']
            fin.seek(fileOffset)
            filepkl = fin.read(fileSize)
            print(pickle.loads(filepkl))

if __name__ == '__main__':
    # structureFilesToG3dFile()
    # G3dFileToStructureFiles('gm.g3d')
    G3dFileQueryStucture('gm.g3d','chr2.pdb')