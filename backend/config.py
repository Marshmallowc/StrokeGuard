"""
配置文件
"""
import os

# 数据库配置
MONGO_URI = "mongodb://root:zpf6fqzf@test-db-mongodb.ns-tcv4xipg.svc:27017"
DATABASE_NAME = "strokeguard"

# 应用配置
DEBUG = True
HOST = "0.0.0.0"
PORT = 8080

# 文件上传配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "dcm"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 创建必要的目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) 