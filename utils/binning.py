#!/usr/bin/python
# programmer : Daofeng
# usage:

from itertools import combinations
from itertools import izip
from copy import deepcopy
from bisect import bisect_left
import sys, os, random, gzip, shlex, glob


def centerOf(start, end):
    return start + (end - start)/2

def xread(fn):
    if fn.endswith('.gz'):
        return gzip.open(fn, 'rb')
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

def regionOverlapByCriteria(qs, qe, ts, te, **cri):
    olap = olapBase(qs, qe, ts, te)
    if olap <= 0: return False
    olap = float(olap)
    byBp = cri['byBp']
    byPctShort = cri['byPctShort']
    byPctLong = cri['byPctLong']
    byPctTest = cri['byPctTest']
    byPctTarget = cri['byPctTarget']
    ql = qe - qs
    tl = te - ts
    l = max(ql, tl)
    s = min(ql, tl)
    if byBp:
        if olap >= byBp: return True
    elif byPctShort:
        if olap/s >= byPctShort: return True
    elif byPctLong:
        if olap/l >= byPctLong: return True
    elif byPctTest:
        if olap/ql >= byPctTest: return True
    elif byPctTarget:
        if olap/tl >= byPctTarget: return True
    else:
        return False
    return False 

class binElement(object):
    '''bin element object'''
    def __init__(self, chrom, start, end, value, name=''):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.value = value
        self.length = end - start
        self.name = name

    def __str__(self):
        return '{}:{}-{}|{}'.format(self.chrom, self.start, self.end, self.name)

    def __repr__(self):
        return self.__str__()
    
    def stringfyRegion(self):
        return '{}|{}|{}'.format(self.chrom, self.start, self.end)
    
    def overlapBase(self, start, end):
        return min(self.end, end) - max(self.start, start)
    
    def overlapFracSelf(self, start, end):
        return (min(self.end, end) - max(self.start, start))/float(self.length)
    
    def overlapFracTarget(self, start, end):
        return (min(self.end, end) - max(self.start, start))/float(end - start)

    def overlapRegion(self, start, end):
        [s, e] = [max(self.start, start), min(self.end, end)]
        if e > s:
            return [s, e]
        else:
            return []
    
    def overlapMergeRegion(self, start, end):
        if self.overlapBase(start, end) > 0:
            return [min(self.start, start), max(self.end, end)]
        else:
            return []
    
    def overlapRelativeRegion(self, start, end):
        return [max(self.start, start) - self.start, min(self.end, end) - self.start]

    def inRegion(self, start, end):
        if self.start >= start and self.end <= end:
            return True
        else:
            return False
    
    def includeRegion(self, start, end):
        if self.start <= start and self.end >= end:
            return True
        else:
            return False

