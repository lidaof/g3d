# g3dtools

A tool for operating .g3d (genome 3D structure) format.

example input

columns are:
* chromosome
* start position
* end position
* X
* Y
* Z
* m for maternal, p for paternal, . for unknown


python g3dtools.py dump test -g hg19 -s GM12878 -o GM12878_chr1_chr2
