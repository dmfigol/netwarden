import Vue from "vue";
import VueMeta from "vue-meta";
import App from "./App.vue";
import router from "./router";
import Buefy from "buefy";
import "buefy/dist/buefy.css";

Vue.use(Buefy);
Vue.use(VueMeta);

new Vue({
  router,
  render: (h) => h(App),
}).$mount("#app");