class binKeeper(object):
    '''bin keeper object'''
    def __init__(self, d):
        self.d = d
        self.namekeylist = d.keys()

    def __len__(self):
        c = 0
        for i in self.d:
            for k in self.d[i]:
                for j in self.d[i][k]:
                    c += 1
        return c
    
    def output2File(self, outf):
        with open(outf, 'w') as fout:
            for i in self.d:
                for k in self.d[i]:
                    for j in self.d[i][k]:
                        #print >> sys.stderr, i
                        #print >> sys.stderr, j.value
                        #exit(1)
                        #fout.write('{}\t{}\t{}\t{}\n'.format(i, j.start, j.end, j.value[7]))
                        #tmp = [str(x) for x in j.value]
                        fout.write('{}\n'.format('\t'.join(j.value)))

    def __and__(self, other):
        """Return the intersection of two sets as a new set.

        (I.e. all elements that are in both sets.)
        """
        if not isinstance(other, binKeeper):
            return NotImplemented
        return self.intersection(other)

    def intersection(self, other):
        """Return the intersection of two sets as a new set.

        (I.e. all elements that are in both sets.)
        """
        if not isinstance(other, binKeeper):
            other = self.__class__(other)
        d1, d2 = self.d, other.d
        #'''
        d = {}
        b = self.__class__(d)
        for namekey in d1:
            if namekey not in d2: continue
            for binkey in d1[namekey]:
                #if binkey not in d2[namekey]: continue
                binlis1 = d1[namekey][binkey]
                #binlis2 = d2[namekey][binkey] # this is buggy, because the overlap regions may have different binkeys, like one region is very wide
                for i in binlis1:
                    binkey2s = reg2bins(i.start, i.end)
                    for binkey2 in binkey2s:
                        if binkey2 not in d2[namekey]: continue
                        binlis2 = d2[namekey][binkey2]
                        for j in binlis2:
                            if i.overlapBase(j.start, j.end) > 0:
                                s, e = i.overlapRegion(j.start, j.end)
                                tmp = deepcopy(j.value) # use j.value as value was bias, need fixed later
                                tmp[0] = namekey # also the position was hard coded
                                tmp[1] = str(s)
                                tmp[2] = str(e)
                                b.add(binElement(namekey, s, e, tmp))
                                #break
        return b
        #'''
        #return self.__class__(overlap2binDictNew(d1,d2)) # same purpose, need imporve code re-usage
    
    def  __sub__(self, other):
        """Return the difference of two sets as a new Set.

        (I.e. all elements that are in this set and not in the other.)
        """
        if not isinstance(other, binKeeper):
            return NotImplemented
        return self.difference(other)

    def difference(self, other):
        """Return the difference of two sets as a new Set.

        (I.e. all elements that are in this set and not in the other.)
        """
        d1, d2 = self.d, other.d
        d = deepcopy(d1)
        for namekey in d1:
            if namekey not in d2: continue
            for binkey in d1[namekey]:
                binlis1 = d1[namekey][binkey]
                tlis = []
                for i in binlis1:
                    olap = False
                    binkey2s = reg2bins(i.start, i.end)
                    for binkey2 in binkey2s:
                        if binkey2 not in d2[namekey]: continue
                        binlis2 = d2[namekey][binkey2]
                        for j in binlis2:
                            if i.overlapBase(j.start, j.end) > 0:
                                olap = True
                                break
                    if not olap:
                        tlis.append(i)
                if tlis:
                    d[namekey][binkey] = tlis
                else:
                    del d[namekey][binkey]
        return self.__class__(d)

    # Membership test

    def __contains__(self, element):
        """Report whether an element is a member of a set.

        (Called in response to the expression `element in self'.)
        """
        namekey = element.chrom
        if namekey not in self.d: return False
        for k in self.d[namekey]:
            for j in self.d[namekey][k]:
                if j.start == element.start and j.end == element.end:
                    return True
        return False

    def add(self, element):
        chrom = element.chrom
        start = element.start
        end = element.end
        namekey = element.chrom
        value = element.value
        binkey = reg2bin(start, end)
        if namekey not in self.d:
            self.d[namekey] = {}
        if binkey not in self.d[namekey]:
            self.d[namekey][binkey] = [binElement(chrom, start, end, value)]
        else:
            self.d[namekey][binkey].append(binElement(chrom, start, end, value))
    
    def intersectionMerge(self, other):
        """Return the intersection merge of two sets as a new set.

        (I.e. all elements that are in both sets.)
        a         b
        -----------
            c        d
            ----------
        return [a, d]
        """
        if not isinstance(other, binKeeper):
            other = self.__class__(other)
        d1, d2 = self.d, other.d
        d = {}
        b = self.__class__(d)
        for namekey in d1:
            if namekey not in d2: continue
            for binkey in d1[namekey]:
                binlis1 = d1[namekey][binkey]
                for i in binlis1:
                    binkey2s = reg2bins(i.start, i.end)
                    for binkey2 in binkey2s:
                        if binkey2 not in d2[namekey]: continue
                        binlis2 = d2[namekey][binkey2]
                        for j in binlis2:
                            if i.overlapBase(j.start, j.end) > 0:
                                s, e = i.overlapMergeRegion(j.start, j.end)
                                tmp = deepcopy(j.value) # use j.value as value was bias, need fixed later
                                tmp[0] = namekey # also the position was hard coded
                                tmp[1] = str(s)
                                tmp[2] = str(e)
                                b.add(binElement(namekey, s, e, tmp))
                                #break
        bd = b.mergeOverlap()
        return bd

    def _update(self, other):
        if not isinstance(other, binKeeper):
            other = self.__class__(other)
        for i in other.d:
            for k in other.d[i]:
                for j in other.d[i][k]:
                    self.add(j)
    
    def unionMerge(self, other):
        """Return the union merged of two sets as a new set.

        (I.e. all elements that are in both sets.)
        """
        if not isinstance(other, binKeeper):
            other = self.__class__(other)
        inter = self.intersectionMerge(other)
        aonly = self - inter
        bonly = other - inter
        d = {}
        b = self.__class__(d)
        b._update(aonly)
        b._update(bonly)
        b._update(inter)
        return b
    
    def mergeOverlap(self):
        """merge overlap of a binKeeper
        """
        d = self.d
        for namekey in d:
            for binkey in d[namekey]:
                binlis = d[namekey][binkey]
                for i in binlis:
                    for j in binlis:
                        if i.overlapBase(j.start, j.end) > 0:
                            s, e = i.overlapMergeRegion(j.start, j.end)
                            i.start = s
                            i.end = e
        d1 = {}
        b = self.__class__(d1)
        for namekey in d:
            for binkey in d[namekey]:
                binlis = d[namekey][binkey]
                for i in binlis:
                    if i not in b:
                        b.add(i)
        return b

