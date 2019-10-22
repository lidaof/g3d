/**
 * help functions for g3dv
 * @author Daofeng Li
 */

/**
 * clear objects of a Three scene
 * from https://stackoverflow.com/questions/30359830/how-do-i-clear-three-js-scene/48722282
 *
 * @param {ThreeScene obj} scene
 */
export function clearScene(scene) {
  while (scene.children.length > 0) {
    scene.remove(scene.children[0])
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
