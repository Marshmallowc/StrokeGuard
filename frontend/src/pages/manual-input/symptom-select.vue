<template>
  <view class="container">
    <!-- 顶部标题 -->
    <view class="header-area">
      <text class="main-title">{{ pageTitles[pageIndex] }}</text>
      <text class="sub-title">{{ pageSubTitles[pageIndex] }}</text>
    </view>
    
    <!-- 加载提示 -->
    <view v-if="loading" class="loading-container">
      <view class="loading-circle"></view>
      <text class="loading-text">加载中...</text>
    </view>
    
    <!-- 症状卡片列表 -->
    <view v-else class="symptom-card-list">
      <view
        v-for="(symptom, idx) in pagedSymptoms"
        :key="symptom.key"
        class="symptom-card"
        :class="{ selected: selected[symptom.globalIdx] }"
        @click="toggleSymptom(symptom.globalIdx)"
      >
        <text class="symptom-label">{{ symptom.label }}</text>
        <view class="emoji-circle" :class="{ selected: selected[symptom.globalIdx] }">
          <text class="symptom-emoji">{{ symptom.emoji }}</text>
        </view>
      </view>
    </view>
    
    <!-- 分页指示器 -->
    <view class="pagination">
      <view v-for="i in totalPages" :key="i" class="dot" :class="{ active: i-1 === pageIndex }"></view>
    </view>
    
    <!-- 底部按钮区域 -->
    <view class="bottom-area">
      <button class="back-btn" hover-class="btn-hover" @click="goBack" :disabled="loading || submitting">返回</button>
      <button class="skip-btn" hover-class="btn-hover" @click="skip" :disabled="loading || submitting">
        {{ pageIndex < totalPages - 1 ? '下一步' : '完成' }}
      </button>
    </view>
  </view>
</template>

<script>
// 默认症状列表（如果API获取失败将使用这个）
const DEFAULT_SYMPTOMS = [
  // 第一页 (3个) - 心脏相关症状
  { key: 'chestPain', label: '胸痛或胸闷', emoji: '💔' },
  { key: 'dyspnea', label: '呼吸急促', emoji: '😮‍💨' },
  { key: 'arrhythmia', label: '心律不齐', emoji: '💗' },
  
  // 第二页 (4个) - 身体感觉
  { key: 'fatigue', label: '疲劳虚弱', emoji: '😪' },
  { key: 'dizziness', label: '头晕目眩', emoji: '🌀' },
  { key: 'swelling', label: '身体水肿', emoji: '🫧' },
  { key: 'sweating', label: '异常出汗', emoji: '💧' },
  
  // 第三页 (3个) - 疼痛和不适
  { key: 'neckPain', label: '颈肩背部疼痛', emoji: '🤕' },
  { key: 'cough', label: '持续性咳嗽', emoji: '😷' },
  { key: 'nausea', label: '恶心想吐', emoji: '🤢' },
  
  // 第四页 (3个) - 其他症状
  { key: 'coldLimbs', label: '手脚发凉', emoji: '🧊' },
  { key: 'snoring', label: '睡觉打鼾', emoji: '😴' },
  { key: 'anxiety', label: '感到焦虑', emoji: '😰' }
];

const PAGE_SIZE = [3, 4, 3, 3];
const PAGE_TITLES = [
  '您最近是否感到胸部不适？',
  '身体有这些感觉吗？',
  '是否有疼痛或不适？',
  '最后，还有其他症状吗？'
];
const PAGE_SUBTITLES = [
  '轻点选择您的症状，可以多选',
  '选择所有符合的症状',
  '告诉我们您的感受',
  '帮助我们更全面了解'
];