def reg2bin(beg, end):
    '''convert region to bin, code from tabix'''
    end -= 1
    if (beg>>14 == end>>14): return 4681 + (beg>>14)
    if (beg>>17 == end>>17): return  585 + (beg>>17)
    if (beg>>20 == end>>20): return   73 + (beg>>20)
    if (beg>>23 == end>>23): return    9 + (beg>>23)
    if (beg>>26 == end>>26): return    1 + (beg>>26)
    return 0

#MAX_BIN = 37450 # =(8^6-1)/7+1

def reg2bins(beg, end):
    '''convert region to bins, code from tabix'''
    lst = []
    lst.append(0)
    if (beg >= end): return lst
    if (end >= 1<<29): end = 1<<29
    end -= 1
    for k in xrange(1 + (beg>>26), 1 + (end>>26) + 1):
        lst.append(k)
    for k in xrange(9 + (beg>>23), 9 + (end>>23) + 1):
        lst.append(k)
    for k in xrange(73 + (beg>>20), 73 + (end>>20) + 1): 
        lst.append(k)
    for k in xrange(585 + (beg>>17), 585 + (end>>17) + 1):
        lst.append(k)
    for k in xrange(4681 + (beg>>14), 4681 + (end>>14) + 1):
        lst.append(k)
    return lst

def lstLargestIndex(lst):
    m = max(lst)
    if m == 0:
        return []
    pos = [i for i, j in enumerate(lst) if j == m]
    return pos

def calRegionByIndex(start, pos):
    lst = []
    for p in pos:
        s = start + p - 25
        e = start + p + 25
        if lst:
            if s <= lst[-1][1]:
                lst[-1][1] = e
            else:
                lst.append([s, e])
        else:
            lst.append([s, e])
    return lst


def file2binDict(f, keyIndex=0, startIndex=1, endIndex=2, delim = '\t', chrom = '', header=False):
    print >> sys.stderr, 'reading file {} to binDict ...'.format(f)
    d = {}
    #with open(f, "rU") as fin:
    with xread(f) as fin:
        if header: next(fin)
        for line in fin:
            #if not line.strip(): continue
            t = line.strip().split(delim)
            #if len(t) < 10: continue # need comment out later
            namekey = t[keyIndex]
            if chrom:
                if namekey != chrom:
                    continue
            start = int(t[startIndex])
            end = int(t[endIndex])
            #if len(t) == 10: # bo suggested for overlapping with cage tinats, do extention of 1k
                #print start, end
                #print >> sys.stderr, 'extension...'
            #    start = start - 1000
            #    end = end + 1000
                #print start, end
                #sys.exit(1)
            binkey = reg2bin(start, end)
            if namekey not in d:
                d[namekey] = {}
            if binkey not in d[namekey]:
                d[namekey][binkey] = [binElement(namekey, start, end, t)]
                #d[namekey][binkey] = [binElement(namekey, start, end, t, t[3])]
                #d[namekey][binkey] = [binElement(namekey, start, end, [], t[3])]
                #d[namekey][binkey] = [binElement(namekey, start, end, [0,0,0,0,0,0], t[3])]
                #d[namekey][binkey] = [binElement(start, end, t[3].split('/')[0])]
            else:
                d[namekey][binkey].append(binElement(namekey, start, end, t))
                #d[namekey][binkey].append(binElement(namekey, start, end, t, t[3]))
                #d[namekey][binkey].append(binElement(namekey, start, end, [], t[3]))
                #d[namekey][binkey].append(binElement(namekey, start, end, [0,0,0,0,0,0], t[3]))
                #d[namekey][binkey].append(binElement(start, end, t[3].split('/')[0]))
    print >> sys.stderr, 'done'
    return d

