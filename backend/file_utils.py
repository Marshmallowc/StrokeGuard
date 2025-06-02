"""
文件处理工具模块
"""
import os
import uuid
from datetime import datetime

class FileHandler:
    """文件处理类"""
    
    def __init__(self, storage_dir="uploads"):
        """
        初始化文件处理器
        
        Args:
            storage_dir (str): 文件存储目录
        """
        self.storage_dir = storage_dir
        
        # 确保存储目录存在
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def save_file(self, file, user_id):
        """
        保存上传的文件
        
        Args:
            file: 上传的文件对象
            user_id (str): 用户ID
            
        Returns:
            dict: 包含文件信息的字典
        """
        # 生成唯一文件名
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
        
        # 构建文件路径
        file_path = os.path.join(self.storage_dir, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 构建文件URL
        # 注意：在实际生产环境中，应该使用配置的域名和CDN
        file_url = f"/uploads/{unique_filename}"
        
        return {
            "originalName": original_filename,
            "fileName": unique_filename,
            "filePath": file_path,
            "fileUrl": file_url,
            "fileSize": os.path.getsize(file_path),
            "uploadTime": datetime.now()
        }
    
    def save_medical_image(self, file, user_id, image_type):
        """
        保存上传的医学图像文件（MRI或CT）
        
        Args:
            file: 上传的文件对象
            user_id (str): 用户ID
            image_type (str): 图像类型 ('MRI' 或 'CT')
            
        Returns:
            dict: 包含文件信息的字典
        """
        # 生成唯一文件名，包含图像类型前缀
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{image_type}_{user_id}_{uuid.uuid4().hex}{file_ext}"
        
        # 构建文件路径
        file_path = os.path.join(self.storage_dir, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 构建文件URL
        file_url = f"/uploads/{unique_filename}"
        
        return {
            "originalName": original_filename,
            "fileName": unique_filename,
            "filePath": file_path,
            "fileUrl": file_url,
            "fileSize": os.path.getsize(file_path),
            "imageType": image_type,
            "uploadTime": datetime.now()
        }
    
    def delete_file(self, filename):
        """
        删除文件
        
        Args:
            filename (str): 文件名
            
        Returns:
            bool: 是否删除成功
        """
        file_path = os.path.join(self.storage_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False 