// const jpickle = require('jpickle');
// const fs = require('fs');
// const zlib = require('zlib');

// fs.open('../GM12878_chr1_chr2.g3d', 'r', function(status, fd) {
//     if (status) {
//         console.log(status.message);
//         return;
//     }
//     var buffer = Buffer.alloc(64000);
//     fs.read(fd, buffer, 0, 64000, 0, (err, num) => {
//         console.log(jpickle.loads(buffer.toString('binary', 0, num)));
//     });
// });

// fs.open('../GM12878_chr1_chr2.g3d', 'r', function(status, fd) {
//     if (status) {
//         console.log(status.message);
//         return;
//     }
//     const buffer = Buffer.alloc(4881);
//     fs.read(fd, buffer, 0, 4881, 68697, (err, num) => {
//         zlib.unzip(buffer, (err, buffer) => {
//             if (!err) {
//               console.log(jpickle.loads(buffer.toString('binary')));
//             } else {
//               // handle error
//             }
//           });
//     });
// });