def fileList2binDict(flis, keyIndex=0, startIndex=1, endIndex=2, delim = '\t'):
    d = {}
    for f in flis:
        print >> sys.stderr, 'reading file {} to binDict ...'.format(f)
        with xread(f) as fin:
            for line in fin:
                #if not line.strip(): continue
                t = line.strip().split(delim)
                #if len(t) < 10: continue # need comment out later
                namekey = t[keyIndex]
                start = int(t[startIndex])
                end = int(t[endIndex])
                binkey = reg2bin(start, end)
                if namekey not in d:
                    d[namekey] = {}
                if binkey not in d[namekey]:
                    #d[namekey][binkey] = [binElement(namekey, start, end, t, t[3])]
                    d[namekey][binkey] = [binElement(namekey, start, end, 0, t[3])]
                    #d[namekey][binkey] = [binElement(start, end, t[3].split('/')[0])]
                else:
                    #d[namekey][binkey].append(binElement(namekey, start, end, t, t[3]))
                    d[namekey][binkey].append(binElement(namekey, start, end, 0, t[3]))
                    #d[namekey][binkey].append(binElement(start, end, t[3].split('/')[0]))
        print >> sys.stderr, 'done'
    return d


def file2binKeeper(f, keyIndex=0, startIndex=1, endIndex=2, delim = '\t', chrom='',header=False):
    return binKeeper(file2binDict(f, keyIndex, startIndex, endIndex, delim, chrom, header))

def binElementAdd2Dict(d, namekey, start, end, value):
    binkey = reg2bin(start, end)
    if namekey not in d:
        d[namekey] = {}
    if binkey not in d[namekey]:
        d[namekey][binkey] = [binElement(namekey, start, end, value)]
    else:
        d[namekey][binkey].append(binElement(namekey, start, end, value))


def overlap2binDict(d1, d2): # buggy, might miss when one very wide region include a small region as they also have different binkeys
    #olapCount = 0
    d = {}
    for namekey in d1:
        if namekey not in d2: continue
        for binkey in d1[namekey]:
            if binkey not in d2[namekey]: continue
            binlis1 = d1[namekey][binkey]
            binlis2 = d2[namekey][binkey]
            for i in binlis1:
                #olap = False
                for j in binlis2:
                    if i.overlapBase(j.start, j.end) > 0:
                        #olapCount += 1
                        #olap = True
                        s, e = i.overlapRegion(j.start, j.end)
                        binElementAdd2Dict(d, namekey, s, e, 0)
                        #break
                #if olap:
                #    break
    #return [olapCount, d]
    return d

def overlap2binDictNew(d1, d2):
    rd1 = {} # regions not overlap with d2 in d1
    rd2 = {} # regions not overlap with d1 in d2
    od1 = {} # regions overlap d2 in d1
    od2 = {} # regions overlap d1 in d2
    d = {} # overlap regions
    #did not fix yet
    for namekey in d1:
        if namekey not in d2: continue
        for binkey in d1[namekey]:
            binlis1 = d1[namekey][binkey]
            for i in binlis1:
                olap = False
                okeys = reg2bins(i.start, i.end)
                for okey in okeys:
                    if okey not in d2[namekey]: continue
                    binlis2 = d2[namekey][okey]
                    for j in binlis2:
                        if i.overlapBase(j.start, j.end) > 0:
                            s, e = i.overlapRegion(j.start, j.end)
                            tmp = deepcopy(j.value)
                            tmp[1] = str(s)
                            tmp[2] = str(e)
                            binElementAdd2Dict(d, namekey, s, e, tmp)
                            olap = True
                if olap:
                    binElementAdd2Dict(od1, namekey, i.start, i.end, i.value)
                else:
                    binElementAdd2Dict(rd1, namekey, i.start, i.end, i.value)
    return d

def countBinDictElement(d):
    c = 0
    for i in d:
        for k in d[i]:
            for j in d[i][k]:
                #print '{}\t{}\t{}'.format(i, j.start, j.end)
                c += 1
    return c

def sortBinDictByStart(d):
    c = {}
    for i in d:
        c[i] = {}
        for k in d[i]:
            s = sorted(d[i][k], key=lambda x: x.start)
            c[i][k] = s
    return c

