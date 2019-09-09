const {assert} = require('chai')
const G3dFile = require('../g3dFile');

suite('RemoteG3dFile', function () {
    test('test read header', async function () {
        const url = "https://wangftp.wustl.edu/~dli/test/GM12878_chr1_chr2.g3d"
        const file = new G3dFile({url})
        const header = await file.readHeader();
        assert.ok(header);
        assert.equal(header.magic, 'G3D');
    })

})
