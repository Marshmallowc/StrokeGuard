#!/usr/bin/env python3
"""
下载脑卒中风险预测模型文件
"""
import os
import sys
import requests
import tarfile
from tqdm import tqdm

# 模型文件存储目录
MODEL_DIR = "saved_stroke_model"

# 模型文件下载URL (这里需要替换为实际的模型文件URL)
MODEL_URL = "https://example.com/stroke_model.tar.gz"

def download_file(url, destination):
    """
    下载文件并显示进度条
    """
    if os.path.exists(destination):
        print(f"文件已存在: {destination}")
        return True
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        
        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        
        progress_bar.close()
        
        if total_size != 0 and progress_bar.n != total_size:
            print("下载的文件大小与预期不符")
            return False
        
        return True
    
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def extract_tarfile(tar_path, extract_path):
    """
    解压tar.gz文件
    """
    try:
        with tarfile.open(tar_path) as tar:
            tar.extractall(path=extract_path)
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def main():
    """
    主函数
    """
    print("开始下载脑卒中风险预测模型文件...")
    
    # 创建模型目录
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 下载模型文件
    tar_path = os.path.join(MODEL_DIR, "stroke_model.tar.gz")
    if download_file(MODEL_URL, tar_path):
        print("模型文件下载成功")
        
        # 解压模型文件
        if extract_tarfile(tar_path, MODEL_DIR):
            print("模型文件解压成功")
            
            # 删除压缩包
            os.remove(tar_path)
            print("清理完成")
            return 0
    
    print("模型文件下载或解压失败")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 