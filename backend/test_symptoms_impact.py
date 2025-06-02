#!/usr/bin/env python3
"""
测试不同症状对预测结果的影响
"""
import requests
import json
import time
import sys

# API基础URL
BASE_URL = "http://localhost:8080"

# 测试用户ID前缀
TEST_USER_ID_PREFIX = "test_symptom_"

def print_result(title, response):
    """打印API响应结果"""
    print(f"\n=== {title} ===")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except:
        print(f"响应内容: {response.text[:100]}...")

def save_basic_info(user_id):
    """保存用户基本信息"""
    data = {
        "userId": user_id,
        "age": 45,
        "gender": "男",
        "height": 175,
        "weight": 70
    }
    response = requests.post(f"{BASE_URL}/api/user/basic-info", json=data)
    return response.status_code == 200

def save_lifestyle(user_id):
    """保存用户生活方式"""
    data = {
        "userId": user_id,
        "maritalStatus": "有",
        "workType": "私营企业",
        "residenceType": "城市",
        "smokingStatus": "吸烟"
    }
    response = requests.post(f"{BASE_URL}/api/user/lifestyle", json=data)
    return response.status_code == 200

def save_symptoms(user_id, symptoms):
    """保存用户症状"""
    data = {
        "userId": user_id,
        "hasSymptoms": "有" if symptoms else "无",
        "symptoms": symptoms
    }
    response = requests.post(f"{BASE_URL}/api/user/symptoms", json=data)
    return response.status_code == 200

def start_detection(user_id):
    """启动检测"""
    data = {
        "userId": user_id
    }
    response = requests.post(f"{BASE_URL}/api/detect/start", json=data)
    return response.status_code == 200

def wait_for_detection(user_id, max_wait=10):
    """等待检测完成"""
    for i in range(max_wait):
        response = requests.get(f"{BASE_URL}/api/detect/status?userId={user_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "finished":
                return True
        time.sleep(1)
    return False

def get_detection_report(user_id):
    """获取检测报告"""
    response = requests.get(f"{BASE_URL}/api/detect/report?userId={user_id}")
    if response.status_code == 200:
        return response.json().get("report", {})
    return None

def get_symptoms_list():
    """获取可用症状列表"""
    response = requests.get(f"{BASE_URL}/api/symptoms/list")
    if response.status_code == 200:
        return response.json().get("symptoms", [])
    return []

def test_symptom_combinations():
    """测试不同症状组合对预测结果的影响"""
    # 获取可用症状列表
    all_symptoms = get_symptoms_list()
    if not all_symptoms:
        print("获取症状列表失败")
        return
    
    print(f"获取到 {len(all_symptoms)} 个可用症状")
    
    # 测试不同症状组合
    test_cases = [
        {"name": "无症状", "symptoms": []},
        {"name": "单一症状-胸痛", "symptoms": [s for s in all_symptoms if s["key"] == "chestPain"]},
        {"name": "单一症状-头晕", "symptoms": [s for s in all_symptoms if s["key"] == "dizziness"]},
        {"name": "多个症状-胸痛和头晕", "symptoms": [s for s in all_symptoms if s["key"] in ["chestPain", "dizziness"]]},
        {"name": "多个症状-3个高风险症状", "symptoms": [s for s in all_symptoms if s["key"] in ["chestPain", "dizziness", "dyspnea"]]},
        {"name": "全部症状", "symptoms": all_symptoms}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        user_id = f"{TEST_USER_ID_PREFIX}{i}"
        print(f"\n开始测试: {test_case['name']} (用户ID: {user_id})")
        
        # 保存用户基本信息和生活方式
        if not save_basic_info(user_id):
            print("保存用户基本信息失败")
            continue
        
        if not save_lifestyle(user_id):
            print("保存用户生活方式失败")
            continue
        
        # 保存症状
        if not save_symptoms(user_id, test_case["symptoms"]):
            print("保存用户症状失败")
            continue
        
        # 启动检测
        if not start_detection(user_id):
            print("启动检测失败")
            continue
        
        # 等待检测完成
        if not wait_for_detection(user_id):
            print("检测超时")
            continue
        
        # 获取检测报告
        report = get_detection_report(user_id)
        if not report:
            print("获取检测报告失败")
            continue
        
        # 记录结果
        results.append({
            "test_case": test_case["name"],
            "user_id": user_id,
            "risk_percent": report.get("riskPercent"),
            "risk_level": report.get("riskLevel"),
            "symptoms_count": len(test_case["symptoms"])
        })
    
    # 打印结果汇总
    print("\n\n=== 测试结果汇总 ===")
    print(f"{'测试用例':<30} {'风险百分比':<15} {'风险级别':<10} {'症状数量':<10}")
    print("-" * 65)
    for result in results:
        print(f"{result['test_case']:<30} {result['risk_percent']:<15.2f} {result['risk_level']:<10} {result['symptoms_count']:<10}")

if __name__ == "__main__":
    test_symptom_combinations() 