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
import { clearScene } from '@/helper'

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
      splines: null // key, chr or region, mat or pat, value, {spine: spline object in Three, color: color}
    }
  },
  computed: mapState(['g3d', 'data3d']),
  methods: {
    init() {
      this.container = this.$refs.canvasContainer
      this.scene = new THREE.Scene()
      //   this.scene.background = new THREE.Color(0x8fbcd4)
      const axes = new THREE.AxesHelper(50)
      this.scene.add(axes)
      this.stats = new Stats()
      this.stats.showPanel(0)
      this.stats.dom.style.position = 'absolute'
      this.$refs.statsContainer.appendChild(this.stats.dom)

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
        75, // FOV
        this.container.clientWidth / this.container.clientHeight, // aspect
        0.1, // near clipping plane
        1000 // far clipping plane
      )

      this.camera.position.set(0, 10, 120)
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
      const params = {
        region: chroms[0],
        shape: 'line',
        'line width': 1
      }
      const folderGeometry = this.gui.addFolder('Regions')
      folderGeometry.add(params, 'region', chroms).onChange(() => {
        this.addShapes(params)
      })
      this.gui
        .add(params, 'shape', { Line: 'line', Tube: 'tube', Ball: 'ball' })
        .onChange(() => this.addShapes(params))
      const lineControls = this.gui.addFolder('Line Controls')
      lineControls
        .add(params, 'line width', 1, 10)
        .onChange(() => this.addShapes(params))
    },
    update() {
      // Don't delete this function!
    },
    render() {
      this.stats.begin()
      this.renderer.render(this.scene, this.camera)
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
      clearScene(this.scene)
      const { region, shape } = params
      const extrudePath = this.splines[region].spline
      const color = this.splines[region].color
      switch (shape) {
        case 'line':
          this.renderLine(extrudePath, params)
          break
        case 'tube':
          this.renderTube(extrudePath, color)
          break
        case 'ball':
          this.renderBall(extrudePath, color)
          break
        default:
          break
      }
    },
    renderTube(path, color) {
      const geometry = new THREE.TubeBufferGeometry(path, 2000, 0.5, 8, false)
      const material = new THREE.MeshBasicMaterial({
        color
      })
      const mesh = new THREE.Mesh(geometry, material)
      this.scene.add(mesh)
    },
    renderLine(path, params) {
      const points = path.getPoints(5000)
      const geometry = new THREE.Geometry().setFromPoints(points)
      const line = new MeshLine()
      line.setGeometry(geometry)
      // line.setGeometry(geometry, function() {
      //   return 2
      // })
      const material = new MeshLineMaterial({
        color: this.splines[params.region].color,
        lineWidth: params['line width'] / 10
      })
      const mesh = new THREE.Mesh(line.geometry, material) // this syntax could definitely be improved!
      this.scene.add(mesh)
    },
    renderBall(path, color) {
      const points = path.getPoints(500)
      const geometry = new THREE.SphereBufferGeometry(0.5, 16, 16)
      const material = new THREE.MeshBasicMaterial({
        color
      })
      const geoms = []
      points.forEach(point => {
        const geom = geometry.clone()
        geom.translate(point.x, point.y, point.z)
        geoms.push(geom)
      })
      const mergedGeometry = BufferGeometryUtils.mergeBufferGeometries(geoms)
      const mesh = new THREE.Mesh(mergedGeometry, material)
      this.scene.add(mesh)
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
