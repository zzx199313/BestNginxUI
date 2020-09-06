import Vue from 'vue'
import VueRouter from 'vue-router'

import Login from '../components/Login.vue'
import Home from '../components/Home.vue'
import Welcome from '../components/Welcome.vue'

import Users  from '../components/users/Users.vue'
import Auth from '../components/users/Auth.vue'
import Msgs from '../components/msgs/Msgs.vue'

import Config from '../components/nginx/Config.vue'
import Upstreams from '../components/nginx/Upsreams.vue'
import Backup from '../components/nginx/Backup.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { 
    path: '/home', 
    component: Home,
    redirect:'/welcome',
    children: [
      { path: '/welcome', component: Welcome },
      { path: '/:ip/config', component: Config },
      { path: '/:ip/upstreams', component: Upstreams },
      { path: '/:ip/backup', component: Backup },
  ]},

]

const router = new VueRouter({
  routes
})

//挂载全局路由导航守卫
router.beforeEach((to, from, next) => {
  //to 将要访问的路径
  //from 代表从哪个路径跳转而来
  //next 是一个函数，表示放行
  if (to.path === '/login') return next()

  //获取token
  const tokenStr = window.sessionStorage.getItem('BestNginxUItoken');
  if (!tokenStr) return next('/login');
  next()
})


export default router
