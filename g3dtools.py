#!/bin/env/python
"""
Main program of g3dtools.
* combine predicted 3d structure files to 1 binary file
significance:
    * support any format
    * one file for whole genome make storage easier
    * remote and range access
    * structure data are compressed to save space
"""

import sys
import os
import pickle
import zlib
import json
import glob
import argparse
from utils.binning import *

MAGIC = 'G3D'
VERSION = 1

# FIXED header size 512000 bytes
HEADER_LENGTH = 512000

def structure_files_to_g3d_file_wrap(args):
    structure_files_to_g3d_file(args.directory, args.output, args.format, args.genome, args.sample)

def structure_files_to_g3d_file(directory, output="output", sformat="pdb", genome="unknow_genome", sample="unknow_sample"):
    """
    Convert many text stucture files in one directory to a g3d format file.
    This folder should contain a list of files naming like chr1.pdb, chr2.pdb.. etc.

    :param directory: directory contains the structure files
    :param output: output g3d file name
    :param sformat: structure file format
    :param genome: genome information
    :param sample: sample information
    :return: null
    :raise: ValueError: raises ValueError while cannot find any structure file

    :example:

    python main.py dump test -g hg19 -s GM12878 -o GM12878_chr1_chr2

    TODO: resolution
    """
    files = glob.glob('{}/*.{}'.format(directory.strip('/'), sformat))
    if len(files) == 0:
        raise ValueError('cannot find any structure file')
    
    header = bytearray(HEADER_LENGTH)
    offset = HEADER_LENGTH
    with open('{}.g3d'.format(output), 'wb') as fout:
        fout.seek(HEADER_LENGTH)
        offsets = {}
        for f in files:
            with open(f, 'rU') as fin:
                pkldata = pickle.dumps(fin.read(), protocol=3)
                compressed = zlib.compress(pkldata)
                size = len(compressed)
                fn = os.path.basename(f)
                [chrom, fnformat] = fn.split('.')
                offsets[chrom] = {'offset': offset, 'size': size, 'chromosome': chrom, 'format': fnformat}
                fout.write(compressed)
                offset += size
        meta = {
            'magic': MAGIC,
            'version': VERSION,
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
    return pickle.loads(zlib.decompress(header_pkl))

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

def get_meta_wrap(args):
    get_meta(args.filename)

def get_meta(g3d_filename):
    '''convert g3d to many text stucture files.'''
    with open(g3d_filename, 'rb') as fin:
        header = read_header(fin)
    del header['offsets'] # too big to print
    del header['magic']
    json.dump(header, sys.stdout, indent=4)
    print()

def parse_3dg_to_g3d_wrap(args):
    parse_3dg_to_g3d(args.filename, args.output, args.genome, args.sample, args.resolutions)

def parse_3dg_to_g3d(file_name, out_file_name, genome, sample, resolutions):
    """
    Parse the .3dg format to .g3d format.
    """
    d = parse_3dg_file_to_g3dDict(file_name)
    gk = g3dKeeper(d, 20000)
    content = {} #key: resolution, value: g3dkeeper
    content[gk.resolution] = gk
    # write g3d file
    header = bytearray(HEADER_LENGTH)
    offset = HEADER_LENGTH
    with open('{}.g3d'.format(out_file_name), 'wb') as fout:
        fout.seek(HEADER_LENGTH)
        offsets = {}
        for namekey in gk.d:
            if namekey not in offsets:
                offsets[namekey] = {}
            for binkey in gk.d[namekey]:
                binlist = gk.d[namekey][binkey]
                binlist_str = [str(e) for e in binlist]
                pkldata = pickle.dumps(binlist_str, protocol=3) # pickle custom object cannot unpicked in JS API, use string instead
                compressed = zlib.compress(pkldata)
                size = len(compressed)
                offsets[namekey][binkey] = {'offset': offset, 'size': size}
                fout.write(compressed)
                offset += size
        meta = {
            'magic': MAGIC,
            'version': VERSION,
            'genome': genome,
            'sample': sample,
            'offsets': offsets,
            'resolutions': [int(x) for x in resolutions.split(',')]
        }
        fout.seek(0)
        meta_pkl = zlib.compress(pickle.dumps(meta, protocol=3))
        meta_pkl_len = len(meta_pkl)
        # print(meta_pkl_len)
        for i in range(0, meta_pkl_len):
            header[i] = meta_pkl[i]
        fout.write(header)

def query_g3d_file_wrap(args):
    query_g3d_file(args.filename, args.chrom, args.start, args.end, args.resolution, args.output, args.wholeChrom, args.wholeGenome)

def query_g3d_file(filename, chrom, start, end, resolution, output, wholeChrom=False, wholeGenome=False):
    """
    query structures from a g3d file
    """
    if not (wholeChrom or wholeChrom):
        if not (chrom and start and end):
            print('[Query] Error, please specify chromsome, start and end\n', file=sys.stderr)
    if output:
        fout = open(output, 'w')
    else:
        fout = sys.stdout
    with open(filename, 'rb') as fin:
        header = read_header(fin)
        offsets = header['offsets']
        if wholeGenome:
            for chrom in offsets:
                for binkey in offsets[chrom]:
                    write_contents_file_handle(fin, fout, offsets[chrom][binkey])
        elif wholeChrom:
            if chrom not in offsets:
                fout.close()
                return
            for binkey in offsets[chrom]:
                write_contents_file_handle(fin, fout, offsets[chrom][binkey])
        else:
            if chrom not in offsets:
                fout.close()
                return
            binkeys = reg2bins(start, end)
            for binkey in binkeys:
                if binkey not in offsets[chrom]: continue
                write_contents_file_handle(fin, fout, offsets[chrom][binkey])
    if output:
        fout.close()
    
def write_contents_file_handle(fh_in, fh_out, data):
    file_offset = data['offset']
    file_size = data['size']
    fh_in.seek(file_offset)
    file_pkl = fh_in.read(file_size)
    contents = pickle.loads(zlib.decompress(file_pkl))
    for con in contents:
        fh_out.write('{}\n'.format(con))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='g3dtools', description='g3dtools for operating text structure files with g3d format.')
    subparsers = parser.add_subparsers(title='subcommands',
                                        description='valid subcommands',
                                        help='additional help')
    #dump
    parser_dump = subparsers.add_parser('dump', help='dump structure files to g3d file')
    parser_dump.add_argument('directory', help='directory contains structure files.')
    parser_dump.add_argument('-g', '--genome', help='genome assembly, like hg19, m10 etc. default: unknow_genome', default='unknow_genome')
    parser_dump.add_argument('-s', '--sample', help='sample name. default: unknow_sample', default='unknow_sample')
    parser_dump.add_argument('-f', '--format', help='structure file format. default: pdb', default='pdb')
    parser_dump.add_argument('-o', '--output', help='output file name. default: output', default='output')
    parser_dump.set_defaults(func=structure_files_to_g3d_file_wrap)

    #paser 3dg
    parser_3dg = subparsers.add_parser('3dg', help='dump 3dg structure files to a g3d file')
    parser_3dg.add_argument('filename', help='file in .3dg file, can be gzip compressed.')
    parser_3dg.add_argument('-g', '--genome', help='genome assembly, like hg19, m10 etc. default: unknow_genome', default='unknow_genome')
    parser_3dg.add_argument('-s', '--sample', help='sample name. default: unknow_sample', default='unknow_sample')
    parser_3dg.add_argument('-r', '--resolutions', help='resolutions, like 20000,40000,80000. default: 0', default='0')
    parser_3dg.add_argument('-o', '--output', help='output file name. default: output', default='output')
    parser_3dg.set_defaults(func=parse_3dg_to_g3d_wrap)

    #meta
    parser_meta = subparsers.add_parser('meta', help='get metadata of a g3d file')
    parser_meta.add_argument('filename', help='a g3d file.')
    parser_meta.set_defaults(func=get_meta_wrap)

    #query
    parser_query = subparsers.add_parser('query', help='query structures from a g3d file')
    parser_query.add_argument('filename', help='file in .3dg file, can be gzip compressed.')
    parser_query.add_argument('-c', '--chrom', help='chromosome.')
    parser_query.add_argument('-s', '--start', type=int, help='start position')
    parser_query.add_argument('-e', '--end', type=int, help='end position')
    parser_query.add_argument('-r', '--resolution', help='specify one resolution, like 20000')
    parser_query.add_argument('-o', '--output', help='output file name, default outputs to screen')
    parser_query.add_argument('-C', '--wholeChrom', help='whether or not get contents from whole chromosome', action='store_true')
    parser_query.add_argument('-G', '--wholeGenome', help='whether or not get contents from whole genome', action='store_true')
    parser_query.set_defaults(func=query_g3d_file_wrap)

    args = parser.parse_args()
    args_len = len(vars(args))
    if args_len == 0:
        parser.print_help()
    if hasattr(args, 'func'):
        args.func(args)
