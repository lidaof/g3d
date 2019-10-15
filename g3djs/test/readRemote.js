const {assert} = require('chai')
const G3dFile = require('../g3dFile');

// const test_url = 'https://wangftp.wustl.edu/~dli/tmp/GSM3271347_gm12878_01.impute3.round4.clean.g3d'
const test_url = 'https://wangftp.wustl.edu/~dli/tmp/test.g3d'

suite('RemoteG3dFile', function () {
    test('test read header', async function () {
        const url = test_url
        const file = new G3dFile({url})
        await file.readHeader();
        console.log(file.meta)
        assert.ok(file.meta);
        assert.equal(file.meta.magic, 'G3D');
    })

    test('test read data for region', async function () {
        const url = test_url
        const file = new G3dFile({url})
        const data = await file.readData('chr7',27053397, 27373765, 20000);
        console.log(data)
        assert.ok(data);
    })

    test('test read data for chromsome', async function () {
        const url = test_url
        const file = new G3dFile({url})
        const data = await file.readDataChromosome('chr21', 200000);
        // console.log(data)
        assert.ok(data);
    })

    // test('test read data for genome', async function () {
    //     const url = test_url
    //     const file = new G3dFile({url})
    //     const data = await file.readDataGenome(200000);
    //     // console.log(data)
    //     assert.ok(data);
    // })


})