export default {
  data() {
    return {
      loading: true,
      submitting: false,
      symptoms: [],
      selected: [],
      pageIndex: 0,
      pageTitles: PAGE_TITLES,
      pageSubTitles: PAGE_SUBTITLES
    }
  },
  async onLoad() {
    // 加载症状列表
    await this.loadSymptoms();
  },
  computed: {
    totalPages() {
      // 直接返回配置的页面数量
      return PAGE_SIZE.length;
    },
    pagedSymptoms() {
      // 计算当前页开始索引
      let start = 0;
      for (let i = 0; i < this.pageIndex; i++) start += PAGE_SIZE[i];
      
      // 计算当前页要显示的数量
      const count = PAGE_SIZE[this.pageIndex];
      
      // 确保不越界
      const availableCount = Math.min(count, this.symptoms.length - start);
      
      if (availableCount <= 0) {
        return [];
      }
      
      // 返回当前页的症状列表
      return this.symptoms.slice(start, start + availableCount).map((s, i) => ({ ...s, globalIdx: start + i }));
    }
  },
  methods: {
    // 从API加载症状列表
    async loadSymptoms() {
      this.loading = true;
      try {
        // 直接使用默认症状列表以确保页面布局正确
        this.symptoms = DEFAULT_SYMPTOMS;
        
        // 初始化选择状态数组
        this.selected = Array(this.symptoms.length).fill(false);
        
        // 尝试从API获取症状，但仅用于更新标签或表情符号
        try {
          const response = await this.$api.otherApi.getSymptomsList();
          if (response.success && response.symptoms && response.symptoms.length === this.symptoms.length) {
            // 仅更新标签和表情符号，保持顺序不变
            for (let i = 0; i < this.symptoms.length; i++) {
              if (response.symptoms[i]) {
                this.symptoms[i].label = response.symptoms[i].label || this.symptoms[i].label;
                this.symptoms[i].emoji = response.symptoms[i].emoji || this.symptoms[i].emoji;
              }
            }
          }
        } catch (apiError) {
          console.warn('API获取症状列表失败，使用默认列表', apiError);
        }
      } catch (error) {
        console.error('症状列表初始化失败:', error);
        this.symptoms = DEFAULT_SYMPTOMS;
        this.selected = Array(this.symptoms.length).fill(false);
      } finally {
        this.loading = false;
      }
    },
    
    // 返回按钮处理
    goBack() {
      if (this.loading || this.submitting) return;
      
      if (this.pageIndex === 0) {
        uni.navigateBack();
      } else {
        this.pageIndex--;
      }
    },
    
    // 切换症状选择状态
    toggleSymptom(idx) {
      if (this.loading || this.submitting) return;
      this.selected[idx] = !this.selected[idx];
    },
    
    // 下一步/完成按钮处理
    async skip() {
      if (this.loading || this.submitting) return;
      
      if (this.pageIndex < this.totalPages - 1) {
        // 还有下一页，直接翻页
        this.pageIndex++;
      } else {
        // 最后一页，提交数据
        this.submitting = true;
        
        try {
          // 收集选中的症状
          const selectedSymptoms = this.symptoms.filter((_, idx) => this.selected[idx]);
          
          // 保存症状数据到API
          await this.$api.userApi.saveSymptoms({
            userId: this.$store.state.userId,
            symptoms: selectedSymptoms,
            hasSymptoms: selectedSymptoms.length > 0 ? '有' : '无'
          });
          
          // 更新全局状态
          const userInfo = this.$store.state.userInfo;
          userInfo.symptoms = selectedSymptoms;
          this.$store.setUserInfo(userInfo);
          
          // 显示提示
          uni.showToast({
            title: '保存成功',
            icon: 'success',
            duration: 1500,
            success: () => {
              setTimeout(async () => {
                // 启动风险检测流程
                try {
                  const startResponse = await this.$api.detectApi.startDetect(this.$store.state.userId);
                  if (startResponse.success) {
                    // 检测已启动，跳转到检测状态页
                    uni.navigateTo({ url: '/pages/medical-record/detect-status' });
                  } else {
                    // 启动失败，直接跳转到病历页
                    uni.navigateTo({ url: '/pages/medical-record/record-detail' });
                  }
                } catch (error) {
                  console.error('启动检测失败:', error);
                  uni.navigateTo({ url: '/pages/medical-record/record-detail' });
                }
              }, 1500);
            }
          });
        } catch (error) {
          console.error('保存症状失败:', error);
          uni.showToast({
            title: '保存失败，请重试',
            icon: 'none'
          });
          this.submitting = false;
        }
      }
    },
    
    // 检查检测状态并导航
    async checkDetectStatus() {
      try {
        const response = await this.$api.detectApi.checkStatus(this.$store.state.userId);
        
        if (response.success) {
          // 更新检测状态
          this.$store.setDetectStatus(response.status, response.progress);
          
          // 根据状态导航
          if (response.status === 'finished') {
            // 检测完成，获取报告
            this.getDetectReport();
          } else {
            // 检测中，跳转到检测状态页
            uni.navigateTo({ url: '/pages/medical-record/detect-status' });
          }
        } else {
          // 状态检查失败，直接跳转到病历页
          uni.navigateTo({ url: '/pages/medical-record/record-detail' });
        }
      } catch (error) {
        console.error('检查检测状态失败:', error);
        // 出错时直接跳转到病历页
        uni.navigateTo({ url: '/pages/medical-record/record-detail' });
      } finally {
        this.submitting = false;
      }
    },
    
    // 获取检测报告
    async getDetectReport() {
      try {
        const response = await this.$api.detectApi.getReport(this.$store.state.userId);
        
        if (response.success && response.report) {
          // 保存报告到全局状态
          this.$store.setCurrentReport(response.report);
          
          // 跳转到报告页
          uni.navigateTo({ url: '/pages/medical-record/report' });
        } else {
          // 获取报告失败，跳转到病历页
          uni.navigateTo({ url: '/pages/medical-record/record-detail' });
        }
      } catch (error) {
        console.error('获取检测报告失败:', error);
        uni.navigateTo({ url: '/pages/medical-record/record-detail' });
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
  justify-content: flex-start;
  align-items: stretch;
}
.header-area {
  margin-top: 120rpx;
  margin-bottom: 36rpx;
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

/* 加载提示样式 */
.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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

.symptom-card-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 0 0 0;
  margin: 0 0 0 0;
}
.symptom-card {
  background: #fff;
  border-radius: 48rpx;
  margin: 36rpx auto 0 auto;
  padding: 0 32rpx 0 40rpx;
  min-height: 120rpx;
  width: 78vw;
  max-width: 600rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4rpx 24rpx rgba(74, 109, 167, 0.06);
  transition: box-shadow 0.2s, background 0.2s;
  position: relative;
}
.symptom-card.selected {
  box-shadow: 0 8rpx 32rpx rgba(74, 109, 167, 0.13);
  background: linear-gradient(90deg, #f3f6fa 60%, #eaf0fa 100%);
}
.symptom-label {
  font-size: 34rpx;
  color: #222;
  font-weight: 500;
}
.emoji-circle {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #f0f1f5;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(74, 109, 167, 0.08);
  transition: background 0.2s, box-shadow 0.2s;
}
.emoji-circle.selected {
  background: linear-gradient(135deg, #4A6DA7 60%, #6fa8dc 100%);
  box-shadow: 0 4rpx 16rpx rgba(74, 109, 167, 0.18);
}
.symptom-emoji {
  font-size: 40rpx;
  color: #4A6DA7;
}
.emoji-circle.selected .symptom-emoji {
  color: #fff;
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
  padding: 48rpx 32rpx 48rpx 32rpx;
  background: transparent;
}
.back-btn, .skip-btn {
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
}
.back-btn:active, .skip-btn:active,
.btn-hover {
  transform: scale(0.96);
  filter: brightness(0.96);
  box-shadow: 0 2rpx 8rpx rgba(74, 109, 167, 0.10);
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
}
.skip-btn:disabled {
  opacity: 0.6;
}
.skip-icon {
  font-size: 36rpx;
  margin-left: 8rpx;
}
</style> 