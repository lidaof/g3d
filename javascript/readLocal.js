const fs = require('fs');
const jpickle = require('jpickle');

binary = fs.readFileSync('../gm.g3d');
const headerpkl = binary.slice(0, 1000);
console.log(headerpkl);
const meta = headerpkl.map(encodehex).join('');
console.log(meta);
process.stdout.write(jpickle.loads(meta));


function encodehex (val) {
    if ((32 <= val) && (val <= 126))
      return String.fromCharCode(val);
    else
      return "\\x"+val.toString(16);
  }