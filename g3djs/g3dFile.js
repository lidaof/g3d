const zlib = require('zlib');
const _ = require('lodash');
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
        this.offsets = {};

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
        const offsets = header.offsets; // offset
        
        // Meta data for the g3d file
        this.meta = {
            magic,
            genome,
            version,
            resolutions,
            sample,
        };

        this.offsets = {...offsets};

    }

    async readData(chrom, start, end) {
        await this.init();
        const offset = this.offsets[chrom];
        if(!offset) {
            return null;
        }
        const binkeys = binning.reg2bins(start, end);
        const promises = binkeys.map(async binkey => {
            const container = this.offsets[chrom][binkey.toString()]; // JS object key can only be string
            if (container) {
                const {offset, size} = container;
                const response = await this.file.read(offset, size);
                if(response) {
                    const buffer = Buffer.from(response);
                    const unzipped = await unzip(buffer);
                    return jpickle.loads(unzipped.toString('binary'));
                }
            }
        });
        const data = await Promise.all(promises);
        const filtered = _.flatten(data.filter(x=>x)).map(x => x.split(' '));
        return filtered;
    }
}

module.exports = G3dFile;
