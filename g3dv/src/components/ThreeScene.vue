<template>
  <div id="parentContainer">
    <div id="stats" ref="statsContainer"></div>
    <div id="gui-container" ref="guiContainer"></div>
    <div id="canvasContainer" ref="canvasContainer"></div>
  </div>
</template>

<script>
// import Vue from 'vue'
import { mapState } from 'vuex'
import * as THREE from 'three'
import OrbitControls from 'three-orbitcontrols'
import {
  CSS2DRenderer,
  CSS2DObject
} from 'three/examples/jsm/renderers/CSS2DRenderer.js'
import Stats from 'stats-js'
import * as dat from 'dat.gui'
import html2canvas from 'html2canvas'
import {
  getSplines,
  getBallMesh,
  getTubeMesh,
  getLineMesh
} from '@/components/Tube'
// import { clearScene } from '@/helper'

const initializeDomEvents = require('threex-domevents')
const THREEx = {}
initializeDomEvents(THREE, THREEx)

// const THREEx = window.THREEx

/**
 * this calss is from https://threejsfundamentals.org/threejs/lessons/threejs-picking.html
 */
// class PickHelper {
//   constructor() {
//     this.raycaster = new THREE.Raycaster()
//     this.pickedObject = null
//   }
//   pick(normalizedPosition, pickTargets, camera) {
//     // restore the color if there is a picked object
//     if (this.pickedObject) {
//       this.pickedObject.scale.set(1, 1, 1)
//       this.pickedObject = undefined
//     }

//     // cast a ray through the frustum
//     this.raycaster.setFromCamera(normalizedPosition, camera)
//     // get the list of objects the ray intersected
//     const intersectedObjects = this.raycaster.intersectObjects(pickTargets)
//     if (intersectedObjects.length) {
//       // pick the first object. It's the closest one
//       this.pickedObject = intersectedObjects[0].object
//       // save its color
//       console.log(this.pickedObject)
//       this.pickedObject.scale.set(1.1, 1.1, 1.1)
//     }
//   }
// }

