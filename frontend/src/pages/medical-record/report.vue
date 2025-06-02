<template>
  <view class="container">
    <!-- 顶部区域 -->
    <view class="top-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">检测报告</text>
    </view>
    
    <!-- 加载中 -->
    <view v-if="loading" class="loading-container">
      <view class="loading-circle"></view>
      <text class="loading-text">加载中...</text>
    </view>
    
    <!-- 报告内容 -->
    <block v-else>
      <!-- 风险等级卡片 -->
      <view class="risk-card">
        <view class="risk-header">
          <text class="risk-title">脑卒中风险评估</text>
          <text class="risk-date">{{ formatReportDate() }}</text>
        </view>
        
        <view class="risk-level-container">
          <view class="risk-meter">
            <view class="risk-indicator" :style="{ left: `calc(${riskPercentPosition}% - 10rpx)` }"></view>
          </view>
          <view class="risk-labels">
            <text class="risk-label">低风险</text>
            <text class="risk-label">中风险</text>
            <text class="risk-label">高风险</text>
          </view>
        </view>
        
        <view class="risk-percent">
          <text class="percent-value">{{ formatRiskPercent() }}%</text>
          <text class="percent-label">{{ report.riskLevel }}</text>
        </view>
      </view>
      
      <!-- 风险描述 -->
      <view class="info-card">
        <text class="info-title">风险评估</text>
        <text class="info-text">{{ report.riskDescription }}</text>
      </view>
      
      <!-- 健康建议 -->
      <view class="info-card">
        <text class="info-title">健康建议</text>
        <text class="info-text">{{ report.riskAdvice }}</text>
      </view>
      
      <!-- 风险因素详情 -->
      <view v-if="report.details" class="info-card">
        <text class="info-title">风险因素分析</text>
        <view class="details-list">
          <view v-for="(value, key) in report.details" :key="key" class="detail-item">
            <text class="detail-label">{{ formatDetailLabel(key) }}</text>
            <text class="detail-value">{{ formatDetailValue(key, value) }}</text>
          </view>
        </view>
      </view>
      
      <!-- 底部按钮 -->
      <view class="bottom-area">
        <button class="primary-button" hover-class="button-hover" @click="backToHome">返回首页</button>
      </view>
    </block>
  </view>
</template>

<script>
import { formatDate } from '../../utils/index.js';

export default {
  data() {
    return {
      loading: true,
      report: null
    }
  },
  computed: {
    // 计算风险指示器位置（0-100%）
    riskPercentPosition() {
      if (!this.report) return 0;
      return Math.min(Math.max(this.report.riskPercent, 0), 100);
    }
  },
  onLoad() {
    this.loadReport();
  },
  methods: {
    // 返回上一页
    goBack() {
      uni.navigateBack();
    },
    
    // 返回首页
    backToHome() {
      uni.reLaunch({
        url: '/pages/index/index'
      });
    },
    
    // 格式化风险百分比，保留两位小数
    formatRiskPercent() {
      if (!this.report || this.report.riskPercent === undefined) return '0.00';
      return parseFloat(this.report.riskPercent).toFixed(2);
    },
    
    // 格式化报告日期
    formatReportDate() {
      if (!this.report || !this.report.createdAt) return '暂无日期';
      return formatDate(this.report.createdAt, 'YYYY-MM-DD HH:mm');
    },
    
    // 格式化详情标签
    formatDetailLabel(key) {
      const labelMap = {
        'modelScore': '模型评分',
        'ageScore': '年龄因素',
        'bmiScore': 'BMI指数',
        'smokingScore': '吸烟状况',
        'symptomScore': '症状评分'
      };
      
      return labelMap[key] || key;
    },
    
    // 格式化详情值
    formatDetailValue(key, value) {
      // 如果是数字类型且不是整数，保留两位小数
      if (!isNaN(value) && value % 1 !== 0) {
        return parseFloat(value).toFixed(2);
      }
      return value;
    },
    
    // 加载报告数据
    async loadReport() {
      this.loading = true;
      
      try {
        // 先尝试从全局状态获取
        const storeReport = this.$store.state.currentReport;
        
        if (storeReport) {
          this.report = storeReport;
        } else {
          // 否则从API获取
          const userId = this.$store.state.userId;
          const response = await this.$api.detectApi.getReport(userId);
          
          if (response.success && response.report) {
            this.report = response.report;
            this.$store.setCurrentReport(response.report);
          } else {
            uni.showToast({
              title: '获取报告失败',
              icon: 'none'
            });
            setTimeout(() => {
              uni.navigateBack();
            }, 1500);
          }
        }
      } catch (error) {
        console.error('加载报告失败:', error);
        uni.showToast({
          title: '加载报告失败',
          icon: 'none'
        });
        setTimeout(() => {
          uni.navigateBack();
        }, 1500);
      } finally {
        this.loading = false;
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
  padding-bottom: 40rpx;
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

/* 加载状态 */
.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 400rpx;
}
.loading-circle {
  width: 60rpx;
  height: 60rpx;
  border: 6rpx solid #f3f3f3;
  border-top: 6rpx solid #4A6DA7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20rpx;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loading-text {
  font-size: 28rpx;
  color: #a0a4b8;
}

/* 风险卡片 */
.risk-card {
  margin: 30rpx 40rpx;
  padding: 40rpx;
  background-color: #fff;
  border-radius: 30rpx;
  box-shadow: 0 8rpx 30rpx rgba(74, 109, 167, 0.08);
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.risk-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.risk-date {
  font-size: 24rpx;
  color: #999;
}

.risk-level-container {
  margin-bottom: 40rpx;
}

.risk-meter {
  height: 20rpx;
  background: linear-gradient(90deg, 
    #6dc267 0%, 
    #6dc267 33%, 
    #fcc44b 33%, 
    #fcc44b 66%, 
    #f86a6a 66%, 
    #f86a6a 100%
  );
  border-radius: 10rpx;
  position: relative;
  margin-bottom: 10rpx;
}

.risk-indicator {
  position: absolute;
  top: -10rpx;
  left: 0;
  width: 20rpx;
  height: 40rpx;
  background-color: #4A6DA7;
  border-radius: 6rpx;
}

.risk-labels {
  display: flex;
  justify-content: space-between;
}

.risk-label {
  font-size: 24rpx;
  color: #666;
}

.risk-percent {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20rpx;
}

.percent-value {
  font-size: 72rpx;
  font-weight: 700;
  color: #4A6DA7;
  line-height: 1;
}

.percent-label {
  font-size: 30rpx;
  font-weight: 500;
  color: #666;
  margin-top: 10rpx;
}

/* 信息卡片 */
.info-card {
  margin: 30rpx 40rpx;
  padding: 40rpx;
  background-color: #fff;
  border-radius: 30rpx;
  box-shadow: 0 8rpx 30rpx rgba(74, 109, 167, 0.08);
}

.info-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.info-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}

/* 详情列表 */
.details-list {
  margin-top: 20rpx;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 15rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 28rpx;
  color: #666;
}

.detail-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

/* 底部按钮 */
.bottom-area {
  padding: 40rpx;
  margin-top: 20rpx;
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