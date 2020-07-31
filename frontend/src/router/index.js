import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import InventoryView from "../views/InventoryView.vue";
import NetworkDiagramView from "../views/NetworkDiagramView.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home
  },
  {
    path: "/inventory",
    name: "InventoryView",
    component: InventoryView
  },
  {
    path: "/diagram",
    name: "NetworkDiagramView",
    component: NetworkDiagramView
  },
  {
    path: "/about",
    name: "About",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import("../views/About.vue")
  }
];

const router = new VueRouter({
  routes
});

export default router;
