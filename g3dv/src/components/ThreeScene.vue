<template>
  <div id="parentContainer">
    <div id="stats" ref="statsContainer"></div>
    <div id="gui-container" ref="guiContainer"></div>
    <div id="canvasContainer" ref="canvasContainer"></div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import * as THREE from 'three'
import OrbitControls from 'three-orbitcontrols'
import Stats from 'stats-js'
import * as dat from 'dat.gui'

import { renderTube } from '@/components/Tube'
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
      gui: null
    }
  },

  computed: mapState(['g3d', 'data3d']),
  methods: {
    init() {
      this.container = this.$refs.canvasContainer
      this.scene = new THREE.Scene()
      //   this.scene.background = new THREE.Color(0x8fbcd4)
      this.stats = new Stats()
      this.stats.showPanel(0)
      this.stats.dom.style.position = 'absolute'
      this.$refs.statsContainer.appendChild(this.stats.dom)
      this.gui = new dat.GUI({ autoPlace: false })
      this.$refs.guiContainer.appendChild(this.gui.domElement)

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

      //   this.renderer.gammaFactor = 2.2;
      //   this.renderer.gammaOutput = true;

      //   this.renderer.physicallyCorrectLights = true;

      this.container.appendChild(this.renderer.domElement)
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
    }
  },
  mounted() {
    this.init()
    window.addEventListener('resize', this.onWindowResize)
  },
  watch: {
    data3d(newData, oldData) {
      if (newData !== oldData) {
        renderTube(newData, this.scene)
      }
    }
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
