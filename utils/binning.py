#!/usr/bin/python
# programmer : Daofeng
# usage:

import sys, gzip

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
    r = l%cnt
    lis = []
    rr = r
    for i in range(cnt):
        if rr > 0:
            rr -= 1
            lis.append(c+1)
        else:
            lis.append(c)
    #return lis
    lis2 = []
    ts = start
    for i in range(cnt):
        te = ts + lis[i]
        lis2.append([ts, te])
        ts = te
    return lis2

class g3dElement(object):
    '''a g3d element object'''
    def __init__(self, chrom, start, end, x, y, z, haplotype='.'):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.x = x
        self.y = y
        self.z = z
        self.haplotype = haplotype
        self.length = end - start

    def __str__(self):
        return '{} {} {} {} {} {} {}'.format(self.chrom, self.start, self.end, self.x, self.y, self.z, self.haplotype)

    def __repr__(self):
        return self.__str__()
    
    def stringfyRegion(self):
        return '{}|{}|{}'.format(self.chrom, self.start, self.end)
    
    def to_array(self):
        return [self.chrom, self.start, self.end, self.x, self.y, self.z, self.haplotype]

class g3dKeeper(object):
    '''g3d keeper object'''
    def __init__(self, d, resolution):
        self.d = d
        self.namekeylist = d.keys()
        self.resolution = resolution

    def __len__(self):
        c = 0
        for i in self.d:
            for k in self.d[i]:
                for j in self.d[i][k]:
                    c += 1
        return c
    
    def write2File(self, outf):
        with open(outf, 'w') as fout:
            for i in self.d:
                for k in self.d[i]:
                    for j in self.d[i][k]:
                        fout.write('{}\n'.format(j))

    def get_g3d_element_by_region(self, namekey, start, end):
        """
            query g3d elements using chromsome, start ane end
            
            :return: a list of g3d elements in same bin
        """
        lst = []
        if namekey not in self.d: return lst
        binkeys = reg2bins(start, end)
        for binkey in binkeys:
            if binkey not in self.d[namekey]: continue
            binList = self.d[namekey][binkey]
            lst.extend(binList)
        return lst

    def get_g3d_element_whole_segment(self, namekey):
        """
            query g3d elements of one whole chromosome

            :return: a list of g3d elements in same chromosome
        """
        lst = []
        if namekey not in self.d: return lst
        for binkey in self.d[namekey]:
            binList = self.d[namekey][binkey]
            lst.extend(binList)
        return lst
    
    def get_all_g3d_element(self):
        """
            query all g3d elements

            :return: a list of g3d elements
        """
        lst = []
        for namekey in self.d:
            for binkey in self.d[namekey]:
                binList = self.d[namekey][binkey]
                lst.extend(binList)
        return lst
    
    def sort_by_start_each_bin(self):
        c = {}
        for i in self.d:
            c[i] = {}
            for k in self.d[i]:
                s = sorted(self.d[i][k], key=lambda x: x.start)
                c[i][k] = s
        self.d = c

def reg2bin(beg, end):
    '''convert region to bin, code from tabix'''
    end -= 1
    if (beg>>14 == end>>14): return 4681 + (beg>>14)
    if (beg>>17 == end>>17): return  585 + (beg>>17)
    if (beg>>20 == end>>20): return   73 + (beg>>20)
    if (beg>>23 == end>>23): return    9 + (beg>>23)
    if (beg>>26 == end>>26): return    1 + (beg>>26)
    return 0

def reg2bins(beg, end):
    '''convert region to bins, code from tabix'''
    lst = []
    lst.append(0)
    if (beg >= end): return lst
    if (end >= 1<<29): end = 1<<29
    end -= 1
    for k in range(1 + (beg>>26), 1 + (end>>26) + 1):
        lst.append(k)
    for k in range(9 + (beg>>23), 9 + (end>>23) + 1):
        lst.append(k)
    for k in range(73 + (beg>>20), 73 + (end>>20) + 1): 
        lst.append(k)
    for k in range(585 + (beg>>17), 585 + (end>>17) + 1):
        lst.append(k)
    for k in range(4681 + (beg>>14), 4681 + (end>>14) + 1):
        lst.append(k)
    return lst


