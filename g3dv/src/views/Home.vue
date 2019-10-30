<template>
  <div class="home">
    <div>
      <h4>Genomic 3D Visualizer</h4>
      <router-link to="/about">About</router-link>
      <Menu />
    </div>
    <Stage />
  </div>
</template>

<script>
// @ is an alias to /src
import Menu from '@/components/Menu.vue'
import Stage from '@/components/Stage.vue'

export default {
  name: 'home',
  components: {
    Menu,
    Stage
  }
}
</script>

<style scoped>
.home {
  display: grid;
  grid-template-columns: 2fr 8fr;
  grid-gap: 10px;
  height: 100%;
  width: 100%;
}
</style>