def binDict2SimpleDict(d):
    print >> sys.stderr, 'converting binDict to simple Dict'
    sd = {}
    for i in d:
        for k in d[i]:
            for j in d[i][k]:
                sd[j.stringfyRegion()] = '|'.join(j.value)
    return sd
    print >> sys.stderr, 'done'
    


def binDictListOverlap(lis):
    l = len(lis)
    data = {}
    for i in range(l):
        data[i] = lis[i]
    res = {}
    for i in range(l):
        for j in combinations(data.keys(), i+1):
            tes = [data[k] for k in j]
            res[tuple(sorted(j))] = reduce(lambda x, y: overlap2binDict(x, y), tes)
    okeys = sorted(res.keys(), key=lambda x: (len(x), x[0]))
    r = []
    #with open(outf, 'w') as fout:
    for i in okeys:
        #fout.write('{}\n\t{}\n'.format(i, countBinDictElement(res[i])))
        r.append([i, res[i]])
    return r

def fileListOverlap(flis, keyIndex, startIndex, endIndex, outf):
    blis = []
    for i in flis:
        blis.append(file2binDict(i, keyIndex, startIndex, endIndex))
    r = binDictListOverlap(blis)
    with open(outf, 'w') as fout:
        for k in r:
            names = tuple([flis[i] for i in k[0]])
            v = countBinDictElement(k[1])
            fout.write('{}\n\t{}\n'.format(names, v))


def zerobinDict(d):
    '''make each of the element in binDict value list to zero'''
    print >> sys.stderr, 'Zeroing...'
    for namekey in d:
        for binkey in d[namekey]:
            for elem in d[namekey][binkey]:
                elem.value = 0
                #for j in xrange(len(elem.value)):
                #    elem.value[j] = 0

def assignZeroListbinDict(d, length):
    '''make each of the element in binDict value as value parameter'''
    print >> sys.stderr, 'Assigning value...'
    for namekey in d:
        for binkey in d[namekey]:
            for elem in d[namekey][binkey]:
                elem.value = []
                for i in range(length):
                    elem.value.append(0)
                #for j in xrange(len(elem.value)):
                #    elem.value[j] = 0

def twobinDictFilterFile(d1, d2, infile, outfile, keyIndex=0, startIndex=1, endIndex=2, delim = '\t'):
    print >> sys.stderr, 'selecting file {} ...'.format(infile)
    with open(infile, "rU") as fin, open(outfile, 'w') as fout:
        c1 = c2 = c3 = c4 = c = 0
        for line in fin:
            if line.startswith('#'): continue
            c += 1
            t = line.strip().split(delim)
            namekey = t[keyIndex]
            start = int(t[startIndex])
            end = int(t[endIndex])
            iso1,v1 = regionIncludebinDict(d1, namekey, start, end)
            iso2,v2 = regionIncludebinDict(d2, namekey, start, end)
            if v1:
                v11 = v1[6]
            else:
                v11 = 0
            if v2:
                v22 = v2[4]
            else:
                v22 = 0
            fout.write('{}\t{}\t{}\t{}\t{}\n'.format(line.strip(), iso1, iso2, v11, v22))
            if iso1:
                if iso2:
                    c1 += 1
                else:
                    c2 += 1
            else:
                if iso2:
                    c3 += 1
                else:
                    c4 += 1
    assert sum([c1, c2, c3, c4]) == c
    print 'both   : {}'.format(c1)
    print 'only 1 : {}'.format(c2)
    print 'only 2 : {}'.format(c3)
    print 'neither: {}'.format(c4)
    print 'total  : {}'.format(c)
    print >> sys.stderr, 'done'

def binDictFilterFile(d, infile, outfile, keyIndex=0, startIndex=1, endIndex=2, delim = '\t'):
    print >> sys.stderr, 'selecting file {} ...'.format(infile)
    with open(infile, "rU") as fin, open(outfile, 'w') as fout:
        for line in fin:
            if line.startswith('#'): continue
            isOverlap = False
            t = line.strip().split(delim)
            namekey = t[keyIndex]
            start = int(t[startIndex])
            end = int(t[endIndex])
            if namekey not in d: continue
            binkeys = reg2bins(start, end)
            for binkey in binkeys:
                if binkey not in d[namekey]: continue
                binList = d[namekey][binkey]
                for i in binList:
                    if i.overlapBase(start, end) > 0:
                    #if i.inRegion(start, end):
                        isOverlap = True
                        break
            if isOverlap:
                fout.write(line)
    print >> sys.stderr, 'done'

