const zlib = require('zlib');
const _ = require('lodash');
const BrowserLocalFile = require('./io/browserLocalFile');
const RemoteFile = require('./io/remoteFile');
// const jpickle = require('jpickle');
const util = require('util');
const msgpack = require('@msgpack/msgpack');

const binning = require('./utils/binning');

const unzip = util.promisify(zlib.unzip);

const HEADER_SIZE = 1024;

class G3dFile {
    constructor(config) {
        this.config = config;
        this.meta = null;
        this.offsets = null;

        if(config.blob) {
            this.file = new BrowserLocalFile(config.blob);
        } else {
            this.url = config.url;
            if (this.url.startsWith("http://") || this.url.startsWith("https://")) {
                this.remote = true
                const remoteFile = new RemoteFile(config);
                this.file = remoteFile;
            } else {
                throw Error("Arguments must include blob, or url")
            }
        }
    }

    async initHeader() {
        if (this.headerReady) {
            return;
        } else {
            await this.readHeader();
            this.headerReady = true;
        }
    }

    async initFooter() {
        if (this.footerReady) {
            return;
        } else {
            await this.readFooter();
            this.footerReady = true;
        }
    }

    async getMetaData() {
        await this.initHeader();
        return this.meta;
    }

    async readHeader() {

        const response = await this.file.read(0, HEADER_SIZE);

        if (!response) {
            return undefined;
        }
        // console.log(response)

        const buffer = Buffer.from(response);
        // const header = jpickle.loads(buffer.toString('binary'));
        const size = this.getPackSize(buffer);
        const newBuffer = buffer.slice(0, size);
        // console.log(size)
        const header = msgpack.decode(newBuffer);
        // console.log(header)
        const magic = header.magic;
        const genome = header.genome;
        const version = header.version;
        const resolutions = header.resolutions;
        const name = header.name;
        const index_offset = header.index_offset;
        const index_size = header.index_size;
        
        // Meta data for the g3d file
        this.meta = {
            magic,
            genome,
            version,
            resolutions,
            name,
            index_offset,
            index_size,
        };
    }

    getPackSize(buffer) {
        let i = buffer.length;
        for(; i--; i>=0) {
            if (buffer[i] !== 0x00) {
                return i+1;
            }
        }
        return i;
    }

    async readFooter() {
        await this.initHeader();
        const {index_offset, index_size} = this.meta;
        const response = await this.file.read(index_offset, index_size);

        if (!response) {
            return undefined;
        }

        const buffer = Buffer.from(response);
        const unzipped = await unzip(buffer);
        // const footer = jpickle.loads(unzipped.toString('binary'));
        const footer = msgpack.decode(unzipped);
        this.offsets = {...footer};
    }

    async readData(chrom, start, end, resolution=20000) {
        await this.initHeader();
        await this.initFooter();
        const resdata = this.offsets[resolution];
        if(!resdata) {
            return null;
        }
        const offset = resdata[chrom];
        if(!offset) {
            return null;
        }
        const binkeys = binning.reg2bins(start, end);
        const promises = binkeys.map(async binkey => {
            const container = resdata[chrom][binkey.toString()]; // JS object key can only be string
            if (container) {
                const {offset, size} = container;
                const response = await this.file.read(offset, size);
                if(response) {
                    const buffer = Buffer.from(response);
                    const unzipped = await unzip(buffer);
                    // return jpickle.loads(unzipped.toString('binary'));
                    return msgpack.decode(unzipped);
                }
            }
        });
        const data = await Promise.all(promises);
        const filtered = _.flatten(data.filter(x=>x)); //.map(x => x.split('\t'));
        return filtered;
    }
}

module.exports = G3dFile;
