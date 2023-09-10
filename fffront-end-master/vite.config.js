import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import importToCDN,{autoComplete } from 'vite-plugin-cdn-import'
export default defineConfig({
  plugins: [
      vue(),
  ],
  base: './',
  resolve: {
      alias: {
      }
  },
  build:{
      rollupOptions:{
      }
  }
})
