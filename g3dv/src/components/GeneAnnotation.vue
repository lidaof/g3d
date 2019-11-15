<template>
  <div class="gene" @click="setGene(gene)">
    <div>{{ gene.collection }} {{ gene.name }} ({{ gene.id }})</div>
    <div>{{ gene.chrom }}:{{ gene.txStart }}-{{ gene.txEnd }}</div>
    <div>
      {{ gene.description }}
    </div>
  </div>
</template>

<script>
export default {
  props: {
    gene: Object
  },
  methods: {
    setGene(gene) {
      console.log('anno', gene)
      this.$emit('onSetGene', gene)
    }
  }
}
</script>

<style>
.gene {
  font-size: 80%;
}
</style>