def binDictFilterOutFile(d, infile, outfile, keyIndex, startIndex, endIndex, delim = '\t'):
    print >> sys.stderr, 'selecting file {} ...'.format(infile)
    with open(infile, "rU") as fin, open(outfile, 'w') as fout:
        for line in fin:
            isOverlap = False
            t = line.strip().split(delim)
            namekey = t[keyIndex]
            start = int(t[startIndex])
            end = int(t[endIndex])
            if namekey not in d: 
                fout.write(line)
                continue
            binkeys = reg2bins(start, end)
            for binkey in binkeys:
                if binkey not in d[namekey]: continue
                binList = d[namekey][binkey]
                for i in binList:
                    if i.overlapBase(start, end) > 0:
                    #if i.inRegion(start, end):
                        isOverlap = True
                        break
            if not isOverlap:
                fout.write(line)
    print >> sys.stderr, 'done'

def binDictInFile(d, infile, outfile, keyIndex=0, startIndex=1, endIndex=2, delim = '\t', extend = 0):
    print >> sys.stderr, 'selecting file {} ...'.format(infile)
    with open(infile, "rU") as fin, open(outfile, 'w') as fout:
        for line in fin:
            t = line.strip().split(delim)
            namekey = t[keyIndex]
            start = int(t[startIndex]) - extend
            end = int(t[endIndex]) + extend
            if namekey not in d:
                fout.write('{}\t'.format(line.strip()))
                fout.write('{}\n'.format('null'))
                continue
            tmp = []
            binkeys = reg2bins(start, end)
            for binkey in binkeys:
                if binkey not in d[namekey]: continue
                binList = d[namekey][binkey]
                #fout.write('{0[5]}\t{0[6]}\t{0[7]}\t{0[10]}\t{0[11]}\t{0[12]}\t'.format(t))
                for i in binList:
                    #if i.overlapBase(start, end) > 0:
                    if i.inRegion(start, end):
                    #if i.includeRegion(start, end):
                        #tmp.append('{}|{}|{}|{}'.format(i.chrom, i.start, i.end, i.name))
                        #tmp.append('{0[0]}|{0[1]}|{0[2]}|{0[3]}'.format(i.value))
                        #tmp.append('{0[5]}|{0[6]}|{0[7]}|{0[10]}'.format(i.value))
                        #tmp.append('{0[1]}|{0[2]}|{0[3]}|{0[0]}'.format(i.value))
                        #tmp.append(i.value)
                        fout.write('{0[0]}\t{0[1]}\t{0[2]}\t{0[4]}\n'.format(i.value))
            #if tmp:
            #    tmp = list(set(tmp))
            #    fout.write('{}\t'.format(line.strip()))
            #    fout.write('{}\n'.format(';'.join(tmp)))
            #else:
            #    fout.write('{}\t'.format(line.strip()))
            #    fout.write('{}\n'.format('null'))
    print >> sys.stderr, 'done'

def binDictListInFile(binlis, infile, outfile, keyIndex=0, startIndex=1, endIndex=2, delim = '\t', extend = 0):
    print >> sys.stderr, 'selecting file {} ...'.format(infile)
    with open(infile, "rU") as fin, open(outfile, 'w') as fout:
        for line in fin:
            t = line.strip().split(delim)
            namekey = t[keyIndex]
            start = int(t[startIndex]) - extend
            end = int(t[endIndex]) + extend
            tmp = []
            binkeys = reg2bins(start, end)
            for d in binlis:
                if namekey not in d:
                    tmp.append('null')
                    continue
                tmpin = []
                for binkey in binkeys:
                    if binkey not in d[namekey]: continue
                    binList = d[namekey][binkey]
                    #fout.write('{0[5]}\t{0[6]}\t{0[7]}\t{0[10]}\t{0[11]}\t{0[12]}\t'.format(t))
                    for i in binList:
                        if i.includeRegion(start, end):
                            tmpin.append('{0[3]}|{0[0]}:{0[1]}-{0[2]}|{0[7]}|full'.format(i.value))
                        #if i.overlapBase(start, end) > 0:
                        elif i.overlapFracTarget(start, end) >= 0.5:
                        #if i.inRegion(start, end):
                        #if i.includeRegion(start, end):
                            #tmpin.append('{}|{}|{}|{}'.format(i.chrom, i.start, i.end, i.name))
                            tmpin.append('{0[3]}|{0[0]}:{0[1]}-{0[2]}|{0[7]}|half'.format(i.value))
                            #tmp.append('{0[5]}|{0[6]}|{0[7]}|{0[10]}'.format(i.value))
                            #tmp.append('{0[1]}|{0[2]}|{0[3]}|{0[0]}'.format(i.value))
                            #tmp.append(i.value)
                if tmpin:
                    tmpin = list(set(tmpin))
                    tmp.append(','.join(tmpin))
                else:
                    tmp.append('null')
            fout.write('{}\t'.format(line.strip()))
            fout.write('{}\n'.format(';'.join(tmp)))
    print >> sys.stderr, 'done'

