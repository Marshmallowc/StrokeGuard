# 脑卒中风险检测小程序 API 接口文档

本文档描述了脑卒中风险检测小程序的后端 API 接口。所有接口均返回 JSON 格式的数据。

## 基础信息

- 基础URL: `https://fobplhljlctv.sealoshzh.site/`
- 所有POST请求的Content-Type应设置为: `application/json`
- 文件上传的Content-Type应设置为: `multipart/form-data`

## 通用返回格式

所有API返回均包含以下基本字段：

```json
{
  "success": true/false,  // 接口调用是否成功
  "message": "提示信息"    // 成功或错误提示信息
}
```

成功时通常还会包含数据字段：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

## 用户信息管理接口

### 1. 保存用户基本信息

**接口**: `/api/user/basic-info`

**方法**: `POST`

**请求参数**:

```json
{
  "userId": "user123",      // 用户ID，必填
  "age": 45,                // 年龄，必填，整数
  "gender": "男",           // 性别，必填，字符串
  "height": 175,            // 身高，单位cm，必填，数字
  "weight": 70              // 体重，单位kg，必填，数字
}
```

**成功响应**:

```json
{
  "success": true,
  "message": "保存成功"
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "年龄必须为正整数"  // 具体错误信息
}
```

### 2. 保存用户生活方式信息

**接口**: `/api/user/lifestyle`

**方法**: `POST`

**请求参数**:

```json
{
  "userId": "user123",           // 用户ID，必填
  "maritalStatus": "有",         // 婚姻状况，必填，"有"或"无"
  "workType": "私营企业",        // 工作类型，必填，可选值："私营企业", "国有企业", "政府机构", "事业单位", "自由职业", "退休", "其他"
  "residenceType": "城市",       // 居住类型，必填，"城市"或"农村"
  "smokingStatus": "吸烟"        // 吸烟状态，必填，可选值："吸烟", "从未吸烟", "曾经吸烟", "未知"
}
```

**成功响应**:

```json
{
  "success": true,
  "message": "保存成功"
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "婚姻状况必须为'有'或'无'"  // 具体错误信息
}
```

### 3. 保存用户症状信息

**接口**: `/api/user/symptoms`

**方法**: `POST`

**请求参数**:

```json
{
  "userId": "user123",      // 用户ID，必填
  "symptoms": [             // 症状列表，数组
    {
      "key": "chestPain",
      "label": "胸痛或胸闷",
      "emoji": "💔"
    },
    {
      "key": "dizziness",
      "label": "头晕目眩",
      "emoji": "🌀"
    }
  ]
}
```

**成功响应**:

```json
{
  "success": true,
  "message": "保存成功"
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "用户ID不能为空"  // 具体错误信息
}
```

### 4. 获取用户病历

**接口**: `/api/user/medical-record`

**方法**: `GET`

**请求参数**:

```
?userId=user123  // 用户ID，必填
```

**成功响应**:

```json
{
  "success": true,
  "data": {
    "userId": "user123",
    "basicInfo": {
      "age": 45,
      "gender": "男",
      "height": 175,
      "weight": 70
    },
    "lifestyle": {
      "maritalStatus": "有",
      "workType": "私营企业",
      "residenceType": "城市",
      "smokingStatus": "吸烟"
    },
    "symptoms": [
      {
        "key": "chestPain",
        "label": "胸痛或胸闷",
        "emoji": "💔"
      }
    ],
    "report": {
      "riskPercent": 35.8,
      "riskLevel": "中风险",
      "riskDescription": "您的脑卒中风险中等",
      "riskAdvice": "建议近期咨询医生，检查相关指标",
      "details": {
        "modelScore": 35.8
      },
      "createdAt": "2023-06-15T08:30:45.123Z"
    }
  }
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "用户不存在"
}
```

### 5. 获取用户资料

**接口**: `/api/user/profile`

**方法**: `GET`

**请求参数**:

```
?userId=user123  // 用户ID，必填
```

**成功响应**:

```json
{
  "success": true,
  "profile": {
    "basicInfo": {
      "age": 45,
      "gender": "男",
      "height": 175,
      "weight": 70
    },
    "lifestyle": {
      "maritalStatus": "有",
      "workType": "私营企业",
      "residenceType": "城市",
      "smokingStatus": "吸烟"
    },
    "createdAt": "2023-06-15T08:30:45.123Z"
  }
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "用户不存在"
}
```

## 检测与报告接口

### 1. 启动检测

**接口**: `/api/detect/start`

**方法**: `POST`

**请求参数**:

```json
{
  "userId": "user123"  // 用户ID，必填
}
```

**成功响应**:

```json
{
  "success": true,
  "message": "检测已启动"
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "用户不存在"
}
```

### 2. 检查检测状态

