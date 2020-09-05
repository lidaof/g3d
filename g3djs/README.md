# g3djs

Javascript API for reading .g3d genomic 3D structure files.

## Installation

Requires [Node](https://nodejs.org).

```bash
npm install g3djs
```

## Examples

```js
import G3dFile from "g3djs";

const url = "https://target.wustl.edu/dli/tmp/test2.g3d";
const file = new G3dFile({ url });
// get metadata
// metadata contains information about genome assembly, dataset name, resolutions etc.
file.readHeader().then(() => console.log(file.meta));

// get 3D data from a specific resolution, 200k here for example
file.readData(200000).then((data) => console.log(data));
```

You can run `npm run test` see the stucture of the returned data.
