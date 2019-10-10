<template>
  <div>
    <canvas ref="renderCanvas" id="renderCanvas"></canvas>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import * as BABYLON from 'babylonjs'
// import * as GUI from 'babylonjs-gui'
// import { deconstructMesh } from '@/helper'

export default {
  computed: mapState(['g3d', 'data3d']),
  data() {
    return {
      canvas: null,
      engine: null,
      scene: null
    }
  },
  methods: {
    init() {
      this.canvas = this.$refs.renderCanvas
      this.engine = new BABYLON.Engine(this.canvas, true, {
        preserveDrawingBuffer: true,
        stencil: true
      })
      this.scene = new BABYLON.Scene(this.engine)
      //camera
      this.mainCamera = new BABYLON.ArcRotateCamera(
        'ArcRotateCamera',
        0,
        0,
        10,
        BABYLON.Vector3.Zero(),
        this.scene
      )

      this.mainCamera.setPosition(new BABYLON.Vector3(0, 0, -10))
      this.mainCamera.wheelPrecision = 0.1
      this.mainCamera.lowerBetaLimit = 0.1
      this.mainCamera.upperBetaLimit = (Math.PI / 2) * 0.99
      this.mainCamera.maxZ = 20000
      this.mainCamera.inputs.attached.pointers.buttons = [0]
      this.mainCamera.attachControl(this.canvas)

      //lights
      this.mainLight = new BABYLON.HemisphericLight(
        'light1',
        new BABYLON.Vector3(0, 1, 0),
        this.scene
      )
      this.renderChromosome()
      this.engine.runRenderLoop(() => {
        if (this.scene) {
          this.scene.render()
        }
      })
    },
    onResizeWindow() {
      if (this.engine) {
        this.engine.resize()
      }
    },
    renderChromosome() {
      if (!this.data3d.length) {
        return
      }
      const pointArray = this.data3d.map(
        item => new BABYLON.Vector3(item[3], item[4], item[5])
      )
      console.log(pointArray)
      const catmullRom = BABYLON.Curve3.CreateCatmullRomSpline(
        pointArray,
        50,
        false
      )
      const path = catmullRom.getPoints()
      console.log(path)
      this.chromosome = BABYLON.TubeBuilder.CreateTube(
        'chromosome',
        {
          path,
          radius: 2,
          cap: BABYLON.Mesh.CAP_ALL
        },
        this.scene
      )
      // const chromosomeSegments = deconstructMesh(chromosome, this.scene)
      // chromosomeSegments.forEach(mesh => {
      //   var color

      //   var rand
      //   rand = Math.random()
      //   if (rand < 0.25) {
      //     color = new BABYLON.Color4(1, 1, 1, 1)
      //   }
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

      //   var materialColor = new BABYLON.StandardMaterial(
      //     'materialcolor',
      //     this.scene
      //   )
      //   materialColor.diffuseColor = color
      //   materialColor.computeHighLevel = true
      //   mesh.material = materialColor
      // })
    }
  },
  mounted() {
    this.init()
    console.log(this.scene)
    // Resize the babylon engine when the window is resized
    window.addEventListener('resize', this.onResizeWindow)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResizeWindow)
  }
}
</script>

<style scoped>
#renderCanvas {
  width: 100%;
  height: 100%;
  display: block;
  font-size: 0;
  touch-action: none;
}
</style>
