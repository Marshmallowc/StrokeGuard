<template>
  <view class="container">
    <!-- 顶部区域 -->
    <view class="top-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">健康指标</text>
    </view>
    
    <!-- 表单区域 -->
    <view class="form-container">
      <!-- BMI -->
      <view class="form-item">
        <text class="form-label">BMI：</text>
        <input class="form-input" type="digit" v-model="formData.bmi" placeholder="BMI = 体重(kg) / 身高(m)²" />
      </view>
      
      <!-- 平均血糖浓度 -->
      <view class="form-item">
        <text class="form-label">平均血糖浓度：</text>
        <input class="form-input" type="digit" v-model="formData.avgGlucose" placeholder="请输入平均血糖浓度(mg/dL)" />
      </view>
      
      <!-- 高血压 -->
      <view class="form-item">
        <text class="form-label">高血压：</text>
        <view class="form-input">
          <picker @change="bindHypertensionChange" :value="hypertensionIndex" :range="hypertensionStatus">
            <view class="picker-content">
              <text>{{ hypertensionStatus[hypertensionIndex] || '请选择是否有高血压' }}</text>
            </view>
          </picker>
        </view>
      </view>
      
      <!-- 心脏病 -->
      <view class="form-item">
        <text class="form-label">心脏病：</text>
        <view class="form-input">
          <picker @change="bindHeartDiseaseChange" :value="heartDiseaseIndex" :range="heartDiseaseStatus">
            <view class="picker-content">
              <text>{{ heartDiseaseStatus[heartDiseaseIndex] || '请选择是否有心脏病' }}</text>
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
        bmi: '',
        avgGlucose: '',
        hypertension: '',
        heartDisease: ''
      },
      hypertensionStatus: ['有', '无'],
      heartDiseaseStatus: ['有', '无'],
      hypertensionIndex: -1,
      heartDiseaseIndex: -1
    }
  },
  methods: {
    goBack() {
      uni.navigateBack();
    },
    bindHypertensionChange(e) {
      this.hypertensionIndex = e.detail.value;
      this.formData.hypertension = this.hypertensionStatus[this.hypertensionIndex];
    },
    bindHeartDiseaseChange(e) {
      this.heartDiseaseIndex = e.detail.value;
      this.formData.heartDisease = this.heartDiseaseStatus[this.heartDiseaseIndex];
    },
    validateBMI(value) {
      const bmi = parseFloat(value);
      return !isNaN(bmi) && bmi > 0 && bmi < 100;
    },
    validateGlucose(value) {
      const glucose = parseFloat(value);
      return !isNaN(glucose) && glucose > 0 && glucose < 1000;
    },
    nextStep() {
      // 表单验证
      if (!this.formData.bmi || !this.validateBMI(this.formData.bmi)) {
        uni.showToast({
          title: '请输入有效的BMI值',
          icon: 'none'
        });
        return;
      }
      
      if (!this.formData.avgGlucose || !this.validateGlucose(this.formData.avgGlucose)) {
        uni.showToast({
          title: '请输入有效的血糖浓度',
          icon: 'none'
        });
        return;
      }
      
      if (this.hypertensionIndex === -1) {
        uni.showToast({
          title: '请选择是否有高血压',
          icon: 'none'
        });
        return;
      }
      
      if (this.heartDiseaseIndex === -1) {
        uni.showToast({
          title: '请选择是否有心脏病',
          icon: 'none'
        });
        return;
      }
      
      // 保存数据并跳转到下一步
      uni.showToast({
        title: '保存成功',
        icon: 'success',
        duration: 1500,
        success: () => {
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/manual-input/result'
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

.form-tip {
  font-size: 24rpx;
  color: #666;
  margin-top: 8rpx;
  display: block;
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