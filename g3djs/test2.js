const fs = require('fs');
const jpickle = require('jpickle');

const readStream = fs.createReadStream('../gm.g3d', {start: 0, end: 64000});
let meta;
readStream.on('data', data => meta = jpickle.loads(data.toString('binary')));
console.log(meta);