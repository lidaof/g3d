#!/usr/bin/python
# programmer : Daofeng
# usage:

import sys
import gzip
import os

MATERNAL = 'maternal'
PATERNAL = 'paternal'
SHARED = 'shared'


def centerOf(start, end):
    return start + (end - start)/2


def xread(fn):
    if fn.endswith('.gz'):
        return gzip.open(fn, 'rt')
    else:
        return open(fn, 'rU')


def xwrite(fn):
    if fn.endswith('.gz'):
        return gzip.open(fn, 'wb')
    else:
        return open(fn, 'w')


def fileLines(f):
    c = 0
    with open(f, 'rU') as fin:
        for line in fin:
            c += 1
    return c


def average(values):
    return sum(values, 0.0) / len(values)


def olapBase(s1, e1, start, end):
    return min(e1, end) - max(s1, start)


def removeOverlapPart(s1, e1, start, end):
    me = min(e1, end)
    ms = max(s1, start)
    o = me - ms
    r = []
    if o > 0:
        if s1 < ms:
            r.append([s1, ms])
        if e1 > me:
            r.append([me, e1])
    else:
        r = [[s1, e1]]
    return r


def splitRegion(start, end, cnt):
    l = end - start
    c = l/cnt
    r = l % cnt
    lis = []
    rr = r
    for i in range(cnt):
        if rr > 0:
            rr -= 1
            lis.append(c+1)
        else:
            lis.append(c)
    # return lis
    lis2 = []
    ts = start
    for i in range(cnt):
        te = ts + lis[i]
        lis2.append([ts, te])
        ts = te
    return lis2


class g3dItem(object):
    '''a g3d item object'''

    def __init__(self, chrom, start, x, y, z):
        self.chrom = chrom
        self.start = int(start)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        return '{}\t{}\t{}\t{}\t{}'.format(self.chrom, self.start, self.x, self.y, self.z)

    def __repr__(self):
        return self.__str__()

    def stringfyRegion(self):
        return '{}|{}'.format(self.chrom, self.start)

    def to_array(self):
        return [self.chrom, self.start, self.x, self.y, self.z]


def summary_g3d_items(element_list):
    if len(element_list) == 0:
        raise ValueError("empty element list to summary")
    elif len(element_list) == 1:
        return element_list[0]
    else:
        # the element list is sorted
        chrom = element_list[0].chrom
        start = element_list[0].start
        x = average([i.x for i in element_list])
        y = average([i.y for i in element_list])
        z = average([i.z for i in element_list])
        return g3dItem(chrom, start, x, y, z)


class g3dKeeperV2(object):
    '''g3d keeper object'''

    def __init__(self, d, resolution):
        self.d = d
        self.haplotypes = d.keys()
        self.resolution = resolution

    def __len__(self):
        c = 0
        for i in self.d:
            for k in self.d[i]:
                c += len(self.d[i][k])
        return c

    def write2File(self, outf):
        with open(outf, 'w') as fout:
            for i in self.d:
                for k in self.d[i]:
                    for j in self.d[i][k]:
                        fout.write('{}\t{}\n'.format(j, i))


def parse_3dg_file_to_g3dDict(f, keyIndex=0, startIndex=1, resolution=20000, xkey=2, ykey=3, zkey=4, delim='\t', chrom='', header=False):
    print('Reading file {}'.format(f), file=sys.stderr)
    if not os.path.exists(f):
        print('Error: {} not exist, please check'.format(f), file=sys.stderr)
        sys.exit(2)
    d = {}
    c = 0
    with xread(f) as fin:
        if header:
            next(fin)
        for line in fin:
            lin = line.strip()
            if not lin:
                continue
            # print(lin)
            # sys.exit()
            t = lin.split(delim)
            name, hap = t[keyIndex].split('(')
            if not name.startswith('chr'):
                namekey = 'chr{}'.format(name)
            hap = hap.rstrip(')')
            if hap == 'pat':
                hap = 'p'
            if hap == 'mat':
                hap = 'm'
            if chrom:
                if namekey != chrom:
                    continue
            # if namekey!= 'chr7': continue
            start = int(t[startIndex])
            end = start + resolution
            binkey = reg2bin(start, end)
            if namekey not in d:
                d[namekey] = {}
            if binkey not in d[namekey]:
                d[namekey][binkey] = [g3dElement(
                    namekey, start, end, t[xkey], t[ykey], t[zkey], hap)]
            else:
                d[namekey][binkey].append(g3dElement(
                    namekey, start, end, t[xkey], t[ykey], t[zkey], hap))
            c += 1
    print('Done read {} records'.format(c), file=sys.stderr)
    return d


