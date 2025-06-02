"""
输入验证模块
"""

def validate_basic_info(data):
    """
    验证用户基本信息
    
    Args:
        data (dict): 用户基本信息
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not data.get('userId'):
        return False, "用户ID不能为空"
    
    if not isinstance(data.get('age'), int) or data.get('age') < 0 or data.get('age') > 120:
        return False, "年龄必须是0-120之间的整数"
    
    if not data.get('gender') or data.get('gender') not in ["男", "女"]:
        return False, "性别必须是'男'或'女'"
    
    if not isinstance(data.get('height'), (int, float)) or data.get('height') < 50 or data.get('height') > 250:
        return False, "身高必须在50-250厘米之间"
    
    if not isinstance(data.get('weight'), (int, float)) or data.get('weight') < 20 or data.get('weight') > 300:
        return False, "体重必须在20-300公斤之间"
    
    # 验证平均血糖浓度
    if 'avg_glucose_level' in data:
        if not isinstance(data.get('avg_glucose_level'), (int, float)) or data.get('avg_glucose_level') < 50 or data.get('avg_glucose_level') > 400:
            return False, "平均血糖浓度必须在50-400 mg/dL之间"
    
    return True, ""

def validate_lifestyle(data):
    """
    验证用户生活方式信息
    
    Args:
        data (dict): 用户生活方式信息
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not data.get('userId'):
        return False, "用户ID不能为空"
    
    valid_marital_status = ["有", "无"]
    if data.get('maritalStatus') not in valid_marital_status:
        return False, f"婚姻状况必须是以下之一: {', '.join(valid_marital_status)}"
    
    valid_work_types = ["个体经营", "政府工作", "私营企业", "儿童", "无", "其他"]
    if data.get('workType') not in valid_work_types:
        return False, f"工作类型必须是以下之一: {', '.join(valid_work_types)}"
    
    valid_residence_types = ["城市", "农村", "城乡结合部"]
    if data.get('residenceType') not in valid_residence_types:
        return False, f"居住类型必须是以下之一: {', '.join(valid_residence_types)}"
    
    valid_smoking_status = ["吸烟", "从未吸烟", "曾经吸烟", "未知"]
    if data.get('smokingStatus') not in valid_smoking_status:
        return False, f"吸烟状态必须是以下之一: {', '.join(valid_smoking_status)}"
    
    return True, ""

def validate_symptoms(data):
    """
    验证用户症状信息
    
    Args:
        data (dict): 用户症状信息
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not data.get('userId'):
        return False, "用户ID不能为空"
    
    if data.get('hasSymptoms') not in ["有", "无"]:
        return False, "hasSymptoms必须是以下之一: 有, 无"
    
    # 如果有症状，验证symptoms是否为列表
    if data.get('hasSymptoms') == "有":
        if not isinstance(data.get('symptoms'), list):
            return False, "symptoms必须是列表格式"
        
        # 验证每个症状是否有key字段
        for symptom in data.get('symptoms', []):
            if not isinstance(symptom, dict):
                return False, "每个症状必须是字典格式"
            
            if not symptom.get('key'):
                return False, "每个症状必须包含key字段"
    
    return True, ""

def validate_file_upload(file):
    """
    验证上传的文件
    
    Args:
        file: 上传的文件对象
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    import config
    
    if not file:
        return False, "文件不能为空"
    
    if file.filename == '':
        return False, "文件名不能为空"
    
    # 检查文件扩展名
    allowed_extensions = config.ALLOWED_EXTENSIONS
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return False, f"只允许上传以下格式的文件: {', '.join(allowed_extensions)}"
    
    return True, "" 

def validate_image_file(file, image_type):
    """
    验证上传的MRI或CT图像文件
    
    Args:
        file: 上传的文件对象
        image_type: 图像类型 ('MRI' 或 'CT')
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    import config
    
    if not file:
        return False, "文件不能为空"
    
    if file.filename == '':
        return False, "文件名不能为空"
    
    # 检查文件扩展名 - 医学图像通常为DICOM格式(.dcm)或常见图像格式
    allowed_extensions = {"dcm", "jpg", "jpeg", "png"}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return False, f"{image_type}图像必须是以下格式之一: {', '.join(allowed_extensions)}"
    
    # TODO: 可以在这里添加更多的图像验证逻辑
    # 例如检查图像尺寸、格式等
    
    return True, "" 