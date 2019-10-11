<template>
  <canvas ref="renderCanvas" id="renderCanvas"></canvas>
</template>

<script>
import * as BABYLON from 'babylonjs'
// import * as GUI from 'babylonjs-gui'

export default {
  name: 'BabylonScene',
  data() {
    return {
      canvas: null,
      engine: null,
      scene: null
    }
  },
  props: {
    data: {
      type: Array
      //   required: true
    },
    onSceneMount: {
      type: Function
    }
  },
  methods: {
    init() {
      this.canvas = this.$refs.renderCanvas
      this.engine = new BABYLON.Engine(this.canvas, true)
      let scene = new BABYLON.Scene(this.engine)
      this.scene = scene
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
      //   // VR
      //   this.vrHelper = this.scene.createDefaultVRExperience({
      //     createDeviceOrientationCamera: false
      //   })
      console.log('xxx')
      if (typeof this.onSceneMount === 'function') {
        this.onSceneMount({
          scene,
          engine: this.engine,
          canvas: this.canvas
        })
      } else {
        console.error('onSceneMount function not available')
      }

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

    // Resize the babylon engine when the window is resized
    window.addEventListener('resize', this.onResizeWindow)
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
