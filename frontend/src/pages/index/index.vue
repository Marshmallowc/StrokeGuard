<template>
  <view class="container">
    <!-- 标题 -->
    <view class="title-container">
      <text class="title">StrokeGuard</text>
    </view>
    
    <!-- 按钮区域 -->
    <view class="button-container">
      <!-- 开始检测按钮 -->
      <view class="button primary-button" hover-class="button-hover" @click="handleCheckClick">
        <text class="icon check-icon">✓</text>
        <text class="button-text">开始检测</text>
      </view>
      
      <!-- 我的病历按钮 -->
      <view class="button secondary-button" hover-class="button-hover" @click="handleHistoryClick">
        <text class="icon file-icon">📄</text>
        <text class="button-text">我的病历</text>
      </view>
    </view>
  </view>
</template>

<script>
import { generateUniqueId } from '../../utils/index.js';

export default {
  data() {
    return {
      loading: false
    }
  },
  onLoad() {
    this.initUserId();
    this.checkHealth();
  },
  methods: {
    // 初始化用户ID
    initUserId() {
      if (!this.$store.state.userId) {
        const userId = generateUniqueId();
        this.$store.setUserId(userId);
        console.log('初始化用户ID:', userId);
      }
    },
    
    // 健康检查
    async checkHealth() {
      try {
        const response = await this.$api.otherApi.healthCheck();
        console.log('后端健康状态:', response);
      } catch (error) {
        console.error('健康检查失败:', error);
      }
    },
    
    // 开始检测
    async handleCheckClick() {
      if (this.loading) return;
      
      this.loading = true;
      try {
        // 跳转到检测方式选择页面
        uni.navigateTo({
          url: '/pages/detect/detect-method'
        });
      } catch (error) {
        console.error('导航失败:', error);
      } finally {
        this.loading = false;
      }
    },
    
    // 查看病历
    handleHistoryClick() {
      uni.navigateTo({
        url: '/pages/medical-record/medical-record'
      });
    }
  }
}
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
  padding: 0 20rpx;
  position: relative;
}

/* 标题样式 */
.title-container {
  display: flex;
  justify-content: center;
  position: absolute;
  top: 40%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
}

.title {
  font-size: 80rpx;
  font-weight: 400;
  color: #4A6DA7;
}

/* 按钮区域样式 */
.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 50rpx;
  position: absolute;
  top: 60%;
  left: 0;
  right: 0;
}

.button {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 70%;
  max-width: 500rpx;
  height: 100rpx;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.button:hover {
  transform: translateY(-3rpx);
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.15);
}

.button-hover {
  transform: scale(0.95);
  opacity: 0.9;
  box-shadow: 0 1rpx 5rpx rgba(0, 0, 0, 0.1);
}

.primary-button {
  background-color: #4A6DA7;
  color: white;
}

.primary-button:hover {
  background-color: #5b7db5;
}

.secondary-button {
  background-color: white;
  color: #4A6DA7;
  border: 1rpx solid #e5e5e5;
}

.secondary-button:hover {
  background-color: #f8f9fc;
  border-color: #4A6DA7;
}

.icon {
  margin-right: 12rpx;
  font-size: 32rpx;
}

.check-icon {
  color: white;
}

.file-icon {
  font-size: 36rpx;
}

.button-text {
  font-size: 30rpx;
}
</style>
