<template>
  <view class="container">
    <!-- 顶部区域 -->
    <view class="top-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">检测进度</text>
    </view>
    
    <!-- 进度区域 -->
    <view class="progress-area">
      <view class="progress-circle-container">
        <view class="progress-circle">
          <view v-if="progress > 0" class="progress-mask" :style="{ transform: `rotate(${firstHalfRotation}deg)` }"></view>
          <view v-if="progress > 50" class="progress-mask-right" :style="{ transform: `rotate(${secondHalfRotation}deg)` }"></view>
          <view class="progress-inner-circle">
            <text class="progress-text">{{ progress }}%</text>
            <text class="progress-status">{{ getStatusText() }}</text>
          </view>
        </view>
      </view>
      
      <!-- 检测中信息 -->
      <view class="info-card">
        <text class="info-title">{{ checkCompleted ? '检测已完成' : '检测正在进行中' }}</text>
        <text class="info-desc">{{ checkCompleted ? '您可以点击下方按钮查看检测结果' : '请耐心等待，系统正在分析您的健康数据...' }}</text>
      </view>
    </view>
    
    <!-- 底部按钮 -->
    <view class="bottom-area">
      <button class="primary-button" hover-class="button-hover" @click="checkResult">
        {{ checkCompleted ? '查看结果' : '刷新进度' }}
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // 检测进度 0-100
      progress: 0,
      // 检测状态 processing, finished
      status: 'processing',
      // 轮询定时器
      timer: null,
      // 是否完成
      checkCompleted: false,
      // 报告获取重试次数
      reportRetryCount: 0,
      // 最大重试次数
      maxRetries: 5,
      // 重试延迟基数（毫秒）
      retryDelayBase: 2000
    }
  },
  computed: {
    // 计算进度对应的角度 (180度 = 50%)
    firstHalfRotation() {
      return Math.min(180, 360 * this.progress / 100);
    },
    // 计算第二部分进度对应的角度 (从50%开始)
    secondHalfRotation() {
      if (this.progress <= 50) return 0;
      return 180 * (this.progress - 50) / 50;
    }
  },
  onLoad() {
    // 加载初始状态
    this.loadStatus();
    // 开始轮询
    this.startPolling();
  },
  onUnload() {
    // 页面卸载时清除定时器
    this.stopPolling();
  },
  methods: {
    // 返回上一页
    goBack() {
      uni.navigateBack();
    },
    
    // 获取状态文本
    getStatusText() {
      if (this.status === 'finished') return '已完成';
      if (this.progress < 30) return '数据准备';
      if (this.progress < 60) return '分析中';
      if (this.progress < 90) return '生成报告';
      return '即将完成';
    },
    
    // 加载检测状态
    async loadStatus() {
      try {
        const userId = this.$store.state.userId;
        const response = await this.$api.detectApi.checkStatus(userId);
        
        if (response.success) {
          this.progress = response.progress || 0;
          this.status = response.status || 'processing';
          
          // 保存到全局状态
          this.$store.setDetectStatus(this.status, this.progress);
          
          // 检查是否完成
          if (this.status === 'finished') {
            this.checkCompleted = true;
            this.stopPolling();
          }
        }
      } catch (error) {
        console.error('获取检测状态失败:', error);
      }
    },
    
    // 开始轮询检测状态
    startPolling() {
      // 每3秒查询一次状态
      this.timer = setInterval(() => {
        this.loadStatus();
      }, 3000);
    },
    
    // 停止轮询
    stopPolling() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },
    
    // 检查结果或刷新进度
    async checkResult() {
      if (this.checkCompleted) {
        // 已完成，获取报告并跳转
        await this.getReport();
      } else {
        // 未完成，刷新进度
        await this.loadStatus();
        uni.showToast({
          title: '已刷新进度',
          icon: 'none'
        });
      }
    },
    
    // 获取检测报告
    async getReport() {
      try {
        uni.showLoading({
          title: '获取报告中...'
        });
        
        const userId = this.$store.state.userId;
        const response = await this.$api.detectApi.getReport(userId);
        
        if (response.success && response.report) {
          // 重置重试计数
          this.reportRetryCount = 0;
          
          // 保存报告到全局状态
          this.$store.setCurrentReport(response.report);
          
          // 跳转到报告页
          uni.navigateTo({
            url: '/pages/medical-record/report'
          });
        } else {
          this.handleReportRetry();
        }
      } catch (error) {
        console.error('获取报告失败:', error);
        this.handleReportRetry();
      } finally {
        uni.hideLoading();
      }
    },
    
    // 处理报告获取重试
    handleReportRetry() {
      if (this.reportRetryCount < this.maxRetries) {
        this.reportRetryCount++;
        
        // 计算指数退避延迟时间
        const delay = this.retryDelayBase * Math.pow(2, this.reportRetryCount - 1);
        
        uni.showToast({
          title: `报告生成中，${Math.round(delay/1000)}秒后重试...`,
          icon: 'none',
          duration: 2000
        });
        
        // 延迟后重试
        setTimeout(() => {
          this.getReport();
        }, delay);
      } else {
        uni.showToast({
          title: '获取报告失败，请稍后再试',
          icon: 'none'
        });
      }
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
  background-color: #f8f9fd;
  position: relative;
}

/* 顶部区域 */
.top-area {
  padding: 60rpx 40rpx 20rpx;
  display: flex;
  align-items: center;
}

.back-button {
  width: 70rpx;
  height: 70rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(74, 109, 167, 0.1);
  cursor: pointer;
}

.back-icon {
  font-size: 40rpx;
  color: #4A6DA7;
}

.page-title {
  margin-left: 20rpx;
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

/* 进度区域 */
.progress-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx;
}

.progress-circle-container {
  position: relative;
  width: 400rpx;
  height: 400rpx;
  margin-bottom: 60rpx;
}

.progress-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #e0e5f0;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8rpx 30rpx rgba(74, 109, 167, 0.12);
}

.progress-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background-color: #4A6DA7;
  transform-origin: right center;
  z-index: 1;
}

.progress-mask-right {
  position: absolute;
  top: 0;
  left: 50%;
  width: 50%;
  height: 100%;
  background-color: #4A6DA7;
  transform-origin: left center;
  z-index: 1;
}

.progress-inner-circle {
  position: absolute;
  top: 40rpx;
  left: 40rpx;
  right: 40rpx;
  bottom: 40rpx;
  border-radius: 50%;
  background-color: #fff;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.progress-text {
  font-size: 80rpx;
  font-weight: 700;
  color: #4A6DA7;
  margin-bottom: 10rpx;
}

.progress-status {
  font-size: 28rpx;
  color: #a0a4b8;
}

/* 信息卡片 */
.info-card {
  background-color: #fff;
  border-radius: 30rpx;
  padding: 40rpx;
  width: 85%;
  box-shadow: 0 8rpx 30rpx rgba(74, 109, 167, 0.08);
  margin-top: 40rpx;
}

.info-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
  text-align: center;
}

.info-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  text-align: center;
  display: block;
}

/* 底部按钮 */
.bottom-area {
  padding: 40rpx;
  margin-top: auto;
}

.primary-button {
  width: 80%;
  height: 90rpx;
  margin: 0 auto;
  background: linear-gradient(90deg, #4A6DA7 60%, #6fa8dc 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 45rpx;
  box-shadow: 0 8rpx 20rpx rgba(74, 109, 167, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.button-hover {
  transform: scale(0.96);
  opacity: 0.9;
  box-shadow: 0 4rpx 10rpx rgba(74, 109, 167, 0.15);
}
</style> 