<template>
   <!-- <a-scene>
      <a-box position="-1 0.5 -3" rotation="0 45 0" color="#4CC3D9"></a-box>
      <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E"></a-sphere>
      <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D"></a-cylinder>
      <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#7BC8A4"></a-plane>
      <a-sky color="#ECECEC"></a-sky>
    </a-scene> -->
    <a-scene embedded arjs>
  	<a-marker preset="hiro">
            <!-- <a-box position='0 0.5 0' material='color: yellow;'></a-box> -->
            <a-entity main></a-entity>
  	</a-marker>
  	<a-entity camera></a-entity>
    </a-scene>
</template>

<script>
import * as THREE from 'three'
export default {
    name: 'ARdemo',
    data(){
        return {
            main: new THREE.Object3D()
        }
    },
    methods: {
        init(){
            var geometry = new THREE.BoxGeometry( 1, 1, 1 );
var material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
const mesh = new THREE.Mesh( geometry, material );
this.main.add(mesh)
        }
    },
    created(){
        this.init()
        console.log(this.main)
        AFRAME.registerComponent('main', {
    init:function(){
      this.el.setObject3D('main', this.main);
    }
  });
    }
}
</script>

<style>

</style>