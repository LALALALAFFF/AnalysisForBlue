import { createRouter, createWebHistory } from 'vue-router'

import Home from "@/views/Home.vue";
import Tag3 from "@/views/Tag3.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('../views/MainLayout.vue'),
      children: [
        {
          path: '/',
          name: 'home',
          component: Home,
        },
        {
          path: '/about',
          name: 'about',
          component: () => import('../views/AboutView.vue'),
        },
        {
          path: '/PlayerCluster',
          name: 'PlayerCluster',
          component: () => import('../views/PlayerCluster.vue'),
        },
        {
          path: "/tags",
          name: "Tags",
          component: Tag3,
        },
        {
          path: "/system-control",
          component: () => import('../views/SystemControl.vue'),
        }
      ]
    },

  ],
})

export default router
