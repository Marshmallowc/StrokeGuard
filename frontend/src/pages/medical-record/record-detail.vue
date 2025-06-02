<template>
  <view class="container">
    <!-- 顶部区域 -->
    <view class="header-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">病历详情</text>
      <button class="home-btn-top" hover-class="btn-hover" @click="goHome">返回首页</button>
    </view>

    <!-- 内容区域 -->
    <view class="content-wrapper">
      <!-- 用户基本信息卡片 -->
      <view class="info-card">
        <view class="card-header">
          <text class="card-title">基本信息</text>
          <view class="risk-badge" :class="[riskLevel.class]">
            <text>{{ riskLevel.text }}</text>
          </view>
        </view>
        <view class="divider"></view>
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">年龄</text>
            <text class="info-value">{{ basicInfo.age || '--' }} 岁</text>
          </view>
          <view class="info-item">
            <text class="info-label">性别</text>
            <text class="info-value">{{ basicInfo.gender || '--' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">身高</text>
            <text class="info-value">{{ basicInfo.height || '--' }} cm</text>
          </view>
          <view class="info-item">
            <text class="info-label">体重</text>
            <text class="info-value">{{ basicInfo.weight || '--' }} kg</text>
          </view>
          <view class="info-item">
            <text class="info-label">BMI</text>
            <text class="info-value">{{ bmi }}</text>
          </view>
        </view>
      </view>

      <!-- 生活方式卡片 -->
      <view class="info-card">
        <view class="card-header">
          <text class="card-title">生活方式</text>
        </view>
        <view class="divider"></view>
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">婚姻状况</text>
            <text class="info-value">{{ lifestyleInfo.maritalStatus || '--' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">工作类型</text>
            <text class="info-value">{{ lifestyleInfo.workType || '--' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">居住类型</text>
            <text class="info-value">{{ lifestyleInfo.residenceType || '--' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">抽烟状况</text>
            <text class="info-value">{{ lifestyleInfo.smokingStatus || '--' }}</text>
          </view>
        </view>
      </view>

      <!-- 症状卡片 -->
      <view class="info-card">
        <view class="card-header">
          <text class="card-title">症状记录</text>
        </view>
        <view class="divider"></view>
        <view v-if="symptoms && symptoms.length > 0" class="symptom-grid">
          <view v-for="(symptom, index) in symptoms" :key="index" class="symptom-tag">
            <text class="symptom-emoji">{{ symptom.emoji || '❓' }}</text>
            <text class="symptom-text">{{ symptom.label || '未知症状' }}</text>
          </view>
        </view>
        <view v-else class="empty-symptoms">
          <text>无症状记录</text>
        </view>
      </view>

      <!-- 风险评估卡片 -->
      <view class="info-card risk-card">
        <view class="card-header">
          <text class="card-title">风险评估</text>
        </view>
        <view class="divider"></view>
        <view class="risk-assessment">
          <view class="risk-chart">
            <view class="risk-indicator" :style="{ width: riskPercent + '%' }"></view>
          </view>
          <view class="risk-detail">
            <text class="risk-percent">{{ formatRiskPercent() }}%</text>
            <text class="risk-desc">{{ riskDescription }}</text>
          </view>
          <text class="risk-advice">{{ riskAdvice }}</text>
        </view>
      </view>
    </view>

    <!-- 底部按钮区域 -->
    <view class="bottom-area">
      <view class="button-row">
        <button class="action-btn print-btn" hover-class="btn-hover" @click="printRecord">
          打印病历
        </button>
        <button class="action-btn share-btn" hover-class="btn-hover" @click="shareRecord">
          分享病历
        </button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      basicInfo: {
        age: '',
        gender: '',
        height: '',
        weight: ''
      },
      lifestyleInfo: {
        maritalStatus: '',
        workType: '',
        residenceType: '',
        smokingStatus: ''
      },
      symptoms: [],
      riskPercent: 25, // 示例风险百分比
      riskLevel: {
        text: '低风险',
        class: 'low-risk'
      },
      riskDescription: '您的脑卒中风险较低',
      riskAdvice: '建议保持健康的生活方式，定期体检，控制血压和血糖。'
    }
  },
  computed: {
    bmi() {
      if (!this.basicInfo.height || !this.basicInfo.weight) return '--';
      const height = this.basicInfo.height / 100; // 转换为米
      const bmi = (this.basicInfo.weight / (height * height)).toFixed(1);
      return bmi;
    }
  },
  onLoad() {
    this.loadUserData();
  },
  methods: {
    goBack() {
      uni.navigateBack();
    },
    goHome() {
      // 返回到首页
      uni.reLaunch({
        url: '/pages/index/index'
      });
    },
    // 格式化风险百分比，保留两位小数
    formatRiskPercent() {
      return parseFloat(this.riskPercent).toFixed(2);
    },
    async loadUserData() {
      try {
        uni.showLoading({ title: '加载中...' });
        
        const userId = this.$store.state.userId;
        
        // 从API加载用户信息
        const profileResponse = await this.$api.userApi.getProfile(userId);
        if (profileResponse.success && profileResponse.profile) {
          // 处理基本信息
          if (profileResponse.profile.basicInfo) {
            this.basicInfo = profileResponse.profile.basicInfo;
          }
          
          // 处理生活方式信息
          if (profileResponse.profile.lifestyle) {
            this.lifestyleInfo = profileResponse.profile.lifestyle;
          }
          
          // 处理症状信息
          if (profileResponse.profile.symptoms) {
            console.log('症状数据:', JSON.stringify(profileResponse.profile.symptoms));
            if (Array.isArray(profileResponse.profile.symptoms)) {
              this.symptoms = profileResponse.profile.symptoms;
            } else if (profileResponse.profile.symptoms.symptoms && Array.isArray(profileResponse.profile.symptoms.symptoms)) {
              this.symptoms = profileResponse.profile.symptoms.symptoms;
            } else {
              this.symptoms = [];
            }
            console.log('处理后的症状数据:', JSON.stringify(this.symptoms));
          }
          
          // 更新全局状态
          this.$store.setUserInfo({
            basicInfo: this.basicInfo,
            lifestyle: this.lifestyleInfo,
            symptoms: this.symptoms
          });
        }
        
        // 获取最新报告
        const reportResponse = await this.$api.detectApi.getReport(userId);
        if (reportResponse.success && reportResponse.report) {
          const report = reportResponse.report;
          
          // 更新风险信息
          this.riskPercent = report.riskPercent || 0;
          this.riskDescription = report.riskDescription || '暂无风险评估';
          this.riskAdvice = report.riskAdvice || '暂无健康建议';
          
          // 设置风险等级
          if (this.riskPercent >= 70) {
            this.riskLevel = { text: '高风险', class: 'high-risk' };
          } else if (this.riskPercent >= 40) {
            this.riskLevel = { text: '中风险', class: 'medium-risk' };
          } else {
            this.riskLevel = { text: '低风险', class: 'low-risk' };
          }
          
          // 保存到全局状态
          this.$store.setCurrentReport(report);
        } else {
          // 如果没有报告，使用简单计算
          this.calculateRisk();
        }
      } catch (error) {
        console.error('加载用户数据失败:', error);
        uni.showToast({
          title: '加载数据失败',
          icon: 'none'
        });
        
        // 加载失败时使用简单计算
        this.calculateRisk();
      } finally {
        uni.hideLoading();
      }
    },
    calculateRisk() {
      // 简单的风险计算逻辑，实际应用中可能需要更复杂的算法
      let riskScore = 0;
      
      // 年龄因素
      if (this.basicInfo.age > 65) riskScore += 20;
      else if (this.basicInfo.age > 45) riskScore += 10;
      
      // BMI因素
      const bmiValue = parseFloat(this.bmi);
      if (bmiValue > 30) riskScore += 15;
      else if (bmiValue > 25) riskScore += 10;
      
      // 吸烟因素
      if (this.lifestyleInfo.smokingStatus === '吸烟') riskScore += 15;
      else if (this.lifestyleInfo.smokingStatus === '曾经吸烟') riskScore += 5;
      
      // 症状因素
      riskScore += this.symptoms.length * 5;
      
      // 限制最大风险为95%
      this.riskPercent = Math.min(riskScore, 95);
      
      // 设置风险等级
      if (this.riskPercent >= 70) {
        this.riskLevel = { text: '高风险', class: 'high-risk' };
        this.riskDescription = '您的脑卒中风险较高';
        this.riskAdvice = '建议立即咨询专业医生，进行详细检查和评估。控制血压、血糖和血脂，采取积极的生活方式干预。';
      } else if (this.riskPercent >= 40) {
        this.riskLevel = { text: '中风险', class: 'medium-risk' };
        this.riskDescription = '您的脑卒中风险中等';
        this.riskAdvice = '建议近期咨询医生，检查相关指标，改善生活习惯，增加体育锻炼，控制体重。';
      } else {
        this.riskLevel = { text: '低风险', class: 'low-risk' };
        this.riskDescription = '您的脑卒中风险较低';
        this.riskAdvice = '建议保持健康的生活方式，定期体检，控制血压和血糖。';
      }
    },
    printRecord() {
      uni.showToast({
        title: '打印功能开发中',
        icon: 'none'
      });
    },
    shareRecord() {
      uni.showShareMenu({
        withShareTicket: true,
        success() {
          uni.showToast({
            title: '请选择分享方式',
            icon: 'none'
          });
        }
      });
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background: #f8f9fd;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
}

.header-area {
  padding: 60rpx 40rpx 20rpx;
  display: flex;
  align-items: center;
  position: relative;
}

.back-button {
  width: 70rpx;
  height: 70rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(74, 109, 167, 0.1);
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

.home-btn-top {
  position: absolute;
  right: 34rpx;
  top: 50%;
  transform: translateY(-50%);
  background: linear-gradient(90deg, #adb0ae 60%, #7d7e7d 100%);
  color: #fff;
  font-weight: 600;
  border: none;
  border-radius: 32rpx;
  font-size: 28rpx;
  padding: 0 36rpx;
  height: 60rpx;
  line-height: 60rpx;
  margin-left: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(74, 109, 167, 0.13);
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
}
.home-btn-top:active,
.home-btn-top.btn-hover {
  transform: scale(0.96);
  filter: brightness(0.96);
  box-shadow: 0 1rpx 4rpx rgba(74, 109, 167, 0.10);
}

.content-wrapper {
  flex: 1;
  padding: 0 32rpx;
  margin-bottom: 180rpx;
}

.info-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(74, 109, 167, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.risk-badge {
  padding: 8rpx 20rpx;
  border-radius: 24rpx;
  font-size: 24rpx;
  color: #fff;
  font-weight: 500;
}

.low-risk {
  background-color: #4CAF50;
}

.medium-risk {
  background-color: #FFC107;
}

.high-risk {
  background-color: #F44336;
}

.divider {
  height: 2rpx;
  background-color: #f0f0f0;
  margin: 16rpx 0 24rpx 0;
}

.info-list {
  display: flex;
  flex-direction: column;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 2rpx solid #f8f8f8;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #666;
  font-size: 28rpx;
}

.info-value {
  color: #333;
  font-size: 28rpx;
  font-weight: 500;
}

.symptom-grid {
  display: flex;
  flex-wrap: wrap;
  margin-top: 16rpx;
}

.symptom-tag {
  display: flex;
  align-items: center;
  background-color: rgba(74, 109, 167, 0.1);
  border-radius: 28rpx;
  padding: 12rpx 24rpx;
  margin-right: 16rpx;
  margin-bottom: 16rpx;
}

.symptom-emoji {
  margin-right: 8rpx;
  font-size: 32rpx;
}

.symptom-text {
  font-size: 26rpx;
  color: #4A6DA7;
}

.empty-symptoms {
  padding: 32rpx 0;
  text-align: center;
  color: #999;
  font-size: 28rpx;
}

.risk-card {
  background: linear-gradient(180deg, #fff 0%, #f8fcff 100%);
}

.risk-assessment {
  padding: 16rpx 0;
}

.risk-chart {
  height: 24rpx;
  background-color: #eee;
  border-radius: 12rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.risk-indicator {
  height: 100%;
  background: linear-gradient(90deg, #4A6DA7 0%, #6fa8dc 100%);
  border-radius: 12rpx;
}

.risk-detail {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.risk-percent {
  font-size: 48rpx;
  font-weight: 600;
  color: #4A6DA7;
  margin-right: 16rpx;
}

.risk-desc {
  font-size: 28rpx;
  color: #333;
}

.risk-advice {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  padding: 16rpx 0;
}

.bottom-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  padding: 24rpx 32rpx 48rpx 32rpx;
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.button-row {
  display: flex;
  width: 100%;
  margin-bottom: 16rpx;
}

.button-row:last-child {
  margin-bottom: 0;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 600;
}

.print-btn {
  margin-right: 16rpx;
  background-color: #f0f1f5;
  color: #4A6DA7;
  border: 2rpx solid #4A6DA7;
}

.share-btn {
  background: linear-gradient(90deg, #4A6DA7 0%, #6fa8dc 100%);
  color: #fff;
  box-shadow: 0 4rpx 16rpx rgba(74, 109, 167, 0.2);
}

.btn-hover {
  transform: scale(0.96);
  opacity: 0.9;
}
</style> 