<template>
  <BabylonScene @sceneReady="mountScene" />
</template>

<script>
import * as BABYLON from 'babylonjs'
import BabylonScene from '@/components/BabylonScene.vue'

export default {
  name: 'SceneViewer',
  components: {
    BabylonScene
  },
  // props: {
  //   data: {
  //     type: Array
  //     //   required: true
  //   }
  // },

  methods: {
    mountScene(e) {
      const { canvas, scene, engine } = e

      scene.clearColor = new BABYLON.Color3.White()
      scene.autoclear = true
      // const camera = new BABYLON.ArcRotateCamera(
      //   'camera1',
      //   BABYLON.Tools.ToRadians(45),
      //   BABYLON.Tools.ToRadians(45),
      //   10,
      //   new BABYLON.Vector3(0, 0, 0),
      //   scene
      // )
      // camera.setPosition(new BABYLON.Vector3(0, 0, -10))

      // This creates and positions a free camera (non-mesh)
      const camera = new BABYLON.FreeCamera(
        'camera1',
        new BABYLON.Vector3(5, -5, -30),
        scene
      )
      // // This targets the camera to scene origin
      camera.setTarget(BABYLON.Vector3.Zero())
      camera.wheelPrecision = 0.05
      camera.lowerBetaLimit = 0.1
      camera.upperBetaLimit = (Math.PI / 2) * 0.99
      camera.maxZ = 20000
      // camera.inputs.attached.pointers.buttons = [0]
      // This attaches the camera to the canvas
      camera.attachControl(canvas, true)
      camera.keysUp.push(87)
      camera.keysDown.push(83)
      camera.keysLeft.push(65)
      camera.keysRight.push(68)
      // This creates a light, aiming 0,1,0 - to the sky (non-mesh)
      const light = new BABYLON.HemisphericLight(
        'light1',
        new BABYLON.Vector3(0, 1, 0),
        scene
      )
      // Default intensity is 1. Let's dim the light a small amount
      light.intensity = 1
      // // Our built-in 'sphere' shape. Params: name, subdivs, size, scene
      // const sphere = BABYLON.Mesh.CreateSphere('sphere1', 16, 2, scene)
      // // Move the sphere upward 1/2 its height
      // sphere.position.y = 1
      // // Our built-in 'ground' shape. Params: name, width, depth, subdivs, scene
      // const ground = BABYLON.Mesh.CreateGround('ground1', 6, 6, 2, scene)
      // ground.position.x = 0

      // VR
      this.vrHelper = scene.createDefaultVRExperience({
        createDeviceOrientationCamera: false
      })
      engine.runRenderLoop(() => {
        if (scene) {
          scene.render()
        }
      })
    }
  }
}
</script>

<style></style>
