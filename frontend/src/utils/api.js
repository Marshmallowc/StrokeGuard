/**
 * API服务
 * 基于api_back.md文档实现与后端的接口通信
 */

// 基础URL
const BASE_URL = 'https://fobplhljlctv.sealoshzh.site/';

/**
 * 通用请求方法
 * @param {String} url - 接口路径
 * @param {Object} options - 请求选项
 * @returns {Promise} - 请求结果
 */
const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      ...options,
      success: (res) => {
        if (res.data.success === false) {
          uni.showToast({
            title: res.data.message || '请求失败',
            icon: 'none'
          });
          reject(res.data);
        } else {
          resolve(res.data);
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 用户信息管理接口
const userApi = {
  /**
   * 保存用户基本信息
   * @param {Object} data - 用户基本信息
   * @returns {Promise}
   */
  saveBasicInfo(data) {
    return request('api/user/basic-info', {
      method: 'POST',
      data,
      header: {
        'Content-Type': 'application/json'
      }
    });
  },

  /**
   * 保存用户生活方式信息
   * @param {Object} data - 用户生活方式信息
   * @returns {Promise}
   */
  saveLifestyle(data) {
    return request('api/user/lifestyle', {
      method: 'POST',
      data,
      header: {
        'Content-Type': 'application/json'
      }
    });
  },

  /**
   * 保存用户症状信息
   * @param {Object} data - 用户症状信息
   * @returns {Promise}
   */
  saveSymptoms(data) {
    return request('api/user/symptoms', {
      method: 'POST',
      data,
      header: {
        'Content-Type': 'application/json'
      }
    });
  },

  /**
   * 获取用户病历
   * @param {String} userId - 用户ID
   * @returns {Promise}
   */
  getMedicalRecord(userId) {
    return request(`api/user/medical-record?userId=${userId}`);
  },

  /**
   * 获取用户资料
   * @param {String} userId - 用户ID
   * @returns {Promise}
   */
  getProfile(userId) {
    return request(`api/user/profile?userId=${userId}`);
  },

  /**
   * 获取用户医疗记录列表
   * @param {String} userId - 用户ID
   * @returns {Promise}
   */
  getMedicalRecords(userId) {
    return request(`api/user/medical-records?userId=${userId}`);
  }
};

// 检测与报告接口
const detectApi = {
  /**
   * 启动检测
   * @param {String} userId - 用户ID
   * @returns {Promise}
   */
  startDetect(userId) {
    return request('api/detect/start', {
      method: 'POST',
      data: { userId },
      header: {
        'Content-Type': 'application/json'
      }
    });
  },

  /**
   * 启动图像检测
   * @param {Object} data - 包含userId、imageType和fileId的对象
   * @returns {Promise}
   */
  startImageDetect(data) {
    return request('api/detect/image', {
      method: 'POST',
      data,
      header: {
        'Content-Type': 'application/json'
      }
    });
  },

  /**
   * 检查检测状态
   * @param {String} userId - 用户ID
   * @returns {Promise}
   */
  checkStatus(userId) {
    return request(`api/detect/status?userId=${userId}`);
  },

  /**
   * 获取检测报告
   * @param {String} userId - 用户ID
   * @returns {Promise}
   */
  getReport(userId) {
    return request(`api/detect/report?userId=${userId}`);
  }
};

// 医疗记录管理接口
const medicalRecordApi = {
  /**
   * 上传医疗记录文件
   * @param {String} userId - 用户ID
   * @param {String} filePath - 文件路径
   * @returns {Promise}
   */
  uploadFile(userId, filePath) {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: `${BASE_URL}api/medical-record/upload`,
        filePath,
        name: 'file',
        formData: {
          userId
        },
        success: (res) => {
          const data = JSON.parse(res.data);
          if (data.success === false) {
            uni.showToast({
              title: data.message || '上传失败',
              icon: 'none'
            });
            reject(data);
          } else {
            resolve(data);
          }
        },
        fail: (err) => {
          uni.showToast({
            title: '上传失败',
            icon: 'none'
          });
          reject(err);
        }
      });
    });
  },

  /**
   * 删除医疗记录
   * @param {String} recordId - 记录ID
   * @returns {Promise}
   */
  deleteRecord(recordId) {
    return request(`api/medical-record/delete/${recordId}`, {
      method: 'DELETE'
    });
  }
};

// 其他接口
const otherApi = {
  /**
   * 获取可选症状列表
   * @returns {Promise}
   */
  getSymptomsList() {
    return request('api/symptoms/list');
  },

  /**
   * 健康检查接口
   * @returns {Promise}
   */
  healthCheck() {
    return request('health');
  }
};

export default {
  BASE_URL,
  userApi,
  detectApi,
  medicalRecordApi,
  otherApi
}; 