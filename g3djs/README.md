# g3djs

Javascript API for reading .g3d genome structure files.

## Installation

Requires [Node](https://nodejs.org)

```bash
npm install g3djs
```

## Examples

```js

    import G3dFile from 'g3djs'

    const url = "https://wangftp.wustl.edu/~dli/tmp/GSM3271347_gm12878_01.impute3.round4.clean.g3d"
    const file = new G3dFile({url})
    // get metadata
    // metadata contains information about genome assembly, dataset name, resolutions etc.
    file.readHeader()
        .then(() => console.log(file.meta))

    // get 3D data from a specific region, under a specific resolution
    // parameters: chrom, start, end, resulution size
    file.readData('chr7',27053397, 27373765, 20000).then(data => console.log(data));

    // get data for a chromsome, 200000 is the resolution
    file.readDataChromosome('chr7', 200000).then(data => console.log(data));

    // get data for the genome, 200000 is the resolution
    file.readDataGenome(200000).then(data => console.log(data));

```
