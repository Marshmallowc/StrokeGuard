#!/usr/bin/env python3
"""
API测试脚本 - 测试hello.py中的API接口
"""
import requests
import json
import time
import sys

# API基础URL
BASE_URL = "http://localhost:8080"

# 测试用户ID
TEST_USER_ID = "test_user_123"

def print_result(title, response):
    """打印API响应结果"""
    print(f"\n=== {title} ===")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except:
        print(f"响应内容: {response.text[:100]}...")

def test_health():
    """测试健康检查接口"""
    response = requests.get(f"{BASE_URL}/health")
    print_result("健康检查", response)
    return response.status_code == 200

def test_basic_info():
    """测试保存用户基本信息"""
    data = {
        "userId": TEST_USER_ID,
        "age": 45,
        "gender": "男",
        "height": 175,
        "weight": 70
    }
    response = requests.post(f"{BASE_URL}/api/user/basic-info", json=data)
    print_result("保存用户基本信息", response)
    return response.status_code == 200

def test_lifestyle():
    """测试保存用户生活方式"""
    data = {
        "userId": TEST_USER_ID,
        "maritalStatus": "有",
        "workType": "私营企业",
        "residenceType": "城市",
        "smokingStatus": "吸烟"
    }
    response = requests.post(f"{BASE_URL}/api/user/lifestyle", json=data)
    print_result("保存用户生活方式", response)
    return response.status_code == 200

def test_symptoms():
    """测试保存用户症状"""
    # 先获取可用症状列表
    symptoms_response = requests.get(f"{BASE_URL}/api/symptoms/list")
    if symptoms_response.status_code != 200:
        print("获取症状列表失败")
        return False
    
    # 选择前两个症状
    available_symptoms = symptoms_response.json()["symptoms"][:2]
    
    data = {
        "userId": TEST_USER_ID,
        "hasSymptoms": "有",
        "symptoms": available_symptoms
    }
    response = requests.post(f"{BASE_URL}/api/user/symptoms", json=data)
    print_result("保存用户症状", response)
    return response.status_code == 200

def test_get_profile():
    """测试获取用户资料"""
    response = requests.get(f"{BASE_URL}/api/user/profile?userId={TEST_USER_ID}")
    print_result("获取用户资料", response)
    return response.status_code == 200

def test_get_medical_record():
    """测试获取用户病历"""
    response = requests.get(f"{BASE_URL}/api/user/medical-record?userId={TEST_USER_ID}")
    print_result("获取用户病历", response)
    return response.status_code == 200

def test_start_detection():
    """测试启动检测"""
    data = {
        "userId": TEST_USER_ID
    }
    response = requests.post(f"{BASE_URL}/api/detect/start", json=data)
    print_result("启动检测", response)
    return response.status_code == 200

def test_detection_status():
    """测试检测状态"""
    # 等待一段时间让检测进行
    time.sleep(1)
    
    response = requests.get(f"{BASE_URL}/api/detect/status?userId={TEST_USER_ID}")
    print_result("检测状态", response)
    return response.status_code == 200

def test_detection_report():
    """测试获取检测报告"""
    # 等待检测完成
    time.sleep(2)
    
    response = requests.get(f"{BASE_URL}/api/detect/report?userId={TEST_USER_ID}")
    print_result("检测报告", response)
    return response.status_code == 200

def test_upload_file():
    """测试上传文件"""
    # 创建一个测试PDF文件
    with open("test_file.pdf", "wb") as f:
        f.write(b"%PDF-1.5\n%Test PDF file for API testing\n")
    
    files = {
        'file': ('test_file.pdf', open('test_file.pdf', 'rb'), 'application/pdf')
    }
    data = {
        'userId': TEST_USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/api/medical-record/upload", files=files, data=data)
    print_result("上传文件", response)
    
    # 保存记录ID用于后续删除测试
    if response.status_code == 200:
        global uploaded_record_id
        # 获取用户病历记录
        records_response = requests.get(f"{BASE_URL}/api/user/medical-records?userId={TEST_USER_ID}")
        if records_response.status_code == 200 and records_response.json()["success"]:
            records = records_response.json()["records"]
            if records:
                uploaded_record_id = records[0]["recordId"]
    
    return response.status_code == 200

def test_get_medical_records():
    """测试获取用户病历记录列表"""
    response = requests.get(f"{BASE_URL}/api/user/medical-records?userId={TEST_USER_ID}")
    print_result("获取用户病历记录", response)
    return response.status_code == 200

def test_delete_medical_record():
    """测试删除病历记录"""
    global uploaded_record_id
    if not uploaded_record_id:
        print("没有可删除的记录")
        return False
    
    response = requests.delete(f"{BASE_URL}/api/medical-record/delete/{uploaded_record_id}")
    print_result("删除病历记录", response)
    return response.status_code == 200

def run_all_tests():
    """运行所有测试"""
    tests = [
        ("健康检查", test_health),
        ("保存用户基本信息", test_basic_info),
        ("保存用户生活方式", test_lifestyle),
        ("保存用户症状", test_symptoms),
        ("获取用户资料", test_get_profile),
        ("获取用户病历", test_get_medical_record),
        ("启动检测", test_start_detection),
        ("检测状态", test_detection_status),
        ("检测报告", test_detection_report),
        ("上传文件", test_upload_file),
        ("获取用户病历记录", test_get_medical_records),
        ("删除病历记录", test_delete_medical_record)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n开始测试: {name}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"测试出错: {str(e)}")
            results.append((name, False))
    
    # 打印测试结果汇总
    print("\n\n=== 测试结果汇总 ===")
    all_passed = True
    for name, success in results:
        status = "通过" if success else "失败"
        print(f"{name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n所有测试通过!")
        return 0
    else:
        print("\n部分测试失败!")
        return 1

if __name__ == "__main__":
    # 存储上传的记录ID
    uploaded_record_id = None
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    if len(sys.argv) > 2:
        TEST_USER_ID = sys.argv[2]
    
    print(f"使用基础URL: {BASE_URL}")
    print(f"使用测试用户ID: {TEST_USER_ID}")
    
    # 运行测试
    sys.exit(run_all_tests()) 