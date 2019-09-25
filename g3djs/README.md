# g3djs

Javascript API for reading .g3d genome structure files.

## Installation

Requires Node (https://nodejs.org)

```
npm install g3djs
```

## Examples

```js

    import g3djs from 'g3djs'

    const url = "https://wangftp.wustl.edu/~dli/test/GM12878_chr1_chr2.g3d"
    const file = new G3dFile({url})
    file.readHeader()
        .then(() => console.log(file.meta))

```
