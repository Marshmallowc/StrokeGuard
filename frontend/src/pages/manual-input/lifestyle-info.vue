<template>
  <view class="container">
    <!-- 顶部区域 -->
    <view class="top-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">生活方式</text>
    </view>
    
    <!-- 表单区域 -->
    <view class="form-container">
      <!-- 婚姻状况 -->
      <view class="form-item">
        <text class="form-label">婚姻状况：</text>
        <view class="form-input">
          <picker @change="bindMaritalChange" :value="maritalIndex" :range="maritalStatus">
            <view class="picker-content">
              <text>{{ maritalStatus[maritalIndex] || '请选择婚姻状况' }}</text>
            </view>
          </picker>
        </view>
      </view>
      
      <!-- 工作类型 -->
      <view class="form-item">
        <text class="form-label">工作类型：</text>
        <view class="form-input">
          <picker @change="bindWorkChange" :value="workIndex" :range="workTypes">
            <view class="picker-content">
              <text>{{ workTypes[workIndex] || '请选择工作类型' }}</text>
            </view>
          </picker>
        </view>
      </view>
      
      <!-- 居住类型 -->
      <view class="form-item">
        <text class="form-label">居住类型：</text>
        <view class="form-input">
          <picker @change="bindResidenceChange" :value="residenceIndex" :range="residenceTypes">
            <view class="picker-content">
              <text>{{ residenceTypes[residenceIndex] || '请选择居住类型' }}</text>
            </view>
          </picker>
        </view>
      </view>
      
      <!-- 抽烟状况 -->
      <view class="form-item">
        <text class="form-label">抽烟状况：</text>
        <view class="form-input">
          <picker @change="bindSmokingChange" :value="smokingIndex" :range="smokingStatus">
            <view class="picker-content">
              <text>{{ smokingStatus[smokingIndex] || '请选择抽烟状况' }}</text>
            </view>
          </picker>
        </view>
      </view>
    </view>
    
    <!-- 底部按钮区域 -->
    <view class="bottom-area">
      <view class="next-button" hover-class="button-hover" @click="nextStep">
        <text class="next-text">next</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        maritalStatus: '',
        workType: '',
        residenceType: '',
        smokingStatus: ''
      },
      maritalStatus: ['有', '无'],
      workTypes: ['个体经营', '政府工作', '私营企业', '儿童', '无'],
      residenceTypes: ['城市', '农村'],
      smokingStatus: ['吸烟', '从未吸烟', '曾经吸烟', '未知'],
      maritalIndex: -1,
      workIndex: -1,
      residenceIndex: -1,
      smokingIndex: -1
    }
  },
  methods: {
    goBack() {
      uni.navigateBack();
    },
    bindMaritalChange(e) {
      this.maritalIndex = e.detail.value;
      this.formData.maritalStatus = this.maritalStatus[this.maritalIndex];
    },
    bindWorkChange(e) {
      this.workIndex = e.detail.value;
      this.formData.workType = this.workTypes[this.workIndex];
    },
    bindResidenceChange(e) {
      this.residenceIndex = e.detail.value;
      this.formData.residenceType = this.residenceTypes[this.residenceIndex];
    },
    bindSmokingChange(e) {
      this.smokingIndex = e.detail.value;
      this.formData.smokingStatus = this.smokingStatus[this.smokingIndex];
    },
    nextStep() {
      // 表单验证
      if (this.maritalIndex === -1) {
        uni.showToast({
          title: '请选择婚姻状况',
          icon: 'none'
        });
        return;
      }
      
      if (this.workIndex === -1) {
        uni.showToast({
          title: '请选择工作类型',
          icon: 'none'
        });
        return;
      }
      
      if (this.residenceIndex === -1) {
        uni.showToast({
          title: '请选择居住类型',
          icon: 'none'
        });
        return;
      }
      
      if (this.smokingIndex === -1) {
        uni.showToast({
          title: '请选择抽烟状况',
          icon: 'none'
        });
        return;
      }
      
      // 保存数据并跳转到下一步
      uni.showToast({
        success: () => {
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/manual-input/symptom-select'
            });
          }, 1500);
        }
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
  position: relative;
}

/* 顶部区域 */
.top-area {
  padding: 60rpx 40rpx 30rpx;
  display: flex;
  align-items: center;
  border-bottom: 1rpx solid rgba(0, 0, 0, 0.05);
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

/* 表单区域 */
.form-container {
  padding: 60rpx 40rpx;
  padding-top: 120rpx;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.form-item {
  margin-bottom: 50rpx;
}

.form-label {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 16rpx;
  display: block;
  font-weight: 500;
}

.form-input {
  width: 100%;
  height: 100rpx;
  border: 2rpx solid #ddd;
  border-radius: 16rpx;
  padding: 0 30rpx;
  font-size: 32rpx;
  box-sizing: border-box;
  background-color: #fafafa;
}

.form-input:focus {
  border-color: #4A6DA7;
  background-color: #fff;
}

.picker-content {
  width: 100%;
  height: 100rpx;
  display: flex;
  align-items: center;
}

/* 底部按钮区域 */
.bottom-area {
  padding: 40rpx 40rpx 60rpx;
  display: flex;
  justify-content: center;
  border-top: 1rpx solid rgba(0, 0, 0, 0.05);
  background-color: #fff;
  position: sticky;
  bottom: 0;
}

/* 下一步按钮 */
.next-button {
  width: 240rpx;
  height: 90rpx;
  background-color: #4A6DA7;
  border-radius: 45rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 10rpx rgba(74, 109, 167, 0.3);
  transition: all 0.3s ease;
}

.next-text {
  color: #ffffff;
  font-size: 34rpx;
  font-weight: 500;
}

.button-hover {
  transform: scale(0.95);
  opacity: 0.9;
}

/* 适配安全区域 */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .bottom-area {
    padding-bottom: calc(50rpx + env(safe-area-inset-bottom));
  }
}
</style> 