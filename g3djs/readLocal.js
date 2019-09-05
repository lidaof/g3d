const fs = require('fs');
const jpickle = require('jpickle');

// const binary = fs.readFileSync('../gm.g3d', "binary");
// const headerpkl = binary.slice(0, 1000);
// console.log(headerpkl);
// process.stdout.write(jpickle.loads(binary));

fs.open('../gm.g3d', 'r', function(status, fd) {
    if (status) {
        console.log(status.message);
        return;
    }
    var buffer = new Buffer(1000);
    fs.read(fd, buffer, 3, 4, 0, function(err, num) {
        console.log(jpickle.loads(buffer));
    });
});