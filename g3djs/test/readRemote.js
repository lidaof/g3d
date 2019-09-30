const {assert} = require('chai')
const G3dFile = require('../g3dFile');

suite('RemoteG3dFile', function () {
    test('test read header', async function () {
        const url = "https://wangftp.wustl.edu/~dli/tmp/GSM3271347_gm12878_01.impute3.round4.clean.g3d"
        const file = new G3dFile({url})
        await file.readHeader();
        // console.log(file.meta)
        assert.ok(file.meta);
        assert.equal(file.meta.magic, 'G3D');
    })

    test('test read data for region', async function () {
        const url = "https://wangftp.wustl.edu/~dli/tmp/GSM3271347_gm12878_01.impute3.round4.clean.g3d"
        const file = new G3dFile({url})
        await file.readHeader();
        const data = await file.readData('chr7',27053397, 27373765, 20000);
        // console.log(data)
        assert.ok(data);
    })


})
