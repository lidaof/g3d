<template @onSetGene="handleSetGene">
  <div class="search-container">
    <VueAutosuggest
      ref="autocomplete"
      v-model="query"
      :suggestions="suggestions"
      :inputProps="inputProps"
      :sectionConfigs="sectionConfigs"
      :renderSuggestion="renderSuggestion"
      :getSuggestionValue="getSuggestionValue"
      @input="fetchResults"
    />
    <div v-if="isoforms.length" style="margin-top: 10px;">
      <div class="autosuggest__results" v-show="displayIsoform">
        <ul>
          <li
            class="autosuggest__results-item"
            v-for="isoform in isoforms"
            :key="isoform._id"
          >
            <GeneAnnotation :gene="isoform" />
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { VueAutosuggest } from 'vue-autosuggest'
import axios from 'axios'
import GeneAnnotation from '@/components/GeneAnnotation.vue'
export default {
  name: 'Gene',
  components: {
    VueAutosuggest,
    GeneAnnotation
  },
  data() {
    return {
      query: '',
      isoforms: [],
      timeout: null,
      selected: null,
      debounceMilliseconds: 250,
      genesUrl: 'https://lambda.epigenomegateway.org/v2',
      inputProps: {
        id: 'autosuggest__input',
        placeholder: 'gene symbol',
        class: 'form-control'
      },
      displayIsoform: true,
      suggestions: [],
      sectionConfigs: {
        symbols: {
          limit: 10,
          label: 'Gene symbols',
          onSelected: selected => {
            this.selected = selected.item
            this.fetchIsoforms()
          }
        }
      }
    }
  },
  methods: {
    handleSetGene(gene) {
      console.log(gene)
      this.displayIsoform = false
    },
    fetchResults() {
      const query = this.query.trim()
      if (query.length < 3) {
        // no fetch is symbol less than 3 letters
        return
      }
      clearTimeout(this.timeout)
      this.timeout = setTimeout(() => {
        const symbolsPromise = axios.get(
          `${this.genesUrl}/hg19/genes/queryName`,
          {
            params: {
              q: query,
              getOnlyNames: true
            }
          }
        )
        Promise.resolve(symbolsPromise).then(value => {
          this.suggestions = []
          this.selected = null
          this.suggestions = [{ name: 'symbols', data: value.data }]
        })
      }, this.debounceMilliseconds)
    },
    renderSuggestion(suggestion) {
      return suggestion.item
    },
    getSuggestionValue(suggestion) {
      return suggestion.item
    },
    async fetchIsoforms() {
      if (this.selected) {
        const params = {
          q: this.selected,
          isExact: true
        }
        const response = await axios.get(
          `${this.genesUrl}/hg19/genes/queryName`,
          { params: params }
        )
        this.isoforms = response.data
      }
    }
  }
}
</script>

<style>
.search-container {
  width: 100%;
  position: relative;
}
#autosuggest__input {
  outline: none;
  position: relative;
  display: block;
  border: 1px solid #616161;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
}

#autosuggest__input.autosuggest__input-open {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.autosuggest__results-container {
  position: relative;
  width: 100%;
}

.autosuggest__results {
  font-weight: 300;
  margin: 0;
  position: absolute;
  z-index: 10000001;
  width: 100%;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  background: white;
  padding: 0px;
  max-height: 400px;
  overflow-y: scroll;
}

.autosuggest__results ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.autosuggest__results .autosuggest__results-item {
  cursor: pointer;
  padding: 15px;
}

#autosuggest ul:nth-child(1) > .autosuggest__results_title {
  border-top: none;
}

.autosuggest__results .autosuggest__results-before {
  color: gray;
  font-size: 11px;
  margin-left: 0;
  padding: 15px 13px 5px;
  border-top: 1px solid lightgray;
}

.autosuggest__results .autosuggest__results-item:active,
.autosuggest__results .autosuggest__results-item:hover,
.autosuggest__results .autosuggest__results-item:focus,
.autosuggest__results
  .autosuggest__results-item.autosuggest__results-item--highlighted {
  background-color: #f6f6f6;
}
</style>
