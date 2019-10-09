<template>
  <div class="home">
    <Menu />
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
