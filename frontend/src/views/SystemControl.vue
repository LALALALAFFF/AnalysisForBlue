<template>
  <el-card class="panel">
    <h2>系统分析控制台</h2>

    <el-divider>手动任务</el-divider>

    <el-button type="primary" @click="buildFeature">
      生成特征向量
    </el-button>

    <el-button type="success" @click="runTags">
      给所有玩家打标签
    </el-button>

    <el-divider>定时任务</el-divider>

    <el-switch
      v-model="featureTimer"
      active-text="定时生成特征向量"
      @change="toggle('build_feature', featureTimer)"
    />

    <br /><br />

    <el-switch
      v-model="tagTimer"
      active-text="定时打标签"
      @change="toggle('run_tags', tagTimer)"
    />
  </el-card>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"

const featureTimer = ref(false)
const tagTimer = ref(false)

const buildFeature = () => {
  axios.get("/analysis/control/build-feature/")
}

const runTags = () => {
  axios.get("/analysis/control/run-tags/")
}

const toggle = (task, enabled) => {
  axios.get("/analysis/control/task-switch/", {
    params: { task, enabled }
  })
}
</script>

<style scoped>
.panel {
  width: 600px;
  margin: 40px auto;
  padding: 30px;
}
</style>
