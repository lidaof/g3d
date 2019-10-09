// const fs = require('fs');
// const jpickle = require('jpickle');

// const readStream = fs.createReadStream('../GM12878_chr1_chr2.g3d', {start: 0, end: 64000});
// let meta;
// readStream.on('data', data => meta = jpickle.loads(data.toString('binary')));
// console.log(meta);


const fs = require('fs');
const msgpack = require('@msgpack/msgpack');

const readStream = fs.createReadStream('/Users/dli/test.dat', {start: 0, end: 13});

test = async function (stream) {
    for await (const item of msgpack.decodeStream(stream)) {
        console.log(item);
      }
}

test(readStream)