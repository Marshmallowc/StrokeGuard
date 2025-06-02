<template>
  <view class="container">
    <!-- 顶部标题 -->
    <view class="header-area">
      <text class="main-title">{{ stepTitles[step] }}</text>
      <text class="sub-title">{{ stepSubTitles[step] }}</text>
    </view>
    <!-- 步骤内容 -->
    <view class="content-wrapper">
      <view v-if="step === 0" class="form-area">
        <!-- 年龄滑动选择 -->
        <view class="form-item">
          <text class="form-label">年龄</text>
          <view class="age-slider-row">
            <text class="age-value">{{ formData.age }}</text>
            <text class="age-unit">岁</text>
          </view>
          <slider
            class="age-slider"
            :min="1"
            :max="120"
            :value="formData.age"
            :activeColor="'#4A6DA7'"
            :backgroundColor="'#E0E0E0'"
            :blockSize="28"
            :blockColor="'#4A6DA7'"
            @change="onAgeChange"
            show-value="false"
          />
        </view>
        <!-- 性别选择 -->
        <view class="form-item">
          <text class="form-label">性别</text>
          <view class="form-input">
            <picker @change="bindGenderChange" :value="genderIndex" :range="genders">
              <view class="picker-content">
                <text>{{ genders[genderIndex] || '请选择性别' }}</text>
              </view>
            </picker>
          </view>
        </view>
        <!-- 身高输入 -->
        <view class="form-item">
          <text class="form-label">身高(cm)</text>
          <input class="form-input" type="digit" v-model="formData.height" placeholder="请输入您的身高" />
        </view>
        <!-- 体重输入 -->
        <view class="form-item">
          <text class="form-label">体重(kg)</text>
          <input class="form-input" type="digit" v-model="formData.weight" placeholder="请输入您的体重" />
        </view>
        <!-- 平均血糖浓度输入 -->
        <view class="form-item">
          <text class="form-label">平均血糖浓度(mg/dL)</text>
          <input class="form-input" type="digit" v-model="formData.avg_glucose_level" placeholder="请输入您的平均血糖浓度" />
        </view>
      </view>
      <view v-else class="form-area">
        <!-- 婚姻状况 -->
        <view class="form-item">
          <text class="form-label">婚姻状况</text>
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
          <text class="form-label">工作类型</text>
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
          <text class="form-label">居住类型</text>
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
          <text class="form-label">抽烟状况</text>
          <view class="form-input">
            <picker @change="bindSmokingChange" :value="smokingIndex" :range="smokingStatus">
              <view class="picker-content">
                <text>{{ smokingStatus[smokingIndex] || '请选择抽烟状况' }}</text>
              </view>
            </picker>
          </view>
        </view>
      </view>
      <!-- 分页指示器 -->
      <view class="pagination">
        <view v-for="i in 2" :key="i" class="dot" :class="{ active: i-1 === step }"></view>
      </view>
    </view>
    
    <!-- 底部按钮区域 -->
    <view class="bottom-area">
      <button class="back-btn" hover-class="btn-hover" @click="goBack" :disabled="loading">返回</button>
      <button v-if="step === 0" class="skip-btn" hover-class="btn-hover" @click="nextStep" :disabled="loading">下一步</button>
      <button v-else class="skip-btn" hover-class="btn-hover" @click="finish" :disabled="loading">完成</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      step: 0,
      stepTitles: ['填写基本信息', '生活方式'],
      stepSubTitles: ['请完善您的基本信息', '请完善您的生活方式信息'],
      formData: {
        age: 30,
        gender: '',
        height: '',
        weight: '',
        avg_glucose_level: '',
        maritalStatus: '',
        workType: '',
        residenceType: '',
        smokingStatus: ''
      },
      genders: ['男', '女'],
      genderIndex: -1,
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
  onLoad() {
    // 尝试从全局状态获取已有数据
    this.loadFormData();
  },
  methods: {
    // 从全局状态加载已有数据
    loadFormData() {
      const userInfo = this.$store.state.userInfo;
      if (userInfo.basicInfo) {
        this.formData.age = userInfo.basicInfo.age || 30;
        this.formData.gender = userInfo.basicInfo.gender || '';
        this.formData.height = userInfo.basicInfo.height || '';
        this.formData.weight = userInfo.basicInfo.weight || '';
        this.formData.avg_glucose_level = userInfo.basicInfo.avg_glucose_level || '';
        
        // 设置选择器索引
        this.genderIndex = this.genders.findIndex(item => item === this.formData.gender);
      }
      
      if (userInfo.lifestyle) {
        this.formData.maritalStatus = userInfo.lifestyle.maritalStatus || '';
        this.formData.workType = userInfo.lifestyle.workType || '';
        this.formData.residenceType = userInfo.lifestyle.residenceType || '';
        this.formData.smokingStatus = userInfo.lifestyle.smokingStatus || '';
        
        // 设置选择器索引
        this.maritalIndex = this.maritalStatus.findIndex(item => item === this.formData.maritalStatus);
        this.workIndex = this.workTypes.findIndex(item => item === this.formData.workType);
        this.residenceIndex = this.residenceTypes.findIndex(item => item === this.formData.residenceType);
        this.smokingIndex = this.smokingStatus.findIndex(item => item === this.formData.smokingStatus);
      }
    },
    
    goBack() {
      if (this.loading) return;
      
      if (this.step === 0) {
        uni.navigateBack();
      } else {
        this.step = 0;
      }
    },
    
    onAgeChange(e) {
      this.formData.age = e.detail.value;
    },
    
    bindGenderChange(e) {
      this.genderIndex = e.detail.value;
      this.formData.gender = this.genders[this.genderIndex];
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
    
    // 保存基本信息并进入下一步
    async nextStep() {
      if (this.loading) return;
      
      // 基本信息校验
      if (!this.formData.age) {
        uni.showToast({ title: '请选择年龄', icon: 'none' }); return;
      }
      if (this.genderIndex === -1) {
        uni.showToast({ title: '请选择性别', icon: 'none' }); return;
      }
      if (!this.formData.height) {
        uni.showToast({ title: '请输入身高', icon: 'none' }); return;
      }
      if (!this.formData.weight) {
        uni.showToast({ title: '请输入体重', icon: 'none' }); return;
      }
      if (!this.formData.avg_glucose_level) {
        uni.showToast({ title: '请输入平均血糖浓度', icon: 'none' }); return;
      }
      
      this.loading = true;
      try {
        // 通过API保存基本信息
        const basicInfo = {
          userId: this.$store.state.userId,
          age: parseInt(this.formData.age),
          gender: this.formData.gender,
          height: parseFloat(this.formData.height),
          weight: parseFloat(this.formData.weight),
          avg_glucose_level: parseFloat(this.formData.avg_glucose_level)
        };
        
        await this.$api.userApi.saveBasicInfo(basicInfo);
        
        // 更新全局状态
        const userInfo = this.$store.state.userInfo;
        userInfo.basicInfo = basicInfo;
        this.$store.setUserInfo(userInfo);
        
        this.step = 1;
      } catch (error) {
        console.error('保存基本信息失败:', error);
        uni.showToast({ title: '保存失败，请重试', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    
    // 保存生活方式信息并完成
    async finish() {
      if (this.loading) return;
      
      // 生活方式校验
      if (this.maritalIndex === -1) {
        uni.showToast({ title: '请选择婚姻状况', icon: 'none' }); return;
      }
      if (this.workIndex === -1) {
        uni.showToast({ title: '请选择工作类型', icon: 'none' }); return;
      }
      if (this.residenceIndex === -1) {
        uni.showToast({ title: '请选择居住类型', icon: 'none' }); return;
      }
      if (this.smokingIndex === -1) {
        uni.showToast({ title: '请选择抽烟状况', icon: 'none' }); return;
      }
      
      this.loading = true;
      try {
        // 工作类型映射表（前端显示值 -> 后端API值）
        const workTypeMapping = {
          '个体经营': '个体经营',
          '政府工作': '政府工作',
          '私营企业': '私营企业',
          '儿童': '儿童',
          '无': '无'
        };
        
        // 抽烟状况映射表
        const smokingStatusMapping = {
          '吸烟': '吸烟',
          '从未吸烟': '从未吸烟',
          '曾经吸烟': '曾经吸烟',
          '未知': '未知'
        };
        
        // 通过API保存生活方式信息
        const lifestyleInfo = {
          userId: this.$store.state.userId,
          maritalStatus: this.formData.maritalStatus,
          workType: workTypeMapping[this.formData.workType] || '其他', // 将前端工作类型映射为后端接受的值
          residenceType: this.formData.residenceType,
          smokingStatus: smokingStatusMapping[this.formData.smokingStatus] || '不吸烟' // 将前端抽烟状况映射为后端接受的值
        };
        
        await this.$api.userApi.saveLifestyle(lifestyleInfo);
        
        // 更新全局状态 - 保存原始值（UI显示用）
        const userInfo = this.$store.state.userInfo;
        userInfo.lifestyle = {
          ...lifestyleInfo,
          workType: this.formData.workType, // 保存原始工作类型值用于UI显示
          smokingStatus: this.formData.smokingStatus // 保存原始抽烟状况值用于UI显示
        };
        this.$store.setUserInfo(userInfo);
        
        uni.navigateTo({ url: '/pages/manual-input/symptom-select' });
      } catch (error) {
        console.error('保存生活方式信息失败:', error);
        uni.showToast({ title: '保存失败，请重试', icon: 'none' });
      } finally {
        this.loading = false;
      }
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
  justify-content: space-between;
  align-items: stretch;
}
.header-area {
  margin-top: 100rpx;
  margin-bottom: 40rpx;
  text-align: center;
}
.main-title {
  font-size: 38rpx;
  font-weight: bold;
  color: #222;
  margin-bottom: 12rpx;
  display: block;
}
.sub-title {
  font-size: 26rpx;
  color: #a0a4b8;
  display: block;
}
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-bottom: 30rpx;
}
.form-area {
  background: #fff;
  border-radius: 40rpx;
  margin: 0 32rpx;
  padding: 48rpx 32rpx 32rpx 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(74, 109, 167, 0.06);
}
.form-item {
  margin-bottom: 44rpx;
}
.form-label {
  font-size: 32rpx;
  color: #222;
  font-weight: 500;
  margin-bottom: 18rpx;
  display: block;
}
.form-input {
  width: 100%;
  height: 90rpx;
  border: 2rpx solid #eee;
  border-radius: 18rpx;
  padding: 0 30rpx;
  font-size: 30rpx;
  box-sizing: border-box;
  background-color: #f7f8fa;
  display: flex;
  align-items: center;
}
.form-input:focus {
  border-color: #4A6DA7;
  background-color: #fff;
}
.picker-content {
  width: 100%;
  height: 90rpx;
  display: flex;
  align-items: center;
}
.age-slider-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 12rpx;
}
.age-value {
  font-size: 48rpx;
  font-weight: 600;
  color: #4A6DA7;
}
.age-unit {
  font-size: 28rpx;
  color: #666;
  margin-left: 10rpx;
}
.age-slider {
  margin: 20rpx 0;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 32rpx 0 0 0;
}
.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #e0e3ee;
  margin: 0 8rpx;
  transition: background 0.2s;
}
.dot.active {
  background: #4A6DA7;
}
.bottom-area {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 48rpx 32rpx 80rpx 32rpx;
  background: transparent;
  margin-top: auto;
}
.back-btn {
  width: 140rpx;
  height: 80rpx;
  border-radius: 28rpx;
  background: #f0f1f5;
  color: #b0b3c6;
  font-size: 30rpx;
  border: none;
  outline: none;
  font-weight: 500;
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
}
.back-btn:disabled {
  opacity: 0.6;
}
.skip-btn {
  flex: 1;
  margin-left: 32rpx;
  height: 80rpx;
  border-radius: 28rpx;
  background: linear-gradient(90deg, #4A6DA7 60%, #6fa8dc 100%);
  color: #fff;
  font-size: 32rpx;
  border: none;
  outline: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(74, 109, 167, 0.13);
  max-width: 420rpx;
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
}
.skip-btn:disabled {
  opacity: 0.6;
}
.back-btn:active, .skip-btn:active,
.btn-hover {
  transform: scale(0.96);
  filter: brightness(0.96);
  box-shadow: 0 2rpx 8rpx rgba(74, 109, 167, 0.10);
}
</style> 