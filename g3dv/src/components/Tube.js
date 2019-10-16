import * as BABYLON from 'babylonjs'
// import { deconstructMesh } from '@/helper'
/**
 * this component renders a 3D tube given the data3d array data
 */

export function renderTubeToScene(data, scene) {
  console.log('render tube...')
  if (!data.length) {
    console.error('error: data for tube is empty')
    return
  }
  const pointArray = data.map(
    item => new BABYLON.Vector3(item[3], item[4], item[5])
  )
  console.log(pointArray.length)
  const catmullRom = BABYLON.Curve3.CreateCatmullRomSpline(pointArray, 6, false)
  const path = catmullRom.getPoints()
  console.log(path.length)
  const chromosome = BABYLON.TubeBuilder.CreateTube(
    'chromosome',
    {
      path,
      radius: 0.1,
      cap: BABYLON.Mesh.CAP_ALL
    },
    scene
  )

  const material = new BABYLON.StandardMaterial('material', scene)
  material.diffuseColor = new BABYLON.Color4(1, 0, 0, 0.7)
  chromosome.material = material

  // chromosome.subdivide(pointArray.length)
  // // console.log(chromosome.subMeshes, chromosome.subdivide(pointArray.length));

  // const chromosomeSegments = deconstructMesh(chromosome)

  // /**
  //  * Color non-duplication relies on knowing colors of all the segments
  //  * @type {MeshColorPair[]}
  //  */
  // const returnSegments = []

  // chromosomeSegments.forEach((mesh, index) => {
  //   let color, rand
  //   rand = Math.random()
  //   if (rand < 0.25) {
  //     color = new BABYLON.Color4(1, 1, 1, 0.7)
  //   } else if (rand >= 0.25 && rand < 0.5) {
  //     color = new BABYLON.Color4(1, 0, 0, 1)
  //   } else if (rand >= 0.5 && rand < 0.75) {
  //     color = new BABYLON.Color4(0, 1, 0, 1)
  //   } else {
  //     color = new BABYLON.Color4(1, 1, 0, 1)
  //   }

  //   const materialColor = new BABYLON.StandardMaterial('materialcolor', scene)
  //   materialColor.diffuseColor = color
  //   materialColor.computeHighLevel = true
  //   mesh.material = materialColor
  //   returnSegments.push({
  //     segment: mesh,
  //     color: color,
  //     vector: pointArray[index]
  //   })
  // })

  // chromosome.dispose()

  // return returnSegments
}
