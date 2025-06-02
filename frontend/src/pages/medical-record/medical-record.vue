<template>
  <view class="container">
    <!-- 顶部区域 -->
    <view class="top-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">我的病历</text>
    </view>
    
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-container">
      <view class="loading-circle"></view>
      <text class="loading-text">加载中...</text>
    </view>
    
    <!-- 中心图形区域 -->
    <view v-else class="center-graphic" @click="goToRecordDetail">
      <view class="circle-animation"></view>
      <view class="pulse-effect"></view>
      <text class="center-text clickable">健康档案</text>
    </view>
    
    <!-- 底部按钮区域 -->
    <view class="button-area">
      <!-- 上传电子病历按钮 -->
      <view class="action-button upload-button" hover-class="button-hover" @click="uploadMedicalRecord" :style="{ opacity: uploading ? 0.7 : 1 }">
        <text class="button-text">{{ uploading ? '上传中...' : '上传电子病历' }}</text>
      </view>
      
      <!-- 手动输入按钮 -->
      <view class="action-button input-button" hover-class="button-hover" @click="manualInput" :style="{ opacity: uploading ? 0.7 : 1 }">
        <text class="button-text">手动输入</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      uploading: false,
      medicalRecords: []
    }
  },
  onLoad() {
    this.loadMedicalRecords();
  },
  methods: {
    // 返回按钮
    goBack() {
      uni.navigateBack();
    },
    
    // 加载用户病历记录
    async loadMedicalRecords() {
      this.loading = true;
      try {
        const userId = this.$store.state.userId;
        const response = await this.$api.userApi.getMedicalRecords(userId);
        
        if (response.success && response.records) {
          this.medicalRecords = response.records;
          this.$store.setMedicalRecords(response.records);
        }
      } catch (error) {
        console.error('加载病历记录失败:', error);
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        });
      } finally {
        this.loading = false;
      }
    },
    
    // 上传电子病历
    uploadMedicalRecord() {
      if (this.uploading) return;
      
      // 调用系统文件选择器，选择PDF或图片文件
      uni.chooseFile({
        count: 1,
        type: 'all',
        extension: ['.pdf', '.jpg', '.jpeg', '.png'],
        success: (res) => {
          const tempFilePath = res.tempFilePaths[0];
          this.uploadFile(tempFilePath);
        },
        fail: (err) => {
          // 部分平台可能不支持chooseFile，尝试使用chooseImage
          if (err.errMsg && err.errMsg.includes('not function')) {
            this.chooseImageFallback();
          } else {
            uni.showToast({
              title: '选择文件失败',
              icon: 'none'
            });
          }
        }
      });
    },
    
    // 兼容性处理：使用chooseImage作为备选
    chooseImageFallback() {
      uni.chooseImage({
        count: 1,
        success: (res) => {
          const tempFilePath = res.tempFilePaths[0];
          this.uploadFile(tempFilePath);
        },
        fail: () => {
          uni.showToast({
            title: '选择图片失败',
            icon: 'none'
          });
        }
      });
    },
    
    // 上传文件到服务器
    async uploadFile(filePath) {
      this.uploading = true;
      
      try {
        const userId = this.$store.state.userId;
        const response = await this.$api.medicalRecordApi.uploadFile(userId, filePath);
        
        if (response.success) {
          uni.showToast({
            title: '上传成功',
            icon: 'success'
          });
          
          // 重新加载病历记录
          await this.loadMedicalRecords();
        } else {
          uni.showToast({
            title: response.message || '上传失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('上传文件失败:', error);
        uni.showToast({
          title: '上传失败',
          icon: 'none'
        });
      } finally {
        this.uploading = false;
      }
    },
    
    // 手动输入按钮
    manualInput() {
      if (this.uploading) return;
      
      uni.navigateTo({
        url: '/pages/manual-input/manual-input'
      });
    },
    
    // 进入病历详情
    goToRecordDetail() {
      if (this.loading) return;
      
      uni.navigateTo({
        url: '/pages/medical-record/record-detail'
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
  height: 40vh;
  margin-top: 5vh;
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

/* 中心图形区域 */
.center-graphic {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 40vh;
  position: relative;
  margin-top: 5vh;
  cursor: pointer;
}

.circle-animation {
  width: 300rpx;
  height: 300rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A6DA7, #86A8E7);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(74, 109, 167, 0.3);
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0rpx);
  }
  50% {
    transform: translateY(-20rpx);
  }
  100% {
    transform: translateY(0rpx);
  }
}

.pulse-effect {
  position: absolute;
  width: 300rpx;
  height: 300rpx;
  border-radius: 50%;
  background-color: rgba(74, 109, 167, 0.3);
  animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
}

.center-text {
  position: absolute;
  font-size: 40rpx;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.2);
}

.center-text.clickable {
  transition: transform 0.15s, filter 0.15s;
}

.center-graphic:active .center-text.clickable {
  transform: scale(0.96);
  filter: brightness(0.92);
}

/* 底部按钮区域 */
.button-area {
  position: absolute;
  bottom: 10%;
  left: 0;
  right: 0;
  padding: 40rpx;
  display: flex;
  justify-content: space-around;
  background: linear-gradient(to top, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0), rgba(255, 255, 255, 0));
}

.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 40%;
  height: 180rpx;
  border-radius: 30rpx;
  background-color: #ffffff;
  box-shadow: 0 5rpx 20rpx rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-button {
  background-color: #4A6DA7;
}

.input-button {
  border: 2rpx solid #4A6DA7;
}

.button-icon {
  font-size: 50rpx;
  margin-bottom: 10rpx;
}

.button-text {
  font-size: 28rpx;
  font-weight: 500;
}

.upload-button .button-text {
  color: #ffffff;
}

.input-button .button-text {
  color: #4A6DA7;
}

.button-hover {
  transform: scale(0.95);
  opacity: 0.9;
}

/* 适配单手操作习惯 */
@media screen and (min-height: 700px) {
  .button-area {
    bottom: 20%;
  }
}
</style> 