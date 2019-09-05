const util = require('util')

// don't load fs native module if running in webpacked code
const fs = typeof __webpack_require__ !== 'function' ? require('fs') : null // eslint-disable-line camelcase
const fsOpen = fs && util.promisify(fs.open)
const fsRead = fs && util.promisify(fs.read)
const fsFStat = fs && util.promisify(fs.stat)
const fsReadFile = fs && util.promisify(fs.readFile)

class NodeLocalFile {

    constructor(args) {
        this.path = args.path
    }


    async read(position, length) {

        const buffer = Buffer.alloc(length)
        const fd = await fsOpen(this.path, 'r')
        const result = await fsRead(fd, buffer, 0, length, position)

       fs.close(fd, function (error) {
           // TODO Do something with error
       })

        //TODO -- compare result.bytesRead with length
        const arrayBuffer = result.buffer.buffer;
        return arrayBuffer
    }
}

module.exports = NodeLocalFile
