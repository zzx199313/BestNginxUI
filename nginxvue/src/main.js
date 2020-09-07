import Vue from 'vue'
import App from './App.vue'
import router from './router'

// 配置axios发送请求
import axios from 'axios'
// 配置请求的根路径
let baseURL = window.Glob.BaseUrl

axios.defaults.baseURL = baseURL
//配置请求拦截器
axios.interceptors.request.use(config => {
  // console.log(config)
  config.headers.Authorization = 'Bearer' + ' ' + window.sessionStorage.getItem('BestNginxUItoken')
  return config
})
//配置响应拦截器
axios.interceptors.response.use(
  response => {
    return response
       },
    
  error => {
    if (error.response){
      if (error.response.status === 401) {
        // console.log(error.response)
        Message.error('token已过期请重新登录')
        
      }
    }
    else {
      Message.error('网络异常')
      // console.log(error)
    }
    return Promise.reject(error)
  }
)

Vue.prototype.$http=axios

//全局挂在element-ui消息提示组件
Vue.prototype.$message= Message

//手动导入element-ui
import ElementUI, { Message } from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
Vue.use(ElementUI)

//导入字体图标
import './assets/fonts/iconfont.css'
// 导入全局样式
import './assets/css/global.css'

Vue.config.productionTip = false

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