**接口**: `/api/detect/status`

**方法**: `GET`

**请求参数**:

```
?userId=user123  // 用户ID，必填
```

**成功响应**:

```json
{
  "success": true,
  "status": "processing",  // 状态：processing, finished
  "progress": 75           // 进度，0-100的整数
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "未找到检测记录"
}
```

### 3. 获取检测报告

**接口**: `/api/detect/report`

**方法**: `GET`

**请求参数**:

```
?userId=user123  // 用户ID，必填
```

**成功响应**:

```json
{
  "success": true,
  "report": {
    "userId": "user123",
    "riskPercent": 35.8,
    "riskLevel": "中风险",
    "riskDescription": "您的脑卒中风险中等",
    "riskAdvice": "建议近期咨询医生，检查相关指标",
    "details": {
      "modelScore": 35.8
    },
    "createdAt": "2023-06-15T08:30:45.123Z",
    "completedAt": "2023-06-15T08:31:15.456Z"
  }
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "报告未完成或不存在"
}
```

## 医疗记录管理接口

### 1. 上传医疗记录文件

**接口**: `/api/medical-record/upload`

**方法**: `POST`

**请求参数**: 
- 使用 `multipart/form-data` 格式
- `file`: 文件对象，支持PDF、JPG、PNG格式，最大10MB
- `userId`: 用户ID，字符串

**成功响应**:

```json
{
  "success": true,
  "fileUrl": "/uploads/user123_20230615_123456.pdf"
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "文件格式不支持，请上传PDF、JPG或PNG格式"
}
```

### 2. 获取用户医疗记录列表

**接口**: `/api/user/medical-records`

**方法**: `GET`

**请求参数**:

```
?userId=user123  // 用户ID，必填
```

**成功响应**:

```json
{
  "success": true,
  "records": [
    {
      "recordId": "record123",
      "date": "2023-06-15",
      "summary": "病历文件",
      "fileUrl": "/uploads/user123_20230615_123456.pdf"
    },
    {
      "recordId": "record124",
      "date": "2023-06-10",
      "summary": "病历文件",
      "fileUrl": "/uploads/user123_20230610_123456.jpg"
    }
  ]
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "用户ID不能为空"
}
```

### 3. 删除医疗记录

**接口**: `/api/medical-record/delete/:recordId`

**方法**: `DELETE`

**URL参数**:
- `recordId`: 记录ID，必填

**成功响应**:

```json
{
  "success": true,
  "message": "记录已删除"
}
```

**失败响应**:

```json
{
  "success": false,
  "message": "记录不存在"
}
```

## 其他接口

### 1. 获取可选症状列表

**接口**: `/api/symptoms/list`

**方法**: `GET`

**请求参数**: 无

**成功响应**:

```json
{
  "success": true,
  "symptoms": [
    {
      "key": "chestPain",
      "label": "胸痛或胸闷",
      "emoji": "💔"
    },
    {
      "key": "dyspnea",
      "label": "呼吸急促",
      "emoji": "😮‍💨"
    },
    {
      "key": "arrhythmia",
      "label": "心律不齐",
      "emoji": "💗"
    },
    {
      "key": "fatigue",
      "label": "疲劳虚弱",
      "emoji": "😪"
    },
    {
      "key": "dizziness",
      "label": "头晕目眩",
      "emoji": "🌀"
    },
    {
      "key": "swelling",
      "label": "身体水肿",
      "emoji": "🫧"
    },
    {
      "key": "sweating",
      "label": "异常出汗",
      "emoji": "💧"
    },
    {
      "key": "neckPain",
      "label": "颈肩背部疼痛",
      "emoji": "🤕"
    },
    {
      "key": "cough",
      "label": "持续性咳嗽",
      "emoji": "😷"
    },
    {
      "key": "nausea",
      "label": "恶心想吐",
      "emoji": "🤢"
    },
    {
      "key": "coldLimbs",
      "label": "手脚发凉",
      "emoji": "🧊"
    },
    {
      "key": "snoring",
      "label": "睡觉打鼾",
      "emoji": "😴"
    },
    {
      "key": "anxiety",
      "label": "感到焦虑",
      "emoji": "😰"
    }
  ]
}
```

### 2. 健康检查接口

**接口**: `/health`

**方法**: `GET`

**请求参数**: 无

**成功响应**:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "connected"
}
```

**失败响应**:

```json
{
  "status": "error",
  "version": "1.0.0",
  "database": "disconnected"
}
```

## 文件访问接口

### 获取上传的文件

**接口**: `/uploads/:filename`

**方法**: `GET`

**URL参数**:
- `filename`: 文件名，必填

**成功响应**:
- 文件内容，带有适当的Content-Type头

**失败响应**:
- HTTP 404 Not Found 