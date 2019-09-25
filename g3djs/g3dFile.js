const zlib = require('zlib');
const BrowserLocalFile = require('./io/browserLocalFile');
const RemoteFile = require('./io/remoteFile');
const jpickle = require('jpickle');
const util = require('util');

const binning = require('./utils/binning');

const unzip = util.promisify(zlib.unzip);

const HEADER_SIZE = 512000; // header size of 512000

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
        const unzipped = await unzip(buffer);
        const header = jpickle.loads(unzipped.toString('binary'));
        const magic = header.magic;
        const genome = header.genome;
        const version = header.version;
        const resolutions = header.resolutions;
        const sample = header.sample;
        const offsets = header.offsets;
        
        // Meta data for the g3d file
        this.meta = {
            magic,
            genome,
            version,
            resolutions,
            sample,
            offsets,
        }
    }

    async readData(chrom, start, end) {
        await this.init();
        const offset = this.meta.offsets[chrom];
        if(!offset) {
            return null;
        }
        const binkeys = binning.reg2bins(start, end);
        const data = [];
        binkeys.forEach(binkey => {
            const container = this.meta.offsets[chrom][binkey];
            if (container) {
                const {offset, size} = container;
            }
        })
        const response = await this.file.read(offset.offset, offset.size);
        if(!response) {
            return null;
        }
        const buffer = Buffer.from(response);
        const unzipped = await unzip(buffer);
        return jpickle.loads(unzipped.toString('binary'));
    }
}

module.exports = G3dFile;
