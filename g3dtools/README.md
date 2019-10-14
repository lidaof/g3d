# g3dtools

A tool for operating .g3d (genome 3D structure) format.

Require: Python (Recommend version 3 and above).

example input

columns are:

-   chromosome
-   start position
-   end position
-   X
-   Y
-   Z
-   haplotype, m for maternal, p for paternal, . for unknown

## Generate a new .g3d file from .3dg format

Input a file with high resolution, let the tool calculate lower resolutions:

```console
$ g3dtools 3dg ../test/GSM3271347_gm12878_01.impute3.round4.clean.3dg.txt.gz -o ../testOut/GSM3271347_gm12878_01.impute3.round4.clean -s 2,3,4,5,6,7,8,9,10
```

or prepare different resolution files in advance:

## Query

By region:

```console
$ g3dtools query testOut/GSM3271347_gm12878_01.impute3.round4.clean.g3d -c chr7 -s 27053397 -e 27373765
```

change resolution:

```console
$ g3dtools query testOut/GSM3271347_gm12878_01.impute3.round4.clean.g3d -c chr7 -s 27053397 -e 27373765 -r 100000
```

when resolution not exists:

```console
$ g3dtools query testOut/GSM3271347_gm12878_01.impute3.round4.clean.g3d -c chr7 -s 27053397 -e 27373765 -r 130000
[Query] Error, resolution 130000 not exists for this file,
available resolutions: [20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000]
```
