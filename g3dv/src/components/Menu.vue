<template>
  <form @submit.prevent="handleSubmit">
    <div class="field">
      <Tabs @setInputSource="onSetInputSource" @tabHandler="setTabHandler">
        <Tab name="Remote file" :selected="true">
          <label>Input a G3D file URL</label>
          <input
            type="text"
            v-model="g3d.url"
            placeholder="G3D file url"
            size="40"
          />
        </Tab>
        <Tab name="Local file">
          <label>Choose a local G3D file</label>
          <input type="file" @change="onFileChange" />
        </Tab>
      </Tabs>
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
        />
        Input region
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
        />
        Whole Genome
      </label>
    </div>
    <button type="button" @click="fillExample">Example</button>
    {{ ' ' }}
    <button type="submit">Go</button>
    <div class="-text-error" v-if="error">{{ error }}</div>
    <div class="-text-error" v-if="stateErrorMsg">{{ stateErrorMsg }}</div>
    <div v-if="isLoading">Loading...</div>
    <div>
      <Gene />
    </div>
  </form>
</template>

<script>
import G3dFile from 'g3djs'
import { mapState } from 'vuex'
import Tabs from '@/components/Tabs.vue'
import Tab from '@/components/Tab.vue'
import Gene from '@/components/Gene.vue'
export default {
  name: 'Menu',
  data() {
    return {
      g3d: this.createFreshG3d(),
      resolutions: this.$store.state.resolutions,
      error: null,
      inputSource: 'Remote file'
    }
  },
  components: {
    Tab,
    Tabs,
    Gene
  },
  computed: mapState(['isLoading', 'stateErrorMsg']),
  methods: {
    // the way to call a method from a child component, a little bit confusing
    // see this SO post: https://stackoverflow.com/a/53059914/1098347
    setTabHandler(fn) {
      this.setTab = fn
    },
    onSetInputSource(name) {
      this.inputSource = name
    },
    onFileChange(e) {
      const files = e.target.files || e.dataTransfer.files
      if (!files.length) {
        this.error = 'Please select a local file'
        return
      }
      this.g3d.blob = files[0]
    },
    fillExample() {
      ;(this.g3d.url = 'https://wangftp.wustl.edu/~dli/tmp/test.g3d'),
        (this.g3d.region = 'chr7:27053397-27373765')
      this.setTab('Remote file')
    },
    createFreshG3d() {
      return {
        url: '',
        blob: null,
        region: '',
        resolution: 200000,
        regionControl: 'region'
      }
    },
    prettyRes(res) {
      return res / 1000 + 'K'
    },
    async handleSubmit() {
      let gf
      this.$store.dispatch('setG3d', this.g3d)
      if (this.inputSource === 'Local file') {
        if (!this.g3d.blob) {
          this.error = 'Please upload a g3d file'
          return
        }
        this.error = null
        gf = new G3dFile({ blob: this.g3d.blob })
      } else {
        if (!this.g3d.url.length) {
          this.error = 'Please submit a URL'
          return
        }
        this.error = null
        gf = new G3dFile({ url: this.g3d.url })
      }
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
button,
label,
input,
optgroup,
select,
textarea {
  display: inline-flex;
  font-family: 'Open sans', sans-serif;
  font-size: 100%;
  line-height: 1.15;
  margin: 0;
}
button,
input {
  overflow: visible;
}
button,
select {
  text-transform: none;
}
button,
[type='button'],
[type='reset'],
[type='submit'] {
  -webkit-appearance: none;
}
button::-moz-focus-inner,
[type='button']::-moz-focus-inner,
[type='reset']::-moz-focus-inner,
[type='submit']::-moz-focus-inner {
  border-style: none;
  padding: 0;
}
button:-moz-focusring,
[type='button']:-moz-focusring,
[type='reset']:-moz-focusring,
[type='submit']:-moz-focusring {
  outline: 2px solid #39b982;
}
label {
  color: rgba(0, 0, 0, 0.5);
  font-weight: 700;
}
input,
textarea {
  box-sizing: border-box;
  border: solid 1px rgba(0, 0, 0, 0.4);
}
textarea {
  width: 100%;
  overflow: auto;
  font-size: 20px;
}
[type='checkbox'],
[type='radio'] {
  box-sizing: border-box;
  padding: 0;
}
[type='number']::-webkit-inner-spin-button,
[type='number']::-webkit-outer-spin-button {
  height: auto;
}
[type='search'] {
  -webkit-appearance: textfield;
  outline-offset: -2px;
}
[type='search']::-webkit-search-decoration {
  -webkit-appearance: none;
}
[type='text'],
[type='number'],
[type='search'],
[type='password'] {
  height: 52px;
  width: 100%;
  padding: 0 10px;
  font-size: 20px;
}
[type='text']:focus,
[type='number']:focus,
[type='search']:focus,
[type='password']:focus {
  border-color: #39b982;
}
::-webkit-file-upload-button {
  -webkit-appearance: button;
  font: inherit;
}
[hidden] {
  display: none;
}
select {
  width: 100%;
  height: 52px;
  padding: 0 24px 0 10px;
  vertical-align: middle;
  background: #fff
    url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'%3E%3Cpath fill='%23343a40' d='M2 0L0 2h4zm0 5L0 3h4z'/%3E%3C/svg%3E")
    no-repeat right 12px center;
  background-size: 8px 10px;
  border: solid 1px rgba(0, 0, 0, 0.4);
  border-radius: 0;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
select:focus {
  border-color: #39b982;
  outline: 0;
}
select:focus::ms-value {
  color: #000;
  background: #fff;
}
select::ms-expand {
  opacity: 0;
}
input[type='radio'] {
  margin-right: 5px;
}
input[type='file'] {
  border: none;
}
</style>
