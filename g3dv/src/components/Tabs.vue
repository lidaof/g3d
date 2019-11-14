<template>
  <div>
    <div class="tabs">
      <ul>
        <li
          v-for="tab in tabs"
          :key="tab.name"
          :class="{ 'is-active': tab.isActive }"
        >
          <span @click="selectTab(tab)">{{ tab.name }}</span>
        </li>
      </ul>
    </div>

    <div class="tabs-details">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Tabs',
  data() {
    return { tabs: [] }
  },

  created() {
    this.tabs = this.$children
  },
  methods: {
    selectTab(selectedTab) {
      this.tabs.forEach(tab => {
        tab.isActive = tab.name == selectedTab.name
      })
    }
  }
}
</script>

<style scoped>
ul {
  list-style: none;
  padding: 0;
}
.tabs {
  white-space: nowrap;
}

.tabs ul {
  display: flex;
  flex-grow: 1;
  flex-shrink: 0;
  justify-content: flex-start;
}
.tabs li {
  display: block;

  align-items: center;
  border-bottom: 1px solid #dbdbdb;
  color: #4a4a4a;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  justify-content: center;
  margin-bottom: -1px;
  padding: 0.5em 1em;
  cursor: pointer;
  transition: none 86ms ease-out;
}

.tabs li.is-active {
  border-bottom-color: #00d1b2;
  color: #00d1b2;
}
</style>
