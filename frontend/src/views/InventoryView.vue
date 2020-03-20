<template>
  <div>
    <Inventory />
  </div>
</template>

<script>
// @ is an alias to /src
import Inventory from "@/components/Inventory.vue";

export default {
  name: "InventoryView",
  components: {
    Inventory
  }
};
</script>
