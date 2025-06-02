/**
 * 全局状态管理
 */

import { reactive } from 'vue';

// 创建状态存储
const store = {
  // 状态
  state: reactive({
    userId: uni.getStorageSync('userId') || '',
    userInfo: uni.getStorageSync('userInfo') || {},
    medicalRecords: [],
    currentReport: null,
    detectStatus: {
      status: 'idle', // idle, processing, finished
      progress: 0
    }
  }),

  // 更新用户ID
  setUserId(userId) {
    this.state.userId = userId;
    uni.setStorageSync('userId', userId);
  },

  // 更新用户信息
  setUserInfo(userInfo) {
    this.state.userInfo = userInfo;
    uni.setStorageSync('userInfo', userInfo);
  },

  // 更新医疗记录列表
  setMedicalRecords(records) {
    this.state.medicalRecords = records;
  },

  // 更新当前报告
  setCurrentReport(report) {
    this.state.currentReport = report;
  },

  // 更新检测状态
  setDetectStatus(status, progress) {
    this.state.detectStatus = {
      status,
      progress: progress || 0
    };
  },

  // 清除用户数据
  clearUserData() {
    this.state.userId = '';
    this.state.userInfo = {};
    this.state.medicalRecords = [];
    this.state.currentReport = null;
    this.state.detectStatus = {
      status: 'idle',
      progress: 0
    };
    uni.removeStorageSync('userId');
    uni.removeStorageSync('userInfo');
  }
};

export default store; 