def parse_3dg_2_g3dKeeper(f, keyIndex=0, startIndex=1, resolution=20000, xkey=2, ykey=3, zkey=4, delim='\t', chrom='', header=False):
    d = parse_3dg_file_to_g3dDict(
        f, keyIndex, startIndex, resolution, xkey, ykey, zkey, delim, chrom, header)
    dk = g3dKeeper(d, resolution)
    dk.sort_by_start_each_bin()
    return dk


def parse_pastis_2_g3dKeeper(f, resolution, chrom, header):
    d = parse_pastis_file_to_g3dDict(f, resolution, chrom, header)
    dk = g3dKeeper(d, resolution)
    dk.sort_by_start_each_bin()
    return dk


def parse_pastis_file_to_g3dDict(f, resolution=10000, chrom='', header=False):
    print('Reading file {}'.format(f), file=sys.stderr)
    if not os.path.exists(f):
        print('Error: {} not exist, please check'.format(f), file=sys.stderr)
        sys.exit(2)
    if not chrom:
        print('Error: chromosome not specified, please check', file=sys.stderr)
        sys.exit(2)
    d = {}
    c = 0
    with xread(f) as fin:
        if header:
            next(fin)
        for line in fin:
            lin = line.strip()
            if not lin:
                continue
            t = lin.split('\t')
            namekey = chrom
            hap = 's'
            start = int(t[0])
            end = start + resolution
            binkey = reg2bin(start, end)
            if namekey not in d:
                d[namekey] = {}
            if binkey not in d[namekey]:
                d[namekey][binkey] = [g3dElement(
                    namekey, start, end, t[1], t[2], t[3], hap)]
            else:
                d[namekey][binkey].append(g3dElement(
                    namekey, start, end, t[1], t[2], t[3], hap))
            c += 1
    print('Done read {} records'.format(c), file=sys.stderr)
    return d


def parse_g3d_bed_file_v2(f, keyIndex=0, startIndex=1, endIndex=2, xkey=3, ykey=4, zkey=5, hapIndex=6, resolution=20000, delim='\t', chrom='', header=False):
    '''
    Reading g3d bed file to a dict.
        key: haplotype, can be SHARED if not specified, or MATERNAL, PATERNAL 
        value: dict of data, key: chrom, value: [list of g3dItem]
    '''
    print('Reading file {}'.format(f), file=sys.stderr)
    if not os.path.exists(f):
        print('Error: {} not exist, please check'.format(f), file=sys.stderr)
        sys.exit(2)
    d = {}
    c = 0
    with xread(f) as fin:
        if header:
            next(fin)
        for line in fin:
            lin = line.strip()
            if not lin:
                continue
            # print(lin)
            # sys.exit()
            t = lin.split(delim)
            namekey = t[keyIndex]
            if namekey == 'MT':
                namekey = 'chrM'
            if not namekey.startswith('chr'):
                namekey = 'chr{}'.format(namekey)
            if len(t) < 7:
                hap = SHARED
            else:
                hap = t[6].lower()
            if hap == 'pat' or hap == 'p':
                hap = PATERNAL
            if hap == 'mat' or hap == 'm':
                hap = MATERNAL
            if chrom:  # filter by chrom if specified
                if namekey != chrom:
                    continue
            start = int(t[startIndex])
            if hap not in d:
                d[hap] = {}
            if namekey not in d[hap]:
                d[hap][namekey] = [
                    g3dItem(namekey, start, t[xkey], t[ykey], t[zkey])]
            else:
                d[hap][namekey].append(
                    g3dItem(namekey, start, t[xkey], t[ykey], t[zkey]))
            c += 1
    print('Done read {} records'.format(c), file=sys.stderr)
    print('Sorting', file=sys.stderr)
    sd = {}
    for k in d:
        sd[k] = {}
        for chrom in d[k]:
            v = sorted(d[k][chrom], key=lambda x: x.start)
            sd[k][chrom] = v
    return sd


