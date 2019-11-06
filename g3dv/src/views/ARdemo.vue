<template>
  <a-scene embedded arjs="sourceType: webcam;" v-if="dataReady">
    <a-entity
      mymesh
      animation="property: rotation; from: 0 0 0; to: 360 360 360; easing: linear; dur: 10000; loop: true"
    ></a-entity>
    <!-- <a-marker-camera preset="kanji"></a-marker-camera> -->
    <a-marker-camera
      preset="custom"
      type="pattern"
      url="https://wangftp.wustl.edu/~dli/test/pattern-arch2.patt"
    ></a-marker-camera>
  </a-scene>
</template>

<script>
import G3dFile from 'g3djs'
import { getSplines } from '@/components/Tube'
const AFRAME = window.AFRAME
const THREE = AFRAME.THREE // very important
export default {
  name: 'ARdemo',
  data() {
    return {
      splines: null,
      group: new THREE.Object3D(),
      dataReady: false
    }
  },
  methods: {
    async initData() {
      // setup data
      const gf = new G3dFile({
        url: 'https://wangftp.wustl.edu/~dli/tmp/test.g3d'
      })
      const data = await gf.readDataGenome(200000)
      this.splines = getSplines(data)
      this.dataReady = true
      // console.log(this.splines)
    }
  },
  async created() {
    // console.log('created')
    // console.log('init data')
    await this.initData()
    // console.log('init ready')
  },
  watch: {
    dataReady(newData) {
      if (newData) {
        const that = this
        AFRAME.registerComponent('mymesh', {
          update: function() {
            const group = new THREE.Object3D()
            // console.log(that.splines)
            Object.keys(that.splines).forEach(chrom => {
              const { spline, color } = that.splines[chrom]
              const geometry = new THREE.TubeBufferGeometry(
                spline,
                2000,
                0.2,
                8,
                false
              )
              const material = new THREE.MeshBasicMaterial({ color })
              const mesh = new THREE.Mesh(geometry, material)
              mesh.scale.set(0.02, 0.02, 0.02)
              group.add(mesh)
            })

            // const material = new THREE.MeshBasicMaterial({ color: 'blue' })
            // const geometry = new THREE.BoxGeometry(1, 1, 1)
            // const cube = new THREE.Mesh(geometry, material)
            // cube.position.x = 0
            // cube.position.y = 0.5
            // cube.position.z = 0
            // const cube2 = cube.clone()
            // cube2.position.x = 1
            // cube2.position.y = 1
            // group.add(cube)
            // group.add(cube2)

            group.position.x = 0
            group.position.y = 0.5
            group.position.z = 0

            // console.log(group)
            this.el.setObject3D('mesh', group) //unique name for each object
            // this.el.object3D.rotation.set(
            //   THREE.Math.degToRad(15),
            //   THREE.Math.degToRad(30),
            //   THREE.Math.degToRad(90)
            // )
            // this.el.object3D.rotation.x += 0.01
            // this.el.object3D.rotation.y += 0.01
            // this.el.object3D.rotation.z += 0.01
            // console.log(this.el.object3DMap)
          }
        })
      }
    }
  }
}
</script>

<style></style>
