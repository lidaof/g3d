import * as BABYLON from 'babylonjs'
import * as THREE from 'three'
import _ from 'lodash'
import iwanthue from 'iwanthue'
// import { deconstructMesh } from '@/helper'
/**
 * this component renders a 3D tube given the data3d array data
 */

function reformatData(data) {
  const grouped = _.groupBy(data, x => x[6])
  const sorted = {}
  Object.keys(grouped).forEach(key => {
    const sort = grouped[key].sort(
      (a, b) => a[0].localeCompare(b[0]) || a[1] - b[1]
    )
    sorted[key] = sort
  })
  return sorted
}

export function renderTubeToScene(data, scene) {
  console.log('render tube...')
  if (!data.length) {
    console.error('error: data for tube is empty')
    return
  }
  const palette = iwanthue(data.length * 2)
  console.log(palette)
  data.forEach((dat, datIndex) => {
    const formatted = reformatData(dat.data)

    Object.keys(formatted).forEach((key, keyIndex) => {
      const tubeData = formatted[key]

      const pointArray = tubeData.map(
        item => new BABYLON.Vector3(item[3], item[4], item[5])
      )
      console.log(pointArray.length)
      const catmullRom = BABYLON.Curve3.CreateCatmullRomSpline(
        pointArray,
        6,
        false
      )
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
      material.diffuseColor = new BABYLON.Color3.FromHexString(
        palette[datIndex + keyIndex]
      )
      chromosome.material = material
    })
  })

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

export function renderTube(data, scene) {
  console.log('render tube...')
  if (!data.length) {
    console.error('error: data for tube is empty')
    return
  }
  // console.log(data, scene)
  // // create a geometry
  // const geometry = new THREE.BoxBufferGeometry(2, 2, 2)

  // // create a purple Standard material
  // const material = new THREE.MeshStandardMaterial({ color: 0x800080 })

  // // create a Mesh containing the geometry and material
  // const mesh = new THREE.Mesh(geometry, material)

  // // add the mesh to the scene object
  // scene.add(mesh)

  // axis
  const axes = new THREE.AxesHelper(20)
  scene.add(axes)

  const palette = iwanthue(data.length * 2)
  console.log(palette)
  data.forEach((dat, datIndex) => {
    const formatted = reformatData(dat.data)

    Object.keys(formatted).forEach((key, keyIndex) => {
      const tubeData = formatted[key]

      const pointArray = tubeData.map(
        item => new THREE.Vector3(item[3], item[4], item[5])
      )
      console.log(pointArray.length)
      const catmullRom = new THREE.CatmullRomCurve3(pointArray)
      const points = catmullRom.getPoints(500)
      console.log(points.length)
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      const material = new THREE.LineBasicMaterial({
        color: palette[datIndex + keyIndex]
      })
      // Create the final object to add to the scene
      const curveObject = new THREE.Line(geometry, material)
      scene.add(curveObject)
    })
  })

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
