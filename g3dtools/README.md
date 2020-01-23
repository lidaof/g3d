# g3dtools

A tool for operating .g3d (genome 3D structure) format.

Require: Python (Recommend version 3 and above).

example input, 6 columns bed-like text file:

```bash
chr7    16760000        16780000        -14.3866688728  -36.3919302029  19.8483965881   m
chr7    16760000        16780000        -24.9116268071  50.0521268287   9.91073185128   p
chr7    25160000        25180000        -10.1170055526  -34.8975763469  20.2401719179   m
chr7    25160000        25180000        -21.8210915649  27.1128556621   13.4856945965   p
chr7    33540000        33560000        -4.11059384846  -54.4940083464  4.21321135564   m
chr7    33540000        33560000        -12.0040359857  31.5960497183   26.6925954134   p
chr7    41940000        41960000        5.75342635105   -55.4976428728  8.65307697332   m
chr7    41940000        41960000        -23.7372022413  36.0614692267   31.919119243    p
chr7    50320000        50340000        -10.7099779927  -38.0214001171  25.8308473821   m
chr7    50320000        50340000        -28.5142098162  26.6468499001   28.8634805533   p
chr7    26200000        26220000        -11.5800097945  -37.9903257744  16.2461100893   m
chr7    26200000        26220000        -15.9552426623  27.016940724    17.5722080595   p
chr7    27260000        27280000        -14.1883124179  -44.7860807973  12.4104162757   m
chr7    27260000        27280000        -20.0857754297  30.9204143041   18.4774635708   p
chr7    28300000        28320000        -18.0160836669  -39.398544495   12.811858164    m
chr7    28300000        28320000        -14.9383020843  39.1464516779   17.3743509519   p
chr7    29360000        29380000        -11.8032470923  -47.3595095319  13.2828128833   m
chr7    29360000        29380000        -12.2445277916  41.2431968179   14.8844908717   p
chr7    30400000        30420000        -12.8674349856  -45.0752589744  9.15498568359   m
```

columns are:

-   chromosome
-   start position
-   end position
-   X (coordinates in 3D)
-   Y
-   Z
-   haplotype (optional), `m` for `maternal`, `p` for `paternal`, `s` for `shared`, if omitted, `s` will be used

## Generate a new .g3d file using the format listed above

```console
g3dtools load ../test/test.g3d.bed.gz -o ../testOut/test -s 2,3,4,5,6,7,8,9,10
```

## Generate a new .g3d file from .3dg format

Input a file with high resolution, let the tool calculate lower resolutions:

```console
g3dtools 3dg ../test/GSM3271347_gm12878_01.impute3.round4.clean.3dg.txt.gz -o ../testOut/GSM3271347_gm12878_01.impute3.round4.clean -s 2,3,4,5,6,7,8,9,10
```

or prepare different resolution files in advance.

## Generate a new .g3d file from PASTIS output

User can also generate .g3d file from [pastis](http://projets.cbio.mines-paristech.fr/~nvaroquaux/pastis/) output.

```console
g3dtools pastis -C chrX ../test/combined-WG-brain.1000000.alt.structure.3d.txt -o ../testOut/combined-WG-brain.1000000.alt.structure.3d
```

## Query

By region:

```console
g3dtools query testOut/test.g3d -c chr7 -s 27053397 -e 27373765
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