def parse_g3d_bed_g3dKeeper_v2(f, keyIndex=0, startIndex=1, endIndex=2, xkey=3, ykey=4, zkey=5, hapIndex=6, resolution=20000, delim='\t', chrom='', header=False):
    d = parse_g3d_bed_file_v2(
        f, keyIndex, startIndex, endIndex, xkey, ykey, zkey, hapIndex, resolution, delim, chrom, header)
    dk = g3dKeeperV2(d, resolution)
    return dk


def parse_nucle3d_2_keeper_v2(f):
    d, resolution = parse_nucle3d_file_v2(f)
    dk = g3dKeeperV2(d, resolution)
    return dk


def parse_nucle3d_file_v2(f):
    '''
    Reading nucle3d bed file to a dict.
        key: haplotype, can be SHARED if not specified, or MATERNAL, PATERNAL 
        value: dict of data, key: chrom, value: [list of g3dItem]
    '''
    print('Reading file {}'.format(f), file=sys.stderr)
    if not os.path.exists(f):
        print('Error: {} not exist, please check'.format(f), file=sys.stderr)
        sys.exit(2)
    d = {}
    c = 0
    hap = SHARED
    reso = 0
    namekey = ''
    with xread(f) as fin:
        for line in fin:
            lin = line.strip()
            if not lin:
                continue
            # print(lin)
            # sys.exit()
            if lin.startswith('TITLE'):
                continue
            if lin.startswith('GENOME'):
                continue
            if lin.startswith('BINSIZE'):
                t = lin.split()
                reso = int(t[1])
                continue
            if lin.startswith('CHR'):
                t = lin.split()
                namekey = t[1]
                continue
            t = lin.split(',')
            start = int(t[0])*reso
            if hap not in d:
                d[hap] = {}
            if namekey not in d[hap]:
                d[hap][namekey] = [
                    g3dItem(namekey, start, t[1], t[2], t[3])]
            else:
                d[hap][namekey].append(
                    g3dItem(namekey, start, t[1], t[2], t[3]))
            c += 1
    print('Done read {} records'.format(c), file=sys.stderr)
    print('Sorting', file=sys.stderr)
    sd = {}
    for k in d:
        sd[k] = {}
        for chrom in d[k]:
            v = sorted(d[k][chrom], key=lambda x: x.start)
            sd[k][chrom] = v
    return [sd, reso]


def scale_keeper_v2(keeper, fold=2):
    """
        scales the keeper to a lower resolution by applying certain fold aggreagation
        :param keeper: the origin g3d keeper object
        :return: a new scaled keeper
    """
    print('Applying scale {}'.format(fold), file=sys.stderr)
    d = {}
    for hap in keeper.d:
        d[hap] = {}
        for chrom in keeper.d[hap]:
            values = keeper.d[hap][chrom]    # already sorted
            scaled = []
            if len(values) > 0:
                chunks = prepare_chunk(values, keeper.resolution, fold)
                for x in chunks:
                    scaled.append(summary_g3d_items(x))
            d[hap][chrom] = scaled
    return g3dKeeperV2(d, keeper.resolution * fold)


def prepare_chunk(elementList, steplen, fold):
    """
        Prepare chunk for scaling, merge elements to nearby *fold* region, skip gaps
    """
    total = len(elementList)
    chunks = []
    start = 0

    def chunk_sub(start):
        gap = False
        for i in range(start, total - fold, fold):
            ok = [elementList[i]]
            for j in range(i+1, i+fold):
                current = elementList[j]
                distance = current.start - ok[0].start
                # nearby interval or in fold interval range
                if distance <= steplen * (fold - 1):
                    ok.append(current)
                    # if j == i+fold-1:
                    #     ok.append(next_one) # last iteration
                elif distance < steplen:
                    raise ValueError('{} and {} distance shorten than expected resolution {}'.format(
                        current, ok[0], steplen))
                else:
                    # a gap here
                    # chunks.append(ok)
                    gap = True
                    start = j
                    break
            chunks.append(ok)
            if gap:
                break
        if gap:
            chunk_sub(start)
    chunk_sub(start)
    return chunks


def count_g3d_dict_element(d):
    c = 0
    for i in d:
        for k in d[i]:
            c += len(d[i][k])
    return c


def g3d_dict_to_simple_dict(d):
    print('converting g3dDict to simple Dict', file=sys.stderr)
    sd = {}
    for i in d:
        for k in d[i]:
            for j in d[i][k]:
                sd[j.stringfyRegion()] = str(j)
    print('done', file=sys.stderr)
    return sd


def main():
    pass


if __name__ == "__main__":
    main()
