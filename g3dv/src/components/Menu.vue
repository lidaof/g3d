<template>
  <form @submit.prevent>
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
        <option v-for="res in resolutions" :key="res" :value="res">
          {{ prettyRes(res) }}
        </option>
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
    <button @click="fillExample">Example</button>
    <button>Go</button>
  </form>
</template>

<script>
export default {
  name: 'Menu',
  data() {
    return {
      g3d: this.createFreshG3d(),
      resolutions: this.$store.state.resolutions
    }
  },
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
    }
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 10px;
}
</style>