def parse_3dg_file_to_g3dDict(f, keyIndex=0, startIndex=1, resolution=20000, xkey=2, ykey=3, zkey=4, delim = '\t', chrom = '', header=False):
    print('reading file {} to g3dDict...'.format(f), file=sys.stderr)
    d = {}
    c = 0
    with xread(f) as fin:
        if header: next(fin)
        for line in fin:
            lin = line.strip()
            if not lin: continue
            # print(lin)
            # sys.exit()
            t = lin.split(delim)
            name, hap = t[keyIndex].split('(')
            if not name.startswith('chr'):
                namekey = 'chr{}'.format(name)
            hap = hap.rstrip(')')
            if chrom:
                if namekey != chrom:
                    continue
            start = int(t[startIndex])
            end = start + resolution
            binkey = reg2bin(start, end)
            if namekey not in d:
                d[namekey] = {}
            if binkey not in d[namekey]:
                d[namekey][binkey] = [g3dElement(namekey, start, end, t[xkey], t[ykey], t[zkey], hap)]
            else:
                d[namekey][binkey].append(g3dElement(namekey, start, end, t[xkey], t[ykey], t[zkey], hap))
            c += 1
    print('done read {} records'.format(c), file=sys.stderr)
    return d

def parse_3dg_2_g3dKeeper(f, keyIndex=0, startIndex=1, resolution=20000, xkey=2, ykey=3, zkey=4, delim = '\t', chrom = '', header=False):
    return g3dKeeper(parse_3dg_file_to_g3dDict(f, keyIndex, startIndex, resolution, xkey, ykey, zkey, delim, chrom, header), resolution)

def scale_keeper(keeper, steplen, fold=2):
    """
        scales the keeper to a lower resolution by applying certain fold aggreagation

        :param keeper: the origin g3d keeper object
        :return: a new scaled keeper
    """
    chrom = 'chr7'
    # keeper.sort_by_start_each_bin()
    binkeys = keeper.d[chrom]
    # sbinkeys = sorted(binkeys)
    pat = []
    mat = []
    both = []
    for binkey in binkeys:
        for x in keeper.d[chrom][binkey]:
            if x.haplotype == 'mat' or x.haplotype == 'm':
                mat.append(x)
            elif x.haplotype == 'pat' or x.haplotype == 'p':
                pat.append(x)
            else:
                both.append(x)
    if len(pat) > 0:
        patsort = sorted(pat, key=lambda x: x.start)
        scaled = apply_scale(patsort, 20000, 5)
        # print(scaled)
        for x in scaled:
            print(x)
    if len(mat) > 0:
        matsort = sorted(mat, key=lambda x: x.start)
    if len(both) > 0:
        bothsort = sorted(both, key=lambda x: x.start)
        


def apply_scale(elementList, steplen, fold):
    total = len(elementList)
    scaled = []
    def scale_sub(start):
        for i in range(start, total - fold, fold):
            ok = []
            for j in range(i, i+fold-1):
                current = elementList[j]
                next_one = elementList[j+1]
                distance = next_one.start - current.start
                if distance == steplen: # nearby interval
                    ok.append(current)
                    if j == i+fold-2:
                        ok.append(next_one) # last iteration
                elif distance < steplen:
                    raise ValueError('{} and {} distance shorten than expected resolution {}'.format(current, next_one, steplen))
                else:
                    # a gap here
                    scaled.append([current])
                    scale_sub(j+1)
            if len(ok) > 0:
                scaled.append(ok)
    scale_sub(0)
    return scaled


    


def g3dElementAdd2Dict(d, namekey, start, end, x, y, z, haplotype):
    binkey = reg2bin(start, end)
    if namekey not in d:
        d[namekey] = {}
    if binkey not in d[namekey]:
        d[namekey][binkey] = [g3dElement(namekey, start, end, x, y, z, haplotype)]
    else:
        d[namekey][binkey].append(g3dElement(namekey, start, end, x, y, z, haplotype))

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
    return sd
    print('done', file=sys.stderr)


def main():
    keeper = parse_3dg_2_g3dKeeper('../test/GSM3271347_gm12878_01.impute3.round4.clean.3dg.txt.gz')
    scale_keeper(keeper, 20000)
    

if __name__=="__main__":
    main()
