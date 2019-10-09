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
    ],
    g3d: {},
    data3d: [],
    isLoading: false,
    g3dFile: null
  },
  mutations: {
    SET_G3D(state, g) {
      state.g3d = g
    },
    SET_LOADING_STATUS(state) {
      state.isLoading = !state.isLoading
    },
    SET_DATA3D(state, data) {
      state.data3d = data
    },
    SET_G3D_FILE(state, gf) {
      state.g3dFile = gf
    }
  },
  actions: {
    setG3d({ commit }, g) {
      commit('SET_G3D', g)
    },
    setG3dFile({ commit }, gf) {
      commit('SET_G3D_FILE', gf)
    },
    async fetchData({ commit, state }) {
      commit('SET_LOADING_STATUS')
      const data = await state.g3dFile.readData(
        'chr7',
        27053397,
        27373765,
        20000
      )
      commit('SET_DATA3D', data)
      commit('SET_LOADING_STATUS')
    }
  }
})
