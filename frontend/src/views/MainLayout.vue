<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="logo">玩家行为分析系统</div>
    </el-header>

    <el-container class="content">
      <el-aside width="220px" class="aside">
        <el-menu router class="menu">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/tags">标签分析</el-menu-item>
          <el-menu-item index="/system-control">分析控制台</el-menu-item>
          <el-menu-item @click="openSimulator">打开模拟端</el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background-color: #1f2937;
  color: #fff;
}

.content {
  flex: 1;
  display: flex;
  width: 100%;
}

.aside {
  background-color: #f9fafb;
  border-right: 1px solid #e5e7eb;
}

.menu {
  border-right: none;
}

.main {
  flex: 1;
  width: 100%;
  background-color: #f5f7fa;
  padding: 30px;
  overflow-y: auto;
}
</style>
