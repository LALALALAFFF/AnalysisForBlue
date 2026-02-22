<template>
  <div class="tag-dashboard">

    <!-- 全体标签分布 -->
    <el-card class="box">
      <h2>全体玩家标签分布</h2>

      <div
        v-for="(group, index) in globalGroups"
        :key="group.code"
        class="chart-box"
      >
        <div :id="`chart-${index}`" class="chart"></div>
      </div>
    </el-card>

    <el-divider />

    <!-- 单个玩家 -->
    <el-card class="box">
      <h2>查询玩家标签</h2>

      <el-input
        v-model="queryUid"
        placeholder="输入玩家ID"
        style="width:200px;margin-right:10px"
      />

      <el-button type="primary" @click="loadUserTags">查询</el-button>

      <div v-if="userTags" class="tag-list">
        <el-tag
          v-for="(tag, category) in userTags"
          :key="category"
          type="success"
        >
          {{ category }}：{{ tag }}
        </el-tag>
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue"
import * as echarts from "echarts"
import axios from "axios"

const globalGroups = ref([])
const queryUid = ref("")
const userTags = ref(null)

// ① 全体标签分布
const loadGlobalTags = async () => {
  const res = await axios.get("/analysis/tag-distribution/")
  globalGroups.value = res.data.data

  await nextTick()

  globalGroups.value.forEach((group, index) => {
    const el = document.getElementById(`chart-${index}`)
    const chart = echarts.init(el)

    chart.setOption({
      title: {
        text: group.category,
        left: "center"
      },
      tooltip: { trigger: "item" },
      series: [{
        type: "pie",
        radius: "60%",
        data: group.data
      }]
    })
  })
}

// ② 单个玩家标签
const loadUserTags = async () => {
  if (!queryUid.value) return

  const res = await axios.get(`/analysis/player-tags/${queryUid.value}/`)
  userTags.value = res.data.tags
}

onMounted(loadGlobalTags)
</script>

<style>
/* 🌈 全局背景图 —— 不能加 scoped */
body {
  background-image: url("@/components/icons/tag_bg.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed; /* 页面滚动背景不动 */
  min-height: 100vh;
}
</style>

<style scoped>
.tag-dashboard {
  width: 900px;
  margin: 20px auto;
  padding: 30px;
  background: rgba(255, 255, 255, 0.75);
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.box {
  margin-bottom: 30px;
}

.chart-box {
  display: inline-block;
}

.chart {
  width: 600px;
  height: 400px;
  margin: 20px auto;
}

.tag-list {
  margin-top: 20px;
}
</style>
