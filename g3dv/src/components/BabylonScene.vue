<template>
  <canvas ref="renderCanvas" id="renderCanvas"></canvas>
</template>

<script>
import { mapState } from 'vuex'
import * as BABYLON from 'babylonjs'
// import * as GUI from 'babylonjs-gui'
import { renderTubeToScene } from '@/components/Tube'

export default {
  name: 'BabylonScene',
  data() {
    return {
      canvas: null,
      engine: null,
      scene: null
    }
  },
  // props: {
  //   data: {
  //     type: Array
  //     //   required: true
  //   },
  //   onSceneMount: {
  //     type: Function
  //   }
  // },
  computed: mapState(['g3d', 'data3d']),
  methods: {
    init() {
      this.canvas = this.$refs.renderCanvas
      this.engine = new BABYLON.Engine(this.canvas, true)
      this.scene = new BABYLON.Scene(this.engine)
      // this.scene = scene
      //camera
      //   this.mainCamera = new BABYLON.ArcRotateCamera(
      //     'ArcRotateCamera',
      //     0,
      //     0,
      //     10,
      //     BABYLON.Vector3.Zero(),
      //     this.scene
      //   )

      //   this.mainCamera.setPosition(new BABYLON.Vector3(0, 0, -10))
      //   this.mainCamera.wheelPrecision = 0.1
      //   this.mainCamera.lowerBetaLimit = 0.1
      //   this.mainCamera.upperBetaLimit = (Math.PI / 2) * 0.99
      //   this.mainCamera.maxZ = 20000
      //   this.mainCamera.inputs.attached.pointers.buttons = [0]
      //   this.mainCamera.attachControl(this.canvas)

      //   //lights
      //   this.mainLight = new BABYLON.HemisphericLight(
      //     'light1',
      //     new BABYLON.Vector3(0, 1, 0),
      //     this.scene
      //   )
      // if (typeof this.onSceneMount === 'function') {
      //   this.onSceneMount({
      //     scene,
      //     engine: this.engine,
      //     canvas: this.canvas
      //   })
      // } else {
      //   console.error('onSceneMount function not available')
      // }

      //   this.engine.runRenderLoop(() => {
      //     if (this.scene) {
      //       this.scene.render()
      //     }
      //   })
    },
    onResizeWindow() {
      if (this.engine) {
        this.engine.resize()
      }
    }
  },
  mounted() {
    this.init()
    this.$emit('sceneReady', {
      scene: this.scene,
      engine: this.engine,
      canvas: this.canvas
    })
    // Resize the babylon engine when the window is resized
    window.addEventListener('resize', this.onResizeWindow)
  },
  watch: {
    data3d(newData, oldData) {
      if (newData !== oldData) {
        renderTubeToScene(newData, this.scene)
      }
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResizeWindow)
  }
}
</script>

<style>
#renderCanvas {
  width: 100%;
  height: 100%;
  display: block;
  font-size: 0;
  touch-action: none;
}
</style>
