<script setup lang="ts">
// App.vue只作为入口，所有内容通过路由加载
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式重置 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

#app {
  height: 100%;
  width: 100%;
}
</style>
