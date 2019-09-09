const zlib = require('zlib');
const BrowserLocalFile = require('./io/browserLocalFile');
const RemoteFile = require('./io/remoteFile');
const jpickle = require('jpickle');

const HEADER_SIZE = 64000; // header size of 64000

class G3dFile {
    constructor(config) {
        this.config = config;
        this.meta = {};

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

    async init() {
        if (this.initialized) {
            return;
        } else {
            await this.readHeader();
            this.initialized = true;
        }
    }

    async getMetaData() {
        await this.init();
        return this.meta;
    }

    async readHeader() {

        const response = await this.file.read(0, HEADER_SIZE);

        if (!response) {
            return undefined;
        }

        const buffer = Buffer.from(response);
        const header = jpickle.loads(buffer.toString('binary'));
        const magic = header.magic;
        const genome = header.genome;
        const version = header.version;
        const sample = header.sample;
        const offsets = header.offsets;
        
        // Meta data for the g3d file
        this.meta = {
            magic,
            genome,
            version,
            sample,
            offsets,
        }
    }

    async readData(chrom) {
        const offset = this.meta.offsets[chrom];
        if(!offset) {
            return null;
        }
        let data;
        const response = this.file.read(offset.offset, offset.size);
        if(!response) {
            return null;
        }
        const buffer = Buffer.from(response);
        zlib.unzip(buffer, (err, buffer) => {
            if (!err) {
                data = jpickle.loads(buffer.toString('binary'));
            } else {
                // handle error
            }
        });
        return data;
    }
}

module.exports = G3dFile;
