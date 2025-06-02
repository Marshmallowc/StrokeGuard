# 脑卒中风险检测小程序后端

这是脑卒中风险检测小程序的后端API实现，基于Flask和MongoDB。

## 技术栈

- Python 3.x
- Flask (Web框架)
- PyMongo (MongoDB客户端)
- MongoDB (数据库)

## 项目结构

- `hello.py`: 主应用程序文件，包含所有API端点
- `risk_calculator.py`: 风险计算模块
- `file_utils.py`: 文件处理工具模块
- `validators.py`: 输入验证模块
- `config.py`: 配置文件
- `requirements.txt`: 项目依赖
- `entrypoint.sh`: 启动脚本
- `test_api.py`: API测试脚本

## API端点

详细的API文档请参考 `api.md` 文件。

主要功能包括：
1. 用户信息与病历管理
   - 保存/获取用户基本信息
   - 保存/获取用户生活方式信息
   - 保存/获取用户症状信息
   - 获取用户完整病历
   - 获取用户基本资料
2. 检测与报告
   - 启动风险检测
   - 查询检测进度/状态
   - 获取检测报告
3. 电子病历上传
   - 上传电子病历文件
   - 删除电子病历文件
   - 访问上传的文件
4. 其他接口
   - 获取用户历史病历列表
   - 获取可选症状列表
   - 健康检查接口

## 启动项目

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python hello.py
```

服务将在 `http://localhost:8080` 上运行。

## 测试接口

项目提供了一个测试脚本用于测试所有API接口：

```bash
# 安装测试依赖
pip install requests

# 运行测试脚本
python test_api.py [base_url] [test_user_id]

# 例如：
python test_api.py http://localhost:8080 test_user_123
```

## 数据库结构

项目使用MongoDB数据库，包含以下集合：
- `users`: 用户基本信息、生活方式和症状
- `reports`: 检测报告
- `medical_records`: 上传的电子病历记录 