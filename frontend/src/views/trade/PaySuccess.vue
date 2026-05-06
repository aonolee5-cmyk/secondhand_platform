<template>
  <div class="success-page">
    <el-result icon="success" title="支付成功" sub-title="订单已支付，请耐心等待卖家发货">
      <template #extra>
        <div class="btn-group">
          <el-button type="primary" @click="$router.push('/user/orders')">查看该订单</el-button>
          <el-button @click="$router.push('/')">继续逛逛</el-button>
        </div>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const viewThisOrder = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const orderId = urlParams.get('id') || route.query.id;

  console.log("--- 成功页状态检查 ---");
  console.log("从 URL 强抓到的 ID:", orderId);
  console.log("从路由对象拿到的 ID:", route.query.id);

  if (orderId && orderId !== 'undefined') {
    router.push(`/order-detail/${orderId}`);
  } else {
    ElMessage.error('抱歉，未能获取该订单详情，请在列表查看');
    router.push('/user/orders');
  }
};
</script>


<style scoped>
.success-container { padding-top: 80px; }
.actions { display: flex; gap: 20px; justify-content: center; }
</style>