<template>
  <view class="container">
    <!-- 顶部标题 -->
    <view class="header-area">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="main-title">选择检测方式</text>
      <text class="sub-title">请选择您希望的检测方式</text>
    </view>
    
    <!-- 检测方式选择区域 -->
    <view class="content-wrapper">
      <view class="method-card-list">
        <!-- 直接检测卡片 -->
        <view class="method-card" hover-class="card-hover" @click="handleDirectDetect">
          <view class="method-icon-container">
            <text class="method-icon">✓</text>
          </view>
          <view class="method-info">
            <text class="method-title">直接检测</text>
            <text class="method-desc">基于您的基本信息和症状进行风险评估</text>
          </view>
        </view>
        
        <!-- MRI卡片 -->
        <view class="method-card" hover-class="card-hover" @click="handleMRIDetect">
          <view class="method-icon-container">
            <text class="method-icon">🔍</text>
          </view>
          <view class="method-info">
            <text class="method-title">MRI</text>
            <text class="method-desc">上传MRI影像进行风险评估</text>
          </view>
        </view>
        
        <!-- CT卡片 -->
        <view class="method-card" hover-class="card-hover" @click="handleCTDetect">
          <view class="method-icon-container">
            <text class="method-icon">📊</text>
          </view>
          <view class="method-info">
            <text class="method-title">CT</text>
            <text class="method-desc">上传CT影像进行风险评估</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      loading: false
    }
  },
  methods: {
    // 返回按钮处理
    goBack() {
      if (this.loading) return;
      uni.navigateBack();
    },
    
    // 直接检测
    async handleDirectDetect() {
      if (this.loading) return;
      
      this.loading = true;
      try {
        // 获取用户ID
        const userId = this.$store.state.userId;
        
        // 检查用户是否已有病历
        const userInfo = this.$store.state.userInfo;
        let hasUserData = false;
        
        // 如果全局状态中有数据，则认为用户已有病历
        if (userInfo && userInfo.basicInfo && userInfo.lifestyle) {
          hasUserData = true;
        } else {
          // 尝试从API获取用户信息
          try {
            const profileResponse = await this.$api.userApi.getProfile(userId);
            if (profileResponse.success && profileResponse.profile) {
              // 如果API返回了用户信息，则认为用户已有病历
              hasUserData = true;
              
              // 更新全局状态
              this.$store.setUserInfo({
                basicInfo: profileResponse.profile.basicInfo || {},
                lifestyle: profileResponse.profile.lifestyle || {},
                symptoms: profileResponse.profile.symptoms || []
              });
            }
          } catch (error) {
            console.error('获取用户信息失败:', error);
            // 获取失败时，假设用户没有病历
            hasUserData = false;
          }
        }
        
        if (hasUserData) {
          // 用户已有病历，直接启动检测
          try {
            await this.$api.detectApi.startDetect(userId);
            // 跳转到检测状态页面
            uni.navigateTo({
              url: '/pages/medical-record/detect-status'
            });
          } catch (error) {
            console.error('启动检测失败:', error);
            uni.showToast({
              title: '启动检测失败',
              icon: 'none'
            });
          }
        } else {
          // 用户没有病历，跳转到基本信息输入页面
          uni.navigateTo({
            url: '/pages/manual-input/manual-input'
          });
        }
      } catch (error) {
        console.error('处理检测请求失败:', error);
        uni.showToast({
          title: '操作失败，请重试',
          icon: 'none'
        });
      } finally {
        this.loading = false;
      }
    },
    
    // MRI检测
    handleMRIDetect() {
      this.chooseAndUploadImage('MRI');
    },
    
    // CT检测
    handleCTDetect() {
      this.chooseAndUploadImage('CT');
    },
    
    // 选择并上传图像
    async chooseAndUploadImage(imageType) {
      if (this.loading) return;
      
      try {
        // 选择图片
        const chooseRes = await new Promise((resolve, reject) => {
          uni.chooseImage({
            count: 1, // 最多选择1张图片
            sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图
            sourceType: ['album', 'camera'], // 从相册选择或使用相机
            success: resolve,
            fail: reject
          });
        });
        
        if (!chooseRes || !chooseRes.tempFilePaths || !chooseRes.tempFilePaths.length) {
          return;
        }
        
        const tempFilePath = chooseRes.tempFilePaths[0];
        
        // 显示上传中提示
        uni.showLoading({
          title: '正在上传...',
          mask: true
        });
        
        this.loading = true;
        
        // 上传图像
        try {
          // 获取用户ID
          const userId = this.$store.state.userId;
          
          // 调用上传接口
          const uploadRes = await this.uploadImageFile(tempFilePath, userId, imageType);
          
          // 隐藏上传提示
          uni.hideLoading();
          
          if (uploadRes && uploadRes.success) {
            // 上传成功，显示提示
            uni.showToast({
              title: '上传成功',
              icon: 'success',
              duration: 1500
            });
            
            // 启动分析流程
            await this.startImageAnalysis(userId, imageType, uploadRes.fileId);
          } else {
            throw new Error('上传失败');
          }
        } catch (error) {
          console.error(`${imageType}图像上传失败:`, error);
          uni.hideLoading();
          uni.showToast({
            title: '上传失败，请重试',
            icon: 'none'
          });
        } finally {
          this.loading = false;
        }
      } catch (error) {
        console.error('选择图片失败:', error);
        uni.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
      }
    },
    
    // 上传图像文件
    async uploadImageFile(filePath, userId, imageType) {
      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: `${this.$api.BASE_URL}api/image/upload`,
          filePath: filePath,
          name: 'file',
          formData: {
            userId: userId,
            imageType: imageType
          },
          success: (res) => {
            try {
              // 解析响应
              const data = JSON.parse(res.data);
              if (data.success) {
                resolve(data);
              } else {
                reject(new Error(data.message || '上传失败'));
              }
            } catch (e) {
              reject(new Error('解析响应失败'));
            }
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },
    
    // 启动图像分析
    async startImageAnalysis(userId, imageType, fileId) {
      try {
        // 显示分析中提示
        uni.showLoading({
          title: '正在分析...',
          mask: true
        });
        
        // 调用分析接口
        const response = await this.$api.detectApi.startImageDetect({
          userId: userId,
          imageType: imageType,
          fileId: fileId
        });
        
        // 隐藏分析提示
        uni.hideLoading();
        
        if (response && response.success) {
          // 分析已启动，跳转到检测状态页面
          uni.navigateTo({
            url: '/pages/medical-record/detect-status'
          });
        } else {
          throw new Error('启动分析失败');
        }
      } catch (error) {
        console.error('启动分析失败:', error);
        uni.hideLoading();
        uni.showToast({
          title: '启动分析失败，请重试',
          icon: 'none'
        });
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
  position: relative;
}

/* 顶部区域样式 */
.header-area {
  padding: 60rpx 40rpx 20rpx;
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
  position: absolute;
  left: 30rpx;
  top: 60rpx;
}

.back-icon {
  font-size: 40rpx;
  color: #4A6DA7;
}

.main-title {
  font-size: 38rpx;
  font-weight: bold;
  color: #222;
  margin-top: 40rpx;
  margin-bottom: 12rpx;
  text-align: center;
  display: block;
}

.sub-title {
  font-size: 26rpx;
  color: #a0a4b8;
  text-align: center;
  display: block;
}

/* 内容区域样式 */
.content-wrapper {
  flex: 1;
  padding: 0 32rpx;
  display: flex;
  flex-direction: column;
}

.method-card-list {
  display: flex;
  flex-direction: column;
  gap: 40rpx;
  width: 100%;
  margin-top: 44vh; /* 将卡片放在页面50%以下 */
}

.method-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(74, 109, 167, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card-hover {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(74, 109, 167, 0.04);
}

.method-icon-container {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #4A6DA7 0%, #6fa8dc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.method-icon {
  font-size: 40rpx;
  color: #fff;
}

.method-info {
  flex: 1;
}

.method-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
  display: block;
}

.method-desc {
  font-size: 24rpx;
  color: #666;
  display: block;
}
</style> 