def regionOverlapbinDict(d, namekey, start, end):
    if namekey not in d: return False
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.overlapBase(start, end) > 0:
                return True
    return False

def regionOverlapbinDictWithFirstContent(d, namekey, start, end):
    if namekey not in d: return False
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.overlapBase(start, end) > 0:
                return i
    return False

def regionOverlapbinDictWithAllContents(d, namekey, start, end):
    lst = []
    if namekey not in d: return lst
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.overlapBase(start, end) > 0:
                lst.append(i)
    return lst

def regionIncludebinDict(d, namekey, start, end):
    if namekey not in d: return False,0
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.inRegion(start, end):
                return True, i.value
    return False,0

def regionIncludebinDictWithFirstContent(d, namekey, start, end):
    if namekey not in d: return False
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        #print >> sys.stderr, 'checking binkey',binkey
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.inRegion(start, end):
                return i
    return False

def regionIncludebinDictWithAllContents(d, namekey, start, end):
    lst = []
    if namekey not in d: return lst
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.inRegion(start, end):
                lst.append(i)
    return lst

def regionInbinDict(d, namekey, start, end):
    if namekey not in d: return False
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.includeRegion(start, end):
                return True
    return False

def regionInbinDictWithFirstContent(d, namekey, start, end):
    if namekey not in d: return False
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.includeRegion(start, end):
                #return '{}|{}|{}|{}'.format(i.chrom, i.start, i.end, i.name)
                return i
    return False

def regionInbinDictWithAllContents(d, namekey, start, end):
    res = []
    if namekey not in d: return res
    binkeys = reg2bins(start, end)
    for binkey in binkeys:
        if binkey not in d[namekey]: continue
        binList = d[namekey][binkey]
        for i in binList:
            if i.includeRegion(start, end):
                #return '{}|{}|{}|{}'.format(i.chrom, i.start, i.end, i.name)
                res.append(i)
    return res

def nearestbinDictElem(d, namekey, start):
    # work for 1bp region, aka position
    if namekey not in d: return None
    binkey = reg2bin(start, start+1)
    maxkey = max(d[namekey].keys())
    if binkey in d[namekey]:
        binList = d[namekey][binkey]
        #sorted_binList = sorted(binList, key=lambda x: x.start)
        #perform sort on original list would be better
        l = len(binList)
        sorted_startlis = [i.start for i in binList] # check if sort needed
        inx = bisect_left(sorted_startlis, start)
        if inx == 0:
            return binList[0]
        elif inx == l:
            return binList[-1]
        else:
            if binList[inx].start == start:
                return binList[inx]
            else:
                if abs(binList[inx].start - start) > abs(binList[inx-1].start - start):
                    return binList[inx-1]
                else:
                    return binList[inx]
    else:
        downkey = binkey - 1
        upkey = binkey + 1
        while downkey or upkey <= maxkey:
            if downkey in d[namekey]:
                if upkey not in d[namekey]:
                    return d[namekey][downkey][-1]
                else:
                    if abs(d[namekey][upkey][0].start - start) > abs(d[namekey][downkey][-1].start - start):
                        return d[namekey][downkey][-1]
                    else:
                        return d[namekey][upkey][0]
            else:
                if upkey in d[namekey]:
                    return d[namekey][upkey][0]
                else:
                    downkey -= 1
                    upkey += 1
    return None

