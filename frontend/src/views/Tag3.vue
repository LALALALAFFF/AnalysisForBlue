<template>
  <div class="tag-dashboard">

    <!-- ===== 全体标签分布 ===== -->
    <el-card class="box">
      <h2>全体玩家标签分布</h2>

      <div class="chart-grid">
        <div
          v-for="(group, index) in globalGroups"
          :key="group.code"
          class="chart-wrapper"
        >
          <div :id="`chart-${index}`" class="chart"></div>
        </div>
      </div>
    </el-card>

    <el-divider />

    <!-- ===== 单个玩家标签 ===== -->
    <el-card class="box">
      <h2>查询玩家标签</h2>

      <el-input
        v-model="queryUid"
        placeholder="输入玩家ID"
        style="width:200px;margin-right:10px"
      />

      <el-button type="primary" @click="loadUserTags">
        查询
      </el-button>

      <div v-if="userTags" class="tag-list">
        <el-tag
          v-for="(tag, category) in userTags"
          :key="category"
          :type="getTagType(tag)"
          effect="dark"
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

/* ======================
   ① 全体标签分布（多个饼图）
====================== */
const loadGlobalTags = async () => {
  const res = await axios.get("/analysis/tag-distribution/")
  globalGroups.value = res.data.data

  await nextTick()

  globalGroups.value.forEach((group, index) => {
    const el = document.getElementById(`chart-${index}`)
    if (!el) return

    const chart = echarts.init(el)

    chart.setOption({
      title: {
        text: group.category,
        left: "center",
        top: 10,
        textStyle: { fontSize: 14 }
      },
      tooltip: { trigger: "item" },
      series: [
        {
          type: "pie",
          radius: ["30%", "65%"],
          center: ["50%", "58%"],  // 往下/中间收，给 label 缓冲
          data: group.data,
          avoidLabelOverlap: true,  // 防止文字重叠

          label: {
            show: true,
            position: "outside",
            width: 110,        // 给 label 足够宽度
            overflow: "break",
            lineHeight: 16,
            formatter: params => `${params.name}\n${params.percent}%`
          },

          labelLine: {
            show: true,
            length: 18,
            length2: 12
          }
        }
      ]
    })
  })
}
const getTagType = (tag) => {
  if (tag === "低") return "success"   // 绿色
  if (tag === "中") return "warning"   // 橙色
  if (tag === "高") return "danger"    // 红色
  return "info"
}
/* ======================
   ② 单个玩家标签
====================== */
const loadUserTags = async () => {
  if (!queryUid.value) return

  const res = await axios.get(`/analysis/player-tags/${queryUid.value}/`)
  userTags.value = res.data.tags
}

onMounted(loadGlobalTags)
</script>

<!-- 🌈 全局背景（不能 scoped） -->
<style>
body {
  background-image: url("@/components/icons/tag_bg.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  min-height: 100vh;
}
</style>

<style scoped>
.tag-dashboard {
  width: 95%;  /* 全屏布局更友好 */
  max-width: 1400px; /* 可选，防止超大屏撑爆 */
  margin: 20px auto;
  padding: 30px;
  background: rgba(255, 255, 255, 0.78);
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.box {
  margin-bottom: 30px;
}

/* ===== 饼图网格：自适应大屏 ===== */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(540px, 1fr));
  gap: 30px 20px;
  justify-items: center;
}

.chart-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* 饼图大小（已为标签预留空间） */
.chart {
  width: 520px;  /* 扩大容器，防止 label 被裁剪 */
  height: 380px;
}

/* ===== 玩家标签 ===== */
.tag-list {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
