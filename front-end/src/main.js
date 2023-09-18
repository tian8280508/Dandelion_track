import {createApp} from 'vue'
import ElementPlus from 'element-plus'  //引入插件
import 'element-plus/theme-chalk/index.css' //默认css样式
import zhCn from 'element-plus/es/locale/lang/zh-cn'   //引入中文包
import axios from 'axios';
import App from './App.vue'

let app = createApp(App)
app.use(ElementPlus,{locale:zhCn})   // use

app.config.globalProperties.$http = axios
axios.defaults.baseURL = 'http://127.0.0.1:5000/'

app.mount('#app')





