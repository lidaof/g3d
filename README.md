# g3dtools

A tool for operating .g3d (genome 3D structure) format.

Require: Python 3 and above. (Note: not work with Python 2)

example input

columns are:
* chromosome
* start position
* end position
* X
* Y
* Z
* haplotype, m for maternal, p for paternal, . for unknown


python g3dtools.py dump test -g hg19 -s GM12878 -o GM12878_chr1_chr2


python g3dtools.py 3dg test/GSM3271347_gm12878_01.impute3.round4.clean.3dg.txt.gz -o testOut/GSM3271347

