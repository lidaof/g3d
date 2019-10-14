import * as BABYLON from 'babylonjs'

export function deconstructMesh(mesh, scene) {
  if (mesh.subMeshes.length > 1) {
    var otherVertexData = BABYLON.VertexData.ExtractFromMesh(mesh, true, true)
    var indices = otherVertexData.indices
    var normals = otherVertexData.normals
    var positions = otherVertexData.positions
    var uvs = otherVertexData.uvs
    var newMeshArray = []
    for (var index = 0; index < mesh.subMeshes.length; index++) {
      var newVertexData = new BABYLON.VertexData()

      var newI = indices.slice(
        mesh.subMeshes[index].indexStart,
        mesh.subMeshes[index].indexStart + mesh.subMeshes[index].indexCount
      )
      var newN = normals.slice(
        mesh.subMeshes[index].verticesStart * 3,
        mesh.subMeshes[index].verticesStart * 3 +
          mesh.subMeshes[index].verticesCount * 3
      )
      var newP = positions.slice(
        mesh.subMeshes[index].verticesStart * 3,
        mesh.subMeshes[index].verticesStart * 3 +
          mesh.subMeshes[index].verticesCount * 3
      )
      var newU = uvs.slice(
        mesh.subMeshes[index].verticesStart * 2,
        mesh.subMeshes[index].verticesStart * 2 +
          mesh.subMeshes[index].verticesCount * 2
      )
      for (var subIndex = 0; subIndex < newI.length; subIndex++) {
        newI[subIndex] = newI[subIndex] - mesh.subMeshes[index].verticesStart
      }

      newVertexData.indices = newI
      newVertexData.normals = newN
      newVertexData.positions = newP
      newVertexData.uvs = newU

      var meshSubclass = new BABYLON.Mesh(mesh.name + '-' + index, scene)

      newVertexData.applyToMesh(meshSubclass)

      newMeshArray.push(meshSubclass)
    }
    return newMeshArray
  } else {
    return [mesh]
  }
}

/**
 * parse user input region string using regular expression
 * format should be like chr1:1-100, can be separated by space, etc.
 * comma in start and end is allowed
 * @param {string} str
 * @return {object} an object with chr, start and end as key, or an object with error as key
 */
export function parseRegionString(str) {
  const regexMatch = str.replace(/,/g, '').match(/([\w:]+)\W+(\d+)\W+(\d+)/)
  if (regexMatch) {
    const chr = regexMatch[1]
    const start = Number.parseInt(regexMatch[2], 10)
    const end = Number.parseInt(regexMatch[3], 10)
    return { chr, start, end }
  } else {
    return { error: 'could not parse region string' }
  }
}

/**
 * Returns a copy of the input list, ensuring its length is below `limit`.  If the list is too long, selects
 * equally-spaced elements from the original list.  Note that if the input is sorted, the output will be sorted as well.
 *
 * @param {[]} list - list for which to ensure a max length
 * @param {number} limit - maximum length of the result list
 * @return {[]} copy of list with max length ensured
 */
export function ensureMaxListLength(list, limit) {
  if (list.length <= limit) {
    return list
  }

  const selectedItems = []
  for (let i = 0; i < limit; i++) {
    const fractionIterated = i / limit
    const selectedIndex = Math.ceil(fractionIterated * list.length)
    selectedItems.push(list[selectedIndex])
  }
  return selectedItems
}