def downstreambinDictElem(ld, namekey, start, strand):
    # work for 1bp region, aka position
    inGene = False
    elem = ''
    if strand == '+':
        d = ld[0]
    else:
        d = ld[1]
    if namekey not in d: return [elem, inGene]
    maxkey = max(d[namekey].keys())
    binkey = reg2bin(start, start+1)
    if binkey in d[namekey]:
        binList = d[namekey][binkey]
        l = len(binList)
        sorted_startlis = [i.start for i in binList] # check if sort needed
        inx = bisect_left(sorted_startlis, start)
        if inx == 0:
            if start == binList[0].start:
                inGene = True
                if strand == '+':
                    if l > 1:
                        elem = binList[1]
                    else:
                        elem = mostRightElemNextBin(d, namekey, binkey, maxkey)
                else:
                    elem = mostLeftElemNextBin(d, namekey, binkey)
            else:
                if strand == '+':
                    elem = binList[0]
                else:
                    elem = mostLeftElemNextBin(d, namekey, binkey)
        elif inx == l:
            if start < binList[-1].end:
                inGene = True
            if strand == '+':
                elem = mostRightElemNextBin(d, namekey, binkey, maxkey)
            else:
                if inGene:
                    if l > 1:
                        elem = binList[-2]
                    else:
                        elem = mostLeftElemNextBin(d, namekey, binkey)
                else:
                    elem = binList[-1]
        else:
            if start == binList[inx].start:
                inGene = True
                if strand == '+':
                    if inx < l-1:
                        elem = binList[inx+1]
                    else:
                        elem = mostRightElemNextBin(d, namekey, binkey, maxkey)
                else:
                    elem = binList[inx-1]
            else:
                if start < binList[inx-1].end:
                    inGene = True
                if strand == '+':
                    elem = binList[inx]
                else:
                    if inGene:
                        if inx >= 2:
                            elem = binList[inx-2]
                        else:
                            elem = mostLeftElemNextBin(d, namekey, binkey)
                    else:
                        elem = binList[inx-1]
    else:
        if strand == '+':
            elem = mostRightElemNextBin(d, namekey, binkey, maxkey)
        else:
            elem = mostLeftElemNextBin(d, namekey, binkey)
    return [elem, inGene]

def downstreambinDictElem2(ld, namekey, start, end, strand):
    # work for 1bp region, aka position
    # difference with function above:
    # if a tss in gene, return this gene, not the gene downstream of this gene
    # a range limit added, require the gene start should less than the 3'end of so called hybrid reads
    #instead of using limit, use start and end coordinates
    inGene = False
    elem = ''
    if strand == '+':
        d = ld[0]
    else:
        d = ld[1]
    if namekey not in d: return [elem, inGene]
    binkey = reg2bin(start, end)
    if binkey in d[namekey]:
        binList = d[namekey][binkey]
        l = len(binList)
        if strand == '+':
            sorted_startlis = [i.start for i in binList] # check if sort needed
            inx = bisect_left(sorted_startlis, start)
        else:
            sorted_startlis = [i.end for i in binList] # check if sort needed
            inx = bisect_left(sorted_startlis, end)
        if inx == 0:
            if strand == '+':
                if start == sorted_startlis[0]:
                    inGene = True
                    elem = binList[0]
                else:
                    if binList[0].start <= end:
                        elem = binList[0]
            else:
                if end == sorted_startlis[0]:
                    inGene = True
                    elem = binList[0]
                else:
                    if binList[0].start <= end:
                        inGene = True
                        elem = binList[0]
        elif inx == l:
            if strand == '+':
                if start < binList[-1].end:
                    inGene = True
                    elem = binList[-1]
            else:
                if start < binList[-1].end:
                    elem = binList[-1]
        else:
            if strand == '+':
                if start == binList[inx].start:
                    inGene = True
                    elem = binList[inx]
                elif start < binList[inx-1].end:
                    inGene = True
                    elem = binList[inx-1]
                else:
                    if end > binList[inx].start:
                        elem = binList[inx]
            else:
                if end == binList[inx].end:
                    inGene = True
                    elem = binList[inx]
                elif start >= binList[inx].start:
                    inGene = True
                    elem = binList[inx]
                else:
                    if start < binList[inx-1].end:
                        elem = binList[inx-1]
    return [elem, inGene]

def mostLeftElemNextBin(d, namekey, binkey):
    key = binkey - 1
    while key:
        if key in d[namekey]:
            return d[namekey][key][-1]
        key -= 1
    return None

def mostRightElemNextBin(d, namekey, binkey, maxkey):
    key = binkey + 1
    while key <= maxkey:
        if key in d[namekey]:
            return d[namekey][key][0]
        key += 1
    return None


def main():
    pass
    


if __name__=="__main__":
    main()

