<template>
  <div class="home">
    <el-card class="welcome">
      <h2>欢迎使用玩家行为分析系统</h2>
      <p>
        本系统用于对玩家行为数据进行采集、特征构建、聚类分析与标签生成，
        帮助你快速构建玩家画像并进行精细化运营分析。
      </p>
    </el-card>

    <el-row :gutter="20" class="quick">
      <el-col :span="8">
        <el-card>
          <h3>标签分析</h3>
          <p>查看玩家标签分布与画像</p>
          <el-button type="primary" @click="goTag">
            进入
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <h3>分析控制台</h3>
          <p>生成特征、执行聚类与标签</p>
          <el-button type="success" @click="goAnalysis">
            进入
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <h3>模拟端</h3>
          <p>模拟玩家行为数据产生处，点击进入控制页面</p>
          <el-button type="warning" @click="openSimulator">
            打开
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();

const goTag = () => router.push("/tags");
const goAnalysis = () => router.push("/system-control");
const openSimulator = () =>
  //window.open("http://localhost:8081/", "_blank");
window.open("http://www.baidu.com", "_blank");
</script>

<style scoped>
.home {
  width: 100%;
  padding: 10px 20px;
  box-sizing: border-box;
}

.welcome {
  margin-bottom: 30px;
}

.quick h3 {
  margin-bottom: 10px;
}
</style>
