# 脑卒中风险检测小程序 后端接口文档

婚姻状况（有/无），工作类型（个体经营、政府工作、私营企业、儿童、无），居住类型（城市、农村），吸烟状况["吸烟", "从未吸烟", "曾经吸烟", "未知"]，症状一个13种在下面一一给你列举了（有/无），年龄、身高、体重、性别。病历一共就只有这些东西，有啥写啥，不要瞎写

症状一共13种：
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

## 1. 用户信息与病历管理

### 1.1. 提交/保存用户基本信息
- **接口地址**：`POST /api/user/basic-info`
- **说明**：保存用户的基本信息（年龄、性别、身高、体重等）
- **请求参数（JSON）**：
  ```json
  {
    "userId": "string",         // 用户唯一标识
    "age": 65,                  // 年龄，整数
    "gender": "男",             // 性别，取值："男"或"女"
    "height": 170,              // 身高，单位：厘米，整数
    "weight": 65                // 体重，单位：千克，整数或小数
  }
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "message": "保存成功"
  }
  ```

### 1.2. 提交/保存用户生活方式信息
- **接口地址**：`POST /api/user/lifestyle`
- **说明**：保存用户的生活方式信息（婚姻、工作、居住、吸烟等）
- **请求参数（JSON）**：
  ```json
  {
    "userId": "string",                // 用户唯一标识
    "maritalStatus": "有",             // 婚姻状况，取值："有"或"无"
    "workType": "私营企业",            // 工作类型，取值："个体经营"、"政府工作"、"私营企业"、"儿童"、"无"
    "residenceType": "城市",           // 居住类型，取值："城市"或"农村"
    "smokingStatus": "吸烟"            // 吸烟状况，取值："吸烟"、"从未吸烟"、"曾经吸烟"、"未知"
  }
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "message": "保存成功"
  }
  ```

### 1.3. 提交/保存用户症状信息
- **接口地址**：`POST /api/user/symptoms`
- **说明**：保存用户症状信息
- **请求参数（JSON）**：
  ```json
  {
    "userId": "string",         // 用户唯一标识
    "hasSymptoms": "有",        // 是否有症状，只能是"有"或"无"
    "symptoms": [               // 当hasSymptoms为"有"时，提供具体症状列表
      {
        "key": "chestPain",     // 症状唯一标识
        "label": "胸痛或胸闷",   // 症状名称
        "emoji": "💔"           // 症状对应的emoji
      },
      {
        "key": "dizziness",
        "label": "头晕目眩",
        "emoji": "🌀"
      },
      // 可能包含的其他症状...
    ]
  }
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "message": "保存成功"
  }
  ```

### 1.4. 获取用户完整病历
- **接口地址**：`GET /api/user/medical-record`
- **说明**：获取用户的完整病历信息（基本信息、生活方式、症状、检测报告等）
- **请求参数（Query）**：
  ```
  userId=xxx
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "data": {
      "basicInfo": { 
        "age": 65, 
        "gender": "男", 
        "height": 170, 
        "weight": 65 
      },
      "lifestyle": { 
        "maritalStatus": "有", 
        "workType": "私营企业", 
        "residenceType": "城市", 
        "smokingStatus": "吸烟" 
      },
      "symptoms": { 
        "hasSymptoms": "有" 
      },
      "report": { /* 检测报告内容，见下文 */ }
    }
  }
  ```

---

## 2. 检测与报告

### 2.1. 启动检测
- **接口地址**：`POST /api/detect/start`
- **说明**：前端点击"开始检测"后调用，通知后端开始检测
- **请求参数（JSON）**：
  ```json
  {
    "userId": "string"          // 用户唯一标识
  }
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "message": "检测已启动"
  }
  ```

### 2.2. 查询检测进度/状态
- **接口地址**：`GET /api/detect/status`
- **说明**：轮询或定时查询检测是否完成
- **请求参数（Query）**：
  ```
  userId=xxx                    // 用户唯一标识
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "status": "processing",     // 检测状态：processing(进行中) | finished(已完成) | failed(失败)
    "progress": 60              // 进度百分比，0-100的整数
  }
  ```

### 2.3. 获取检测报告
- **接口地址**：`GET /api/detect/report`
- **说明**：检测完成后，获取检测报告内容
- **请求参数（Query）**：
  ```
  userId=xxx                    // 用户唯一标识
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "report": {
      "riskPercent": 42,                // 风险百分比，0-100的整数
      "riskLevel": "中风险",             // 风险等级描述
      "riskDescription": "您的脑卒中风险中等", // 风险描述文本
      "riskAdvice": "建议近期咨询医生，检查相关指标，改善生活习惯，增加体育锻炼，控制体重。", // 建议文本
      "details": {
        "ageScore": 10,                 // 年龄因素得分
        "bmiScore": 10,                 // BMI因素得分
        "smokingScore": 15,             // 吸烟因素得分
        "symptomScore": 7               // 症状因素得分
      }
    }
  }
  ```

---

## 3. 电子病历上传

### 3.1. 上传电子病历文件
- **接口地址**：`POST /api/medical-record/upload`
- **说明**：上传 PDF 等电子病历文件
- **请求参数**：`multipart/form-data`
  - `userId`：string            // 用户唯一标识
  - `file`：PDF 文件            // 上传的PDF文件
- **返回示例**：
  ```json
  {
    "success": true,
    "fileUrl": "https://xxx/xxx.pdf"    // 上传成功后的文件访问URL
  }
  ```

---

## 4. 其他（可选）

### 4.1. 获取用户历史病历列表
- **接口地址**：`GET /api/user/medical-records`
- **说明**：获取用户所有历史病历简要信息
- **请求参数（Query）**：
  ```
  userId=xxx                    // 用户唯一标识
  ```
- **返回示例**：
  ```json
  {
    "success": true,
    "records": [
      { 
        "recordId": "xxx",      // 病历ID
        "date": "2024-06-01",   // 记录日期
        "summary": "低风险"      // 风险简要描述
      }
    ]
  }
  ```

---

# 总结

**后端实现的接口一览：**
1. 用户信息相关
   - 基本信息（年龄、性别、身高、体重）
   - 生活方式（婚姻状况、工作类型、居住类型、吸烟状况）
   - 症状（有/无）
   - 病历获取
2. 检测相关（启动检测、检测状态、获取报告）
3. 电子病历上传
4. 可选：历史病历列表

**参数值范围说明：**
- 婚姻状况：有/无
- 工作类型：个体经营、政府工作、私营企业、儿童、无
- 居住类型：城市、农村
- 吸烟状况：吸烟、从未吸烟、曾经吸烟、未知
- 症状：有/无

如需接口字段调整或有特殊业务需求，可随时补充说明！ 