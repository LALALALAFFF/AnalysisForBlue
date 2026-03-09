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

    <!-- 特征构建任务 -->
    <div class="task-row">
      <el-switch
        v-model="featureTimer"
        active-text="定时生成特征向量"
        @change="val => toggle('build_feature', val, featureInterval)"
      />

      <span class="interval-label">间隔(分钟)：</span>

      <el-input-number
        v-model="featureInterval"
        :min="1"
        size="small"
      />
    </div>

    <br />

    <!-- 打标签任务 -->
    <div class="task-row">
      <el-switch
        v-model="tagTimer"
        active-text="定时打标签"
        @change="val => toggle('run_tags', val, tagInterval)"
      />

      <span class="interval-label">间隔(分钟)：</span>

      <el-input-number
        v-model="tagInterval"
        :min="1"
        size="small"
      />
    </div>

  </el-card>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"

const featureTimer = ref(false)
const tagTimer = ref(false)

const featureInterval = ref(10)
const tagInterval = ref(10)

const buildFeature = () => {
  axios.get("/analysis/control/build-features/")
}

const runTags = () => {
  axios.get("/analysis/control/run-dbscan/")
}

const toggle = (task, enabled, interval) => {

  axios.get("/analysis/control/task-switch/", {
    params: {
      task,
      enabled,
      interval
    }
  }).then(res => {
    console.log("任务状态更新：", res.data)
  })
}
</script>

<style scoped>
.panel {
  width: 600px;
  margin: 40px auto;
  padding: 30px;
}

.task-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.interval-label {
  font-size: 14px;
}
</style>
