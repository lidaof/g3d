import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    resolutions: [
      200000,
      180000,
      160000,
      140000,
      120000,
      100000,
      80000,
      60000,
      40000,
      20000
    ]
  },
  mutations: {},
  actions: {}
})
