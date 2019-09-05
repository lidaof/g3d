const fs = require('fs');
const jpickle = require('jpickle');

const binary = fs.readFileSync('../gm.g3d', "binary");
const headerpkl = binary.slice(0, 1000);
console.log(headerpkl);
process.stdout.write(jpickle.loads(binary));
