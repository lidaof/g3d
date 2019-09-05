const fs = require('fs');
const jpickle = require('jpickle');

fs.open('test.dat', 'r', (err, fd) => {
    const buffer = Buffer.alloc(100);
    fs.read(fd, buffer, 0, 100, 0, (err, buf) => {
        console.log(buf);
        const data = jpickle.loads(buf)
        console.log(data)
    })
    
})