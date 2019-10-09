<template>
  <form @submit.prevent="handleSubmit">
    <div class="field">
      <label>Input a G3D file URL</label>
      <input
        type="text"
        v-model="g3d.url"
        placeholder="G3D file url"
        size="40"
      />
    </div>
    <div class="field">
      <label>Genome assembly</label>
      <select>
        <option value="hg19">hg19</option>
      </select>
    </div>
    <div class="field">
      <label>Select a resolution</label>
      <select v-model="g3d.resolution">
        <option v-for="res in resolutions" :key="res" :value="res">{{
          prettyRes(res)
        }}</option>
      </select>
    </div>
    <div class="field">
      <label>Select a gene or region</label>
      <br />
      <input
        type="text"
        v-model="g3d.region"
        size="40"
        placeholder="gene symbol or region"
      />
    </div>
    <div class="field">
      <label>Choose display region</label>
      <br />
      <label>
        <input
          type="radio"
          name="region"
          v-model="g3d.regionControl"
          value="region"
        />Input region
      </label>
      <br />
      <label>
        <input
          type="radio"
          name="region"
          v-model="g3d.regionControl"
          value="chrom"
        />
        Whole Chromosome
      </label>
      <br />
      <label>
        <input
          type="radio"
          name="region"
          v-model="g3d.regionControl"
          value="genome"
        />Whole Genome
      </label>
    </div>
    <button type="button" @click="fillExample">Example</button>
    <button type="submit">Go</button>
    <div v-if="error">{{ error }}</div>
    <div v-if="isLoading">Loading...</div>
  </form>
</template>

<script>
import G3dFile from 'g3djs'
import { mapState } from 'vuex'
export default {
  name: 'Menu',
  data() {
    return {
      g3d: this.createFreshG3d(),
      resolutions: this.$store.state.resolutions,
      error: null
    }
  },
  computed: mapState(['isLoading']),
  methods: {
    fillExample() {
      ;(this.g3d.url =
        'https://wangftp.wustl.edu/~dli/tmp/GSM3271347_gm12878_01.impute3.round4.clean.g3d'),
        (this.g3d.region = 'chr7:27053397-27373765')
    },
    createFreshG3d() {
      return {
        url: '',
        region: '',
        resolution: 200000,
        regionControl: 'region'
      }
    },
    prettyRes(res) {
      return res / 1000 + 'K'
    },
    async handleSubmit() {
      if (!this.g3d.url.length) {
        this.error = 'Please submit a URL'
        return
      }
      this.$store.dispatch('setG3d', this.g3d)
      const gf = new G3dFile({ url: this.g3d.url })
      this.$store.dispatch('setG3dFile', gf)
      await this.$store.dispatch('fetchData')
    }
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 10px;
}
</style>
