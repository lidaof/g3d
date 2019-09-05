const NodeLocalFile = require("./io/nodeLocalFile");
const jpickle = require('jpickle');

readHeader = async () => {
    const path = require.resolve('../gm.g3d');
    const file = new NodeLocalFile({path});
    console.log(file)
    const arrayBuffer = await file.read(0, 64000);
    console.log(buf2hex(arrayBuffer))
    const data = new DataView(arrayBuffer);
    console.log(data);
    const header = jpickle.loads(buf2hex(arrayBuffer));
    console.log(header)
    return header;
}


readHeader().then(res => console.log(res));
