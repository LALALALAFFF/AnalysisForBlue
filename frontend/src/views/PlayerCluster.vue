<template>
  <div class="container">

    <!-- 标题 -->
    <h2>玩家聚类分析可视化</h2>

    <!-- 聚类标签分布图 -->
    <div id="clusterChart" style="width: 600px; height: 400px;"></div>

    <h3>玩家聚类结果列表</h3>
    <table border="1" style="width: 600px; text-align:center">
      <thead>
        <tr>
          <th>玩家 ID</th>
          <th>聚类 ID</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in players" :key="p.player_id">
          <td>{{ p.player_id }}</td>
          <td>{{ p.cluster_id }}</td>
          <td>
            <button @click="viewPlayer(p.player_id)">查看玩家画像</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="selectedPlayer">
      <h3>玩家画像信息（ID: {{ selectedPlayer.player_id }}）</h3>
      <p>标签：{{ selectedPlayer.player_tag }}</p>
      <p>聚类 ID：{{ selectedPlayer.cluster_id }}</p>
      <p>总在线时长：{{ selectedPlayer.total_play_time }}</p>
      <p>登录频率：{{ selectedPlayer.login_frequency }}</p>
      <p>消费金额：{{ selectedPlayer.consume_amount }}</p>
      <p>对战次数：{{ selectedPlayer.battle_count }}</p>
      <p>胜率：{{ selectedPlayer.win_rate }}</p>
      <p>社交互动：{{ selectedPlayer.social_interaction }}</p>
    </div>

  </div>
</template>


<script setup>
import { ref, onMounted, nextTick } from "vue";
import axios from "axios";
import * as echarts from "echarts";
axios.defaults.withCredentials = true;

// 静态数据
const clusterDistribution = { "0": 17, "1": 17, "2": 16 };
const players = ref([
  { player_id: 1, cluster_id: 0 },
  { player_id: 2, cluster_id: 1 },
  { player_id: 3, cluster_id: 2 },
  { player_id: 4, cluster_id: 0 },
]);

const playerProfiles = {
  1: {
    player_tag: "氪金大佬",
    cluster_id: 0,
    total_play_time: 1200,
    login_frequency: 15,
    consume_amount: 600,
    battle_count: 50,
    win_rate: 0.6,
    social_interaction: 30
  },
  2: {
    player_tag: "PVP 重度玩家",
    cluster_id: 1,
    total_play_time: 900,
    login_frequency: 12,
    consume_amount: 200,
    battle_count: 120,
    win_rate: 0.7,
    social_interaction: 20
  },
  3: {
    player_tag: "社交型玩家",
    cluster_id: 2,
    total_play_time: 400,
    login_frequency: 8,
    consume_amount: 50,
    battle_count: 30,
    win_rate: 0.4,
    social_interaction: 60
  },
  4: {
    player_tag: "普通玩家",
    cluster_id: 0,
    total_play_time: 300,
    login_frequency: 5,
    consume_amount: 0,
    battle_count: 10,
    win_rate: 0.3,
    social_interaction: 10
  },
};

const selectedPlayer = ref(null);
let clusterChart = null;

// 生成聚类分布图
const renderChart = () => {
  const chartDom = document.getElementById("clusterChart");
  if (!clusterChart) clusterChart = echarts.init(chartDom);

  clusterChart.setOption({
    title: { text: "聚类分布图" },
    tooltip: {},
    xAxis: { type: "category", data: Object.keys(clusterDistribution) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: Object.values(clusterDistribution) }]
  });
};

// 查看玩家画像（静态）
const viewPlayer = (id) => {
  selectedPlayer.value = playerProfiles[id];
};

onMounted(() => {
  renderChart();
  // 监听窗口 resize
  window.addEventListener("resize", () => {
    if (clusterChart) clusterChart.resize();
  });
});
/*
const players = ref([]);
const selectedPlayer = ref(null);
let clusterChart = null;  // ECharts 图表实例

// 🚀 加载聚类分布图
const loadDistribution = async () => {
  try {
    const res = await axios.get("/analysis/cluster/distribution");

    if (!res.data || res.data.status !== "success") {
      console.error("后端返回错误：", res.data);
      return;
    }

    const dist = res.data.cluster_distribution || {};
    const keys = Object.keys(dist);
    const values = Object.values(dist);

    console.log("聚类数据：", keys, values);

    // 等待 DOM 完全渲染后初始化图表
    await nextTick();

    const chartDom = document.getElementById("clusterChart");

    if (!chartDom) {
      console.error("❌ clusterChart DOM 未找到");
      return;
    }

    // 若已初始化，先销毁避免重复绑定
    if (clusterChart) {
      clusterChart.dispose();
    }

    clusterChart = echarts.init(chartDom);

    clusterChart.setOption({
      title: { text: "聚类分布图", left: "center" },
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: keys, name: "聚类ID" },
      yAxis: { type: "value", name: "玩家数量" },
      series: [
        {
          type: "bar",
          data: values,
          barWidth: 40,
        },
      ],
    });

    // 强制 resize（关键修复点）
    setTimeout(() => {
      clusterChart.resize();
    }, 50);

  } catch (err) {
    console.error("聚类分布加载失败：", err);
  }
};

// 🚀 加载聚类结果列表
const loadClusterResults = async () => {
  try {
    const res = await axios.get("/analysis/results");
    players.value = res.data;
  } catch (e) {
    console.error("聚类结果加载失败", e);
  }
};

// 🚀 加载某玩家画像信息
const viewPlayer = async (id) => {
  try {
    const res = await axios.get(`/analysis/player/${id}`);
    selectedPlayer.value = res.data;
  } catch (e) {
    console.error("玩家画像加载失败", e);
  }
};

// 页面加载后执行
onMounted(async () => {
  await loadClusterResults();
  await loadDistribution();

  // 图表自适应窗口变化
  window.addEventListener("resize", () => {
    if (clusterChart) clusterChart.resize();
  });
});*/
</script>



<style>
.container {
  padding: 20px;
}
table {
  margin-top: 20px;
  border-collapse: collapse;
}
</style>
