# g3dtools

A tool for operating .g3d (genome 3D structure) format, for more information please check [documentation](https://g3d.readthedocs.io/en/latest/g3dtools.html).

Require: Python (Recommend version 3 and above).

example input, 6 columns bed-like text file (6th column is optional):

```bash
chr7    16760000     -14.3866688728  -36.3919302029  19.8483965881   m
chr7    16760000     -24.9116268071  50.0521268287   9.91073185128   p
chr7    25160000     -10.1170055526  -34.8975763469  20.2401719179   m
chr7    25160000     -21.8210915649  27.1128556621   13.4856945965   p
chr7    33540000     -4.11059384846  -54.4940083464  4.21321135564   m
chr7    33540000     -12.0040359857  31.5960497183   26.6925954134   p
chr7    41940000     5.75342635105   -55.4976428728  8.65307697332   m
chr7    41940000     -23.7372022413  36.0614692267   31.919119243    p
chr7    50320000     -10.7099779927  -38.0214001171  25.8308473821   m
chr7    50320000     -28.5142098162  26.6468499001   28.8634805533   p
chr7    26200000     -11.5800097945  -37.9903257744  16.2461100893   m
chr7    26200000     -15.9552426623  27.016940724    17.5722080595   p
chr7    27260000     -14.1883124179  -44.7860807973  12.4104162757   m
chr7    27260000     -20.0857754297  30.9204143041   18.4774635708   p
chr7    28300000     -18.0160836669  -39.398544495   12.811858164    m
chr7    28300000     -14.9383020843  39.1464516779   17.3743509519   p
chr7    29360000     -11.8032470923  -47.3595095319  13.2828128833   m
chr7    29360000     -12.2445277916  41.2431968179   14.8844908717   p
chr7    30400000     -12.8674349856  -45.0752589744  9.15498568359   m
```

columns are:

-   chromosome
-   start position
-   X (coordinates in 3D)
-   Y
-   Z
-   category (optional), usually haplotype or cell/sample type, or time point information can be used, like for haplotype, `m` for `maternal`, `p` for `paternal`, `s` for `shared`, if omitted, `shared` will be used, or user can choose `cell-1`, `cell-2` etc. for cell identifier...

This file input looks simiar to [3dg format](https://github.com/tanlongzhi/dip-c#3dg) except we put haplotype or category info on last column.

## Generate a new .g3d file using the format listed above

```console
g3dtools load ../test/test.g3d.bed.gz -o ../testOut/test -s 2,3,4,5,6,7,8,9,10 -n GM12878 -g hg19
```

## Generate a new .g3d file from .3dg format

Input a file with high resolution, let the tool calculate lower resolutions:

```console
g3dtools 3dg ../test/GSM3271347_gm12878_01.impute3.round4.clean.3dg.txt.gz -o ../testOut/GSM3271347_gm12878_01.impute3.round4.clean -n GM12878 -g hg19 -s 2,3,4,5,6,7,8,9,10
```

or prepare different resolution files in advance.

## Generate a new .g3d file from PASTIS output

User can also generate .g3d file from [pastis](http://projets.cbio.mines-paristech.fr/~nvaroquaux/pastis/) output.

```console
g3dtools pastis -g Pfal3D7 -n Rings -o ../testOut/rings ../test/RINGS.3D_coord.txt
```

```console
g3dtools pastis-pdb  -g Pfal3D7 -n Rings -o ../testOut/rings_pdb -s 2,3,4,5,6 ~/Downloads/RINGS.pdb
```

## Generate a new .g3d from nucle3d format

User can also generate .g3d file from [nucle3d](https://github.com/nucleome/nucle3d) format.

```console
g3dtools nucle3d -n k562 -g hg38 -o ../testOut/k562 ../test/K562.nucle3d
```

## Query

By region:

```console
g3dtools query testOut/test.g3d -c chr7 -s 27053397 -e 27373765
```

change haplotype (or category):

```console
g3dtools query -c chr7 -s 500000 -e 50000000 -y paternal ../testOut/test2.g3d > x
```

change resolution:

```console
g3dtools query testOut/test.g3d -c chr7 -s 27053397 -e 27373765 -r 100000
```

when resolution not exists:

```console
$ g3dtools query testOut/test.g3d -c chr7 -s 27053397 -e 27373765 -r 130000
[Query] Error, resolution 130000 not exists for this file,
available resolutions: [20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000]
```

## Get metadata information

```console
g3dtools meta testOut/test2.g3d
{
    "version": 2,
    "genome": "hg19",
    "name": "GM12878",
    "resolutions": [
        20000,
        40000,
        60000,
        80000,
        100000,
        120000,
        140000,
        160000,
        180000,
        200000
    ],
    "categories": [
        "maternal",
        "paternal"
    ]
}
```

## Troubeshooting

### RecursionError: maximum recursion depth exceeded in comparison

This error happens is the resolution of the input file is not the default 20000, you would need specify the `-r` parameter. Somehow resolution checking is not working as the bins are not always continuous.
