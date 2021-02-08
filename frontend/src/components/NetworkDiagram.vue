<template>
  <container>
    <h1 class="title has-text-centered">Network Diagram based on LLDP</h1>
    <network
      class="diagram"
      ref="network"
      :nodes="nodes"
      :edges="edges"
      :options="options"
    />
  </container>
</template>

<script>
import axios from "axios";
// import { Network } from "vue-visjs";
import { Network } from "@vue2vis/network";
// Vue.component("network", vue2vis.Network);
export default {
  name: "NetworkDiagram",
  components: {
    // Timeline,
    // DataSet,
    Network,
  },
  data: function () {
    return {
      //   count: 200,
      nodes: [],
      edges: [],
      options: {
        layout: {
          randomSeed: 10,
        },
        physics: {
          enabled: true,
          // barnesHut: {
          //   springConstant: 0.9,
          //   avoidOverlap: 10
          // },
          // maxVelocity: 1,
          // minVelocity: 10,
          // solver: "barnesHut",
          // stabilization: {
          //   enabled: true,
          //   iterations: 1,
          //   onlyDynamicEdges: true,
          //   fit: true
          // },
          // timestep: 0.5,
          // adaptiveTimestep: true
        },
        interaction: {
          dragNodes: true,
        },
        stabilization: false,
        hierarchical: {
          enabled: true,
          // levelSeparation: 300, // does not seem to work, 150 default
          // nodeSpacing: 250, // 100 default
          direction: "UD", // UD, DU, LR, RL
          sortMethod: "directed", // hubsize, directed
        },
      },
    };
  },
  mounted() {
    axios.get("/api/network/lldp").then((response) => {
      this.nodes = response.data.nodes;
      this.edges = response.data.edges;
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<!-- <style src="vis-timeline/dist/vis-timeline-graph2d.css"></style> -->
<style scoped lang="scss">
.diagram {
  height: 800px;
}
</style>