export default {
  name: 'ThreeScene',
  data() {
    return {
      canvas: null,
      scene: null,
      container: null,
      camera: null,
      renderer: null,
      controls: null,
      stats: null,
      gui: null,
      splines: null, // key, chr or region, mat or pat, value, {spine: spline object in Three, color: color}
      mesh: null, //single model mode
      meshes: {}, // all models mode, key: region, value: Mesh obj
      binormal: new THREE.Vector3(),
      normal: new THREE.Vector3(),
      parent: null,
      splineCamera: null,
      cameraHelper: null,
      cameraEye: null,
      meshGeometry: null,
      meshMaterial: null,
      labelRenderer: null,
      labelControls: null,
      // pickPosition: { x: 0, y: 0 },
      // pickHelper: new PickHelper(),
      domEvents: null,
      selectedMesh: null,
      params: {
        region: '',
        shape: 'line',
        lineWidth: 1,
        color: '',
        animationView: false,
        lookAhead: false,
        cameraHelper: false,
        scale: 1,
        speed: 1,
        sceneColor: 0x00000,
        screenshot: null,
        showAll: false,
        displayLabels: true
      }
    }
  },
  computed: mapState(['g3d', 'data3d']),
  methods: {
    init() {
      this.container = this.$refs.canvasContainer
      this.scene = new THREE.Scene()
      //   this.scene.background = new THREE.Color(0x8fbcd4)
      // this.scene.background = new THREE.Color(0xf0f0f0)
      const axes = new THREE.AxesHelper(50)
      this.scene.add(axes)
      this.stats = new Stats()
      this.stats.showPanel(0)
      this.stats.dom.style.position = 'absolute'
      this.$refs.statsContainer.appendChild(this.stats.dom)
      // const light = new THREE.DirectionalLight(0xffffff)
      // light.position.set(0, 0, 1)
      // this.scene.add(light)
      this.parent = new THREE.Object3D()
      this.scene.add(this.parent)
      this.createCamera()
      this.createControls()
      this.createLights()
      this.createRenderer()
      // start the animation loop
      this.renderer.setAnimationLoop(() => {
        this.update()
        this.render()
      })
    },
    createCamera() {
      const containerWidth = this.container.clientWidth
      const containerHeight = this.container.clientHeight
      const aspect = containerWidth / containerHeight
      this.camera = new THREE.PerspectiveCamera(
        50, // FOV
        aspect, // aspect
        0.1, // near clipping plane
        10000 // far clipping plane
      )

      this.camera.position.set(0, 50, 200)

      this.splineCamera = new THREE.PerspectiveCamera(84, aspect, 0.01, 1000)
      this.parent.add(this.splineCamera)

      this.cameraHelper = new THREE.CameraHelper(this.splineCamera)
      this.scene.add(this.cameraHelper)

      this.cameraEye = new THREE.Mesh(
        new THREE.SphereBufferGeometry(1),
        new THREE.MeshBasicMaterial({ color: 0xdddddd })
      )
      this.parent.add(this.cameraEye)

      this.cameraHelper.visible = this.params.cameraHelper
      this.cameraEye.visible = this.params.cameraHelper
    },
    createControls() {
      this.controls = new OrbitControls(this.camera, this.container)
    },
    createLights() {
      const ambientLight = new THREE.HemisphereLight(
        0xddeeff, // sky color
        0x202020, // ground color
        8 // intensity
      )

      const mainLight = new THREE.DirectionalLight(0xffffff, 5)
      mainLight.position.set(10, 10, 10)

      this.scene.add(ambientLight, mainLight)
    },
    createRenderer() {
      this.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.renderer.setSize(
        this.container.clientWidth,
        this.container.clientHeight
      )

      this.renderer.setPixelRatio(window.devicePixelRatio)
      this.container.appendChild(this.renderer.domElement)

      // label renderer
      this.labelRenderer = new CSS2DRenderer()
      this.labelRenderer.setSize(
        this.container.clientWidth,
        this.container.clientHeight
      )
      this.labelRenderer.domElement.style.position = 'absolute'
      this.labelRenderer.domElement.style.top = 0
      this.labelRenderer.domElement.id = 'labelDiv' // for by pass mouse events
      this.container.appendChild(this.labelRenderer.domElement)
      // this.labelControls = new OrbitControls(
      //   this.camera,
      //   this.labelRenderer.domElement
      // )

      this.domEvents = new THREEx.DomEvents(
        this.camera,
        this.renderer.domElement
      )
    },
    updateGui() {
      if (this.gui) {
        this.$refs.guiContainer.removeChild(this.gui.domElement)
        this.gui.destroy()
      }
      this.gui = new dat.GUI({ autoPlace: false })
      this.$refs.guiContainer.appendChild(this.gui.domElement)
      const chroms = Object.keys(this.splines)

      this.gui
        .addColor(this.params, 'sceneColor')
        .name('Background')
        .listen()
        .onChange(e => (this.scene.background = new THREE.Color(e)))
      this.gui
        .add(this.params, 'displayLabels')
        .name('Show label')
        .onChange(() => this.toggleLabelDisplay())
      this.gui
        .add(this.params, 'showAll')
        .name('Show all')
        .onChange(() => this.toggleAllMode())
      const folderGeometry = this.gui.addFolder('Regions')
      if (this.params.showAll) {
        Object.keys(this.splines).forEach(chrom => {
          const colorKey = `color_${chrom}`
          folderGeometry
            .addColor(this.params, colorKey)
            .listen()
            .name(chrom)
            .onChange(e => {
              if (this.meshes[chrom]) {
                this.meshes[chrom].material.color.setStyle(e)
              }
            })
        })
        const displayControl = this.gui.addFolder('Display')
        Object.keys(this.splines).forEach(chrom => {
          const displayKey = `display_${chrom}`
          displayControl
            .add(this.params, displayKey)
            .name(chrom)
            .onChange(val => {
              this.meshes[chrom].visible = val
              this.meshes[chrom].children.forEach(
                child => (child.visible = val)
              )
            })
        })
        this.gui
          .add(this.params, 'shape', {
            Line: 'line',
            Tube: 'tube',
            Ball: 'ball'
          })
          .name('Shape')
          .onChange(() => this.addAllShapes(this.params))
        const lineControls = this.gui.addFolder('Line Controls')
        lineControls
          .add(this.params, 'lineWidth', 1, 10)
          .onChange(() => this.addAllShapes(this.params))
      } else {
        this.params.color = this.meshMaterial.color.getStyle()

        folderGeometry.add(this.params, 'region', chroms).onChange(() => {
          this.addShapes(this.params)
        })
        folderGeometry.open()

        this.gui
          .addColor(this.params, 'color')
          .listen()
          .onChange(e => this.meshMaterial.color.setStyle(e))
        this.gui
          .add(this.params, 'scale', 1, 10)
          .onChange(() => this.setScale())

        const folderCamera = this.gui.addFolder('Camera')
        folderCamera
          .add(this.params, 'animationView')
          .name('Walk mode')
          .onChange(() => {
            this.animateCamera()
          })
        folderCamera
          .add(this.params, 'lookAhead')
          .name('Look ahead')
          .onChange(() => {
            this.animateCamera()
          })
        // folderCamera
        //   .add(this.params, 'cameraHelper')
        //   .onChange(() => this.animateCamera())
        folderCamera.add(this.params, 'speed', {
          Slow: 1,
          Medium: 10,
          Fast: 100
        })
        folderCamera.open()
      }

      // screenshot function
      this.params.screenshot = async () => {
        this.render()
        let screenshotCanvas
        if (this.params.displayLabels) {
          screenshotCanvas = await this.mergeCanvas()
        } else {
          screenshotCanvas = this.renderer.domElement
        }
        screenshotCanvas.toBlob(blob =>
          this.saveBlob(
            blob,
            `g3dv-screencapture-${new Date().toISOString()}.png`
          )
        )
      }
      this.gui.add(this.params, 'screenshot').name('📷Screenshot')
    },
    async mergeCanvas() {
      const labelCanvas = await html2canvas(this.labelRenderer.domElement, {
        backgroundColor: null
      })
      this.render()
      const threeCanvas = this.renderer.domElement
      const newCanvas = document.createElement('canvas')
      const ctx = newCanvas.getContext('2d')
      const width = threeCanvas.width
      const height = threeCanvas.height

      newCanvas.width = width
      newCanvas.height = height
      ;[threeCanvas, labelCanvas].forEach(function(n) {
        ctx.beginPath()
        ctx.drawImage(n, 0, 0, width, height)
      })

      return newCanvas
    },
    setScale() {
      this.mesh.scale.set(
        this.params.scale,
        this.params.scale,
        this.params.scale
      )
    },
    animateCamera() {
      this.cameraHelper.visible = this.params.cameraHelper
      this.cameraEye.visible = this.params.cameraHelper
    },
    update() {
      // Don't delete this function!
    },
    render() {
      this.stats.begin()
      // this.renderer.render(this.scene, this.camera)
      if (!this.meshGeometry) {
        return
      }

      const time = Date.now()
      const looptime = (20 * 100000) / this.params.speed
      const t = (time % looptime) / looptime

      const pos = this.meshGeometry.parameters.path.getPointAt(t)
      pos.multiplyScalar(this.params.scale)
      // interpolation

      const segments = this.meshGeometry.tangents.length
      const pickt = t * segments
      const pick = Math.floor(pickt)
      const pickNext = (pick + 1) % segments

      this.binormal.subVectors(
        this.meshGeometry.binormals[pickNext],
        this.meshGeometry.binormals[pick]
      )
      this.binormal
        .multiplyScalar(pickt - pick)
        .add(this.meshGeometry.binormals[pick])
      const dir = this.meshGeometry.parameters.path.getTangentAt(t)
      const offset = 1
      this.normal.copy(this.binormal).cross(dir)
      // we move on a offset on its binormal
      pos.add(this.normal.clone().multiplyScalar(offset))
      // console.log(pos)
      this.splineCamera.position.copy(pos)
      this.cameraEye.position.copy(pos)
      // using arclength for stablization in look ahead
      const lookAt = this.meshGeometry.parameters.path
        .getPointAt(
          (t + 30 / this.meshGeometry.parameters.path.getLength()) % 1
        )
        .multiplyScalar(this.params.scale)
      // camera orientation 2 - up orientation via normal
      if (!this.params.lookAhead) lookAt.copy(pos).add(dir)
      this.splineCamera.matrix.lookAt(
        this.splineCamera.position,
        lookAt,
        this.normal
      )
      this.splineCamera.quaternion.setFromRotationMatrix(
        this.splineCamera.matrix
      )

      // //picker
      // this.pickHelper.pick(this.pickPosition, this.scene.children, this.camera)

      this.cameraHelper.update()
      this.renderer.render(
        this.scene,
        this.params.animationView ? this.splineCamera : this.camera
      )
      this.labelRenderer.render(this.scene, this.camera)

      this.stats.end()
    },
    onWindowResize() {
      // set the aspect ratio to match the new browser window aspect ratio
      this.camera.aspect =
        this.container.clientWidth / this.container.clientHeight

      // update the camera's frustum
      this.camera.updateProjectionMatrix()

      // update the size of the renderer AND the canvas
      this.renderer.setSize(
        this.container.clientWidth,
        this.container.clientHeight
      )
      this.labelRenderer.setSize(
        this.container.clientWidth,
        this.container.clientHeight
      )
    },
    clearLabelDiv() {
      // const labelDiv = document.querySelector('#labelDiv')
      const labelDiv = this.labelRenderer.domElement
      while (labelDiv.firstChild) {
        labelDiv.removeChild(labelDiv.firstChild)
      }
    },
    toggleLabelDisplay() {
      // const labelDiv = document.querySelector('#labelDiv')
      const labelDiv = this.labelRenderer.domElement
      labelDiv.style.display = this.params.displayLabels ? 'block' : 'none'
    },
    toggleAllMode() {
      this.clearLabelDiv()
      if (this.params.showAll) {
        this.params.animationView = false
        this.params.lookAhead = false
        this.params.cameraHelper = false
        this.clearSingleMesh()
        this.addAllShapes(this.params)
        this.updateGui()
      } else {
        this.clearAllMeshes()
        this.addShapes(this.params)
        this.updateGui()
      }
    },
    addAllShapes(params) {
      this.clearAllMeshes()
      Object.keys(this.splines).forEach(chrom => {
        const { spline } = this.splines[chrom]
        let mesh
        switch (params.shape) {
          case 'line':
            mesh = getLineMesh(spline, params, chrom)
            break
          case 'tube':
            mesh = getTubeMesh(spline, params, chrom)
            break
          case 'ball':
            mesh = getBallMesh(spline, params, chrom)
            break
          default:
            break
        }
        this.scene.add(mesh)
        const displayKey = `display_${chrom}`
        mesh.visible = this.params[displayKey]
        // add label
        const labelDiv = document.createElement('div')
        labelDiv.className = 'label'
        labelDiv.textContent = chrom
        labelDiv.style.marginTop = '-1em'
        const colorKey = `color_${chrom}`
        const color = params[colorKey]
        labelDiv.style.color = color
        const label = new CSS2DObject(labelDiv)
        label.position.copy(spline.getPoint(0))
        mesh.add(label)
        this.meshes[chrom] = mesh
      })
    },
    addShapes(params) {
      // clearScene(this.scene)
      this.clearSingleMesh()
      const { region } = params
      const extrudePath = this.splines[region].spline
      this.meshGeometry = new THREE.TubeBufferGeometry(
        extrudePath,
        2000,
        0.1,
        8,
        false
      )
      this.meshMaterial = new THREE.MeshBasicMaterial({
        color: this.splines[params.region].color
      })
      this.mesh = new THREE.Mesh(this.meshGeometry, this.meshMaterial)
      // add label
      const labelDiv = document.createElement('div')
      labelDiv.className = 'label'
      labelDiv.textContent = region
      labelDiv.style.marginTop = '-1em'
      labelDiv.style.color = this.splines[params.region].color
      const label = new CSS2DObject(labelDiv)
      label.position.copy(extrudePath.getPoint(0))
      this.mesh.add(label)
      this.parent.add(this.mesh)
      this.domEvents.addEventListener(
        this.mesh,
        'click',
        () => {
          this.selectedMesh = this.mesh
          this.selectedMesh.material.color.set(0xffff00)
          this.selectedMesh.scale.set(1.1, 1.1, 1.1)
          this.selectedMesh.children[0].element.style.color = '#ffff00'
        },
        false
      )
    },
    disposeMesh(mesh) {
      mesh.geometry.dispose()
      if (mesh.material.isMaterial) {
        mesh.material.dispose()
      } else {
        for (const material of mesh.material) {
          material.dispose()
        }
      }
    },
    clearSingleMesh() {
      if (this.mesh) {
        this.parent.remove(this.mesh)
        this.disposeMesh(this.mesh)
      }
    },
    clearAllMeshes() {
      if (Object.keys(this.meshes).length) {
        Object.keys(this.meshes).forEach(chrom => {
          const mesh = this.meshes[chrom]
          this.scene.remove(mesh)
          this.disposeMesh(mesh)
        })
      }
    },
    saveBlob(blob, fileName) {
      const a = document.createElement('a')
      document.body.appendChild(a)
      a.style.display = 'none'
      return (function saveData(blob, fileName) {
        // console.log(blob)
        const url = window.URL.createObjectURL(blob)
        // console.log(url)
        a.href = url
        a.download = fileName
        a.click()
      })(blob, fileName)
    }
    // getCanvasRelativePosition(event) {
    //   const rect = this.container.getBoundingClientRect()
    //   return {
    //     x: event.clientX - rect.left,
    //     y: event.clientY - rect.top
    //   }
    // },
    // setPickPosition(event) {
    //   const pos = this.getCanvasRelativePosition(event)
    //   this.pickPosition.x = (pos.x / this.container.clientWidth) * 2 - 1
    //   this.pickPosition.y = (pos.y / this.container.clientHeight) * -2 + 1 // note we flip Y
    // },
    // clearPickPosition() {
    //   // unlike the mouse which always has a position
    //   // if the user stops touching the screen we want
    //   // to stop picking. For now we just pick a value
    //   // unlikely to pick something
    //   this.pickPosition.x = -100000
    //   this.pickPosition.y = -100000
    // }
  },
  mounted() {
    this.init()
    window.addEventListener('resize', this.onWindowResize)
    // window.addEventListener('mousemove', this.setPickPosition)
    // window.addEventListener('mouseout', this.clearPickPosition)
    // window.addEventListener('mouseleave', this.clearPickPosition)

    // //for mobile
    // window.addEventListener(
    //   'touchstart',
    //   event => {
    //     // prevent the window from scrolling
    //     event.preventDefault()
    //     this.setPickPosition(event.touches[0])
    //   },
    //   { passive: false }
    // )

    // window.addEventListener('touchmove', event => {
    //   this.setPickPosition(event.touches[0])
    // })

    // window.addEventListener('touchend', this.clearPickPosition)
  },
  watch: {
    data3d(newData, oldData) {
      if (newData !== oldData) {
        // renderShape(newData, this.scene, this.drawParam)
        this.splines = getSplines(newData)
        this.clearSingleMesh()
        this.clearAllMeshes()
        // show fist model by default
        const chroms = Object.keys(this.splines)
        // set each chrom color
        Object.keys(this.splines).forEach(chrom => {
          const colorKey = `color_${chrom}`
          const displayKey = `display_${chrom}`
          this.params[colorKey] = this.splines[chrom].color
          this.params[displayKey] = true
        })
        this.params.region = chroms[0]
        if (this.params.showAll) {
          this.addAllShapes(this.params)
        } else {
          this.addShapes(this.params)
        }
        this.updateGui()
        this.clearLabelDiv()
      }
    }
    // drawParam: {
    //   handler(newParam) {
    //     console.log(newParam)
    //   },
    //   deep: true
    // }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onWindowResize)
    // window.removeEventListener('mousemove', this.setPickPosition)
    // window.removeEventListener('mouseout', this.clearPickPosition)
    // window.removeEventListener('mouseleave', this.clearPickPosition)
  }
}
</script>

<style>
#parentContainer {
  position: relative;
}
#canvasContainer {
  width: 100%;
  height: 100%;
  display: block;
  font-size: 0;
  /* touch-action: none; */
}
#stats {
  position: absolute;
  left: 0px;
  top: 0px;
}
#gui-container {
  position: absolute;
  top: 0px;
  right: 0px;
  z-index: 10;
}

.dg .cr.boolean {
  overflow: visible;
}
.label {
  font-size: 12px;
  color: #fff;
  font-family: sans-serif;
  padding: 2px;
  background: rgba(0, 0, 0, 0.6);
}

#labelDiv {
  pointer-events: none;
}
</style>
