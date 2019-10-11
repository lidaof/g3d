<template>
  <SceneViewer />
</template>

<script>
import { mapState } from 'vuex'
import SceneViewer from '@/components/SceneViewer.vue'
export default {
  name: 'Stage',
  components: {
    SceneViewer
  },
  computed: mapState(['g3d', 'data3d'])
}
</script>

<style scoped></style>
