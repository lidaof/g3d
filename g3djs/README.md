# g3djs

Javascript API for reading .g3d genome structure files.

## Installation

Requires [Node](https://nodejs.org)

```bash
npm install g3djs
```

## Examples

```js

    import g3djs from 'g3djs'

    const url = "https://wangftp.wustl.edu/~dli/tmp/GSM3271347_gm12878_01.impute3.round4.clean.g3d"
    const file = new G3dFile({url})
    file.readHeader()
        .then(() => console.log(file.meta))

```
