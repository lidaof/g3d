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
import { BufferGeometryUtils } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { MeshLine, MeshLineMaterial } from 'three.meshline'
import Stats from 'stats-js'
import * as dat from 'dat.gui'
import { getSplines } from '@/components/Tube'
// import { clearScene } from '@/helper'

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
      binormal: new THREE.Vector3(),
      normal: new THREE.Vector3(),
      parent: null,
      splineCamera: null,
      cameraHelper: null,
      cameraEye: null,
      meshGeometry: null,
      meshMaterial: null,
      params: {
        region: '',
        shape: 'tube',
        lineWidth: 1,
        color: '',
        animationView: false,
        lookAhead: false,
        cameraHelper: false,
        scale: 1
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
      this.camera = new THREE.PerspectiveCamera(
        50, // FOV
        this.container.clientWidth / this.container.clientHeight, // aspect
        0.1, // near clipping plane
        10000 // far clipping plane
      )

      this.camera.position.set(0, 50, 500)

      this.splineCamera = new THREE.PerspectiveCamera(
        84,
        this.container.clientWidth / this.container.clientHeight,
        0.01,
        1000
      )
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
    },
    updateGui() {
      if (this.gui) {
        this.$refs.guiContainer.removeChild(this.gui.domElement)
        this.gui.destroy()
      }
      this.gui = new dat.GUI({ autoPlace: false })
      this.$refs.guiContainer.appendChild(this.gui.domElement)
      const chroms = Object.keys(this.splines)
      this.params.region = chroms[0]

      this.params.color = this.meshMaterial.color.getStyle()

      const folderGeometry = this.gui.addFolder('Regions')
      folderGeometry.add(this.params, 'region', chroms).onChange(() => {
        this.addShapes(this.params)
      })
      folderGeometry.open()
      this.gui
        .add(this.params, 'shape', { Line: 'line', Tube: 'tube', Ball: 'ball' })
        .onChange(() => this.addShapes(this.params))
      this.gui
        .addColor(this.params, 'color')
        .listen()
        .onChange(e => this.meshMaterial.color.setStyle(e))
      this.gui.add(this.params, 'scale', 1, 10).onChange(() => this.setScale())
      const lineControls = this.gui.addFolder('Line Controls')
      lineControls
        .add(this.params, 'lineWidth', 1, 10)
        .onChange(() => this.addShapes(this.params))

      const folderCamera = this.gui.addFolder('Camera')
      folderCamera.add(this.params, 'animationView').onChange(() => {
        this.animateCamera()
      })
      folderCamera.add(this.params, 'lookAhead').onChange(() => {
        this.animateCamera()
      })
      folderCamera
        .add(this.params, 'cameraHelper')
        .onChange(() => this.animateCamera())
      folderCamera.open()
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
      const looptime = 20 * 100000
      const t = (time % looptime) / looptime

      const pos = this.meshGeometry.parameters.path.getPointAt(t)
      pos.multiplyScalar(this.params.scale)
      // console.log(pos)
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

      this.cameraHelper.update()

      this.renderer.render(
        this.scene,
        this.params.animationView ? this.splineCamera : this.camera
      )

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
    },
    addShapes(params) {
      // clearScene(this.scene)
      if (this.mesh) {
        this.parent.remove(this.mesh)
        this.mesh.geometry.dispose()
        if (this.mesh.material.isMaterial) {
          this.mesh.material.dispose()
        } else {
          for (const material of this.mesh.material) {
            material.dispose()
          }
        }
      }
      const { region, shape } = params
      const extrudePath = this.splines[region].spline
      switch (shape) {
        case 'line':
          this.prepareLineMesh(extrudePath, params)
          break
        case 'tube':
          this.prepareTubeMesh(extrudePath, params)
          break
        case 'ball':
          this.prepareBallMesh(extrudePath, params)
          break
        default:
          break
      }
      this.mesh = new THREE.Mesh(this.meshGeometry, this.meshMaterial)
      this.parent.add(this.mesh)
    },
    prepareTubeMesh(path, params) {
      this.meshGeometry = new THREE.TubeBufferGeometry(
        path,
        2000,
        0.1,
        8,
        false
      )
      this.meshMaterial = new THREE.MeshBasicMaterial({
        color: this.splines[params.region].color
      })
    },
    prepareLineMesh(path, params) {
      const points = path.getPoints(5000)
      const geometry = new THREE.Geometry().setFromPoints(points)
      const line = new MeshLine()
      line.setGeometry(geometry)
      // line.setGeometry(geometry, function() {
      //   return 2
      // })
      const material = new MeshLineMaterial({
        color: this.splines[params.region].color,
        lineWidth: params.lineWidth / 10
      })
      this.meshGeometry = line.geometry
      this.meshMaterial = material
    },
    prepareBallMesh(path, params) {
      const points = path.getPoints(500)
      const geometry = new THREE.SphereBufferGeometry(0.5, 16, 16)
      const material = new THREE.MeshBasicMaterial({
        color: this.splines[params.region].color
      })
      const geoms = []
      points.forEach(point => {
        const geom = geometry.clone()
        geom.translate(point.x, point.y, point.z)
        geoms.push(geom)
      })
      this.meshGeometry = BufferGeometryUtils.mergeBufferGeometries(geoms)
      this.meshMaterial = material
    }
  },
  mounted() {
    this.init()
    window.addEventListener('resize', this.onWindowResize)
  },
  watch: {
    data3d(newData, oldData) {
      if (newData !== oldData) {
        // renderShape(newData, this.scene, this.drawParam)
        this.splines = getSplines(newData)
        // show fist model by default
        const chroms = Object.keys(this.splines)
        const defaultParams = {
          ...this.params,
          region: chroms[0]
        }
        this.addShapes(defaultParams)
        this.updateGui()
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
}
</style>