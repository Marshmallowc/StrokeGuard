from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymongo
from bson.objectid import ObjectId
import os
from datetime import datetime
import config
from validators import validate_basic_info, validate_lifestyle, validate_symptoms, validate_file_upload, validate_image_file
from risk_calculator import RiskCalculator
from file_utils import FileHandler

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# MongoDB connection
client = pymongo.MongoClient(config.MONGO_URI)
db = client[config.DATABASE_NAME]

# Collections
users_collection = db["users"]
medical_records_collection = db["medical_records"]
reports_collection = db["reports"]

# 初始化文件处理器
file_handler = FileHandler(storage_dir=config.UPLOAD_FOLDER)

# User Information and Medical Record Management

@app.route('/api/user/basic-info', methods=['POST'])
def save_basic_info():
    data = request.json
    
    # 验证输入数据
    is_valid, error_message = validate_basic_info(data)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400
    
    user_id = data.get('userId')
    
    # Check if user exists
    user = users_collection.find_one({"userId": user_id})
    
    if user:
        # Update existing user
        users_collection.update_one(
            {"userId": user_id},
            {"$set": {
                "basicInfo": {
                    "age": data.get('age'),
                    "gender": data.get('gender'),
                    "height": data.get('height'),
                    "weight": data.get('weight'),
                    "avg_glucose_level": data.get('avg_glucose_level', 90.0)
                }
            }}
        )
    else:
        # Create new user
        users_collection.insert_one({
            "userId": user_id,
            "basicInfo": {
                "age": data.get('age'),
                "gender": data.get('gender'),
                "height": data.get('height'),
                "weight": data.get('weight'),
                "avg_glucose_level": data.get('avg_glucose_level', 90.0)
            },
            "createdAt": datetime.now()
        })
    
    return jsonify({"success": True, "message": "保存成功"})



@app.route('/api/user/lifestyle', methods=['POST'])
def save_lifestyle():
    data = request.json
    
    # 验证输入数据
    is_valid, error_message = validate_lifestyle(data)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400
    
    user_id = data.get('userId')
    
    # Update user lifestyle info
    users_collection.update_one(
        {"userId": user_id},
        {"$set": {
            "lifestyle": {
                "maritalStatus": data.get('maritalStatus'),
                "workType": data.get('workType'),
                "residenceType": data.get('residenceType'),
                "smokingStatus": data.get('smokingStatus')
            }
        }},
        upsert=True
    )
    
    return jsonify({"success": True, "message": "保存成功"})



@app.route('/api/user/symptoms', methods=['POST'])
def save_symptoms():
    data = request.json
    
    # 打印接收到的数据，用于调试
    print("接收到的症状数据:", data)
    
    # 检查必要字段
    if not data or not data.get('userId'):
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400
    
    user_id = data.get('userId')
    has_symptoms = data.get('hasSymptoms')
    
    # 验证hasSymptoms字段
    if has_symptoms not in ["有", "无"]:
        return jsonify({"success": False, "message": "hasSymptoms必须是'有'或'无'"}), 400
    
    # 获取症状列表的完整信息
    symptoms_list = [
        {"key": "chestPain", "label": "胸痛或胸闷", "emoji": "💔"},
        {"key": "dyspnea", "label": "呼吸急促", "emoji": "😮‍💨"},
        {"key": "arrhythmia", "label": "心律不齐", "emoji": "💗"},
        {"key": "fatigue", "label": "疲劳虚弱", "emoji": "😪"},
        {"key": "dizziness", "label": "头晕目眩", "emoji": "🌀"},
        {"key": "swelling", "label": "身体水肿", "emoji": "🫧"},
        {"key": "sweating", "label": "异常出汗", "emoji": "💧"},
        {"key": "neckPain", "label": "颈肩背部疼痛", "emoji": "🤕"},
        {"key": "cough", "label": "持续性咳嗽", "emoji": "😷"},
        {"key": "nausea", "label": "恶心想吐", "emoji": "🤢"},
        {"key": "coldLimbs", "label": "手脚发凉", "emoji": "🧊"},
        {"key": "snoring", "label": "睡觉打鼾", "emoji": "😴"},
        {"key": "anxiety", "label": "感到焦虑", "emoji": "😰"}
    ]
    
    # 创建一个查找表，以便通过key快速查找症状信息
    symptoms_map = {symptom["key"]: symptom for symptom in symptoms_list}
    
    # 转换数据格式
    symptoms_data = []
    if has_symptoms == "有" and 'symptoms' in data and isinstance(data['symptoms'], list):
        for symptom in data['symptoms']:
            if isinstance(symptom, dict) and 'key' in symptom:
                symptom_key = symptom['key']
                if symptom_key in symptoms_map:
                    # 存储完整的症状信息，包括emoji和label
                    symptoms_data.append({
                        "key": symptom_key,
                        "emoji": symptoms_map[symptom_key]["emoji"],
                        "label": symptoms_map[symptom_key]["label"],
                        "value": "有"
                    })
    
    # 更新用户症状数据
    users_collection.update_one(
        {"userId": user_id},
        {"$set": {
            "hasSymptoms": has_symptoms,
            "symptoms": symptoms_data
        }},
        upsert=True
    )
    
    return jsonify({"success": True, "message": "保存成功"})

@app.route('/api/user/medical-record', methods=['GET'])
def get_medical_record():
    user_id = request.args.get('userId')
    
    # Get user data
    user = users_collection.find_one({"userId": user_id}, {"_id": 0})
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
    
    # Get latest report
    report = reports_collection.find_one(
        {"userId": user_id},
        {"_id": 0},
        sort=[("createdAt", pymongo.DESCENDING)]
    )
    
    # Combine data
    result = user
    if report:
        result["report"] = report
    
    return jsonify({"success": True, "data": result})

# Detection and Report
@app.route('/api/detect/start', methods=['POST'])
def start_detection():
    data = request.json
    user_id = data.get('userId')
    
    # 添加调试日志
    print(f"启动用户 {user_id} 的风险检测")
    
    # Get user data for risk calculation
    user = users_collection.find_one({"userId": user_id})
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
    
    # 检查是否已有进行中的检测任务
    existing_report = reports_collection.find_one(
        {"userId": user_id, "status": "processing"},
        sort=[("createdAt", pymongo.DESCENDING)]
    )
    
    if existing_report:
        print(f"用户 {user_id} 已有进行中的检测任务")
        return jsonify({"success": True, "message": "检测已在进行中"}), 200
    
    # Create detection task
    reports_collection.insert_one({
        "userId": user_id,
        "status": "processing",
        "progress": 0,
        "createdAt": datetime.now()
    })
    
    # 在后台线程中执行风险计算
    import threading
    thread = threading.Thread(target=calculate_risk, args=(user_id,))
    thread.daemon = True
    thread.start()
    
    print(f"用户 {user_id} 的风险检测已启动，计算在后台线程中进行")
    return jsonify({"success": True, "message": "检测已启动"})

@app.route('/api/detect/status', methods=['GET'])
def check_detection_status():
    user_id = request.args.get('userId')
    
    # Get latest report status
    report = reports_collection.find_one(
        {"userId": user_id},
        sort=[("createdAt", pymongo.DESCENDING)]
    )
    
    if not report:
        return jsonify({"success": False, "message": "未找到检测记录"}), 404
    
    return jsonify({
        "success": True,
        "status": report.get("status", "processing"),
        "progress": report.get("progress", 0)
    })

@app.route('/api/detect/report', methods=['GET'])
def get_detection_report():
    user_id = request.args.get('userId')
    
    # 添加调试日志
    print(f"获取用户 {user_id} 的检测报告")
    
    # Get latest report
    report = reports_collection.find_one(
        {"userId": user_id},
        {"_id": 0},  # 移除了status和progress的过滤，以便我们可以看到完整数据
        sort=[("createdAt", pymongo.DESCENDING)]
    )
    
    # 添加调试日志
    print(f"查询到的报告数据: {report}")
    
    if not report:
        return jsonify({"success": False, "message": "报告不存在"}), 404
    
    # 临时移除对status的检查，以便我们可以看到任何状态的报告
    # if report.get("status") != "finished":
    #     return jsonify({"success": False, "message": "报告未完成"}), 404
    
    return jsonify({"success": True, "report": report})

# Medical Record Upload

@app.route('/api/medical-record/upload', methods=['POST'])
def upload_medical_record():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "没有文件"}), 400
    
    file = request.files['file']
    user_id = request.form.get('userId')
    
    if not user_id:
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400
    
    # 验证文件
    is_valid, error_message = validate_file_upload(file)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400
    
    # 使用文件处理器保存文件
    file_info = file_handler.save_file(file, user_id)
    
    # 保存记录到数据库
    medical_records_collection.insert_one({
        "userId": user_id,
        "fileUrl": file_info["fileUrl"],
        "fileName": file_info["originalName"],
        "storedFileName": file_info["fileName"],
        "fileSize": file_info["fileSize"],
        "uploadedAt": datetime.now()
    })
    
    return jsonify({"success": True, "fileUrl": file_info["fileUrl"]})

@app.route('/api/user/medical-records', methods=['GET'])
def get_medical_records():
    user_id = request.args.get('userId')
    
    # Get all user medical records
    records = list(medical_records_collection.find(
        {"userId": user_id},
        {"_id": 0, "userId": 0}
    ))
    
    # Format records
    formatted_records = []
    for record in records:
        formatted_records.append({
            "recordId": str(record.get("_id")),
            "date": record.get("uploadedAt").strftime("%Y-%m-%d"),
            "summary": "病历文件",
            "fileUrl": record.get("fileUrl")
        })
    
    return jsonify({"success": True, "records": formatted_records})

# 新增接口: 获取可选症状列表
@app.route('/api/symptoms/list', methods=['GET'])
def get_symptoms_list():
    """获取可选的症状列表"""
    symptoms = [
        # 第一页 (3个) - 心脏相关症状
        {"key": "chestPain", "label": "胸痛或胸闷", "emoji": "💔"},
        {"key": "dyspnea", "label": "呼吸急促", "emoji": "😮‍💨"},
        {"key": "arrhythmia", "label": "心律不齐", "emoji": "💗"},
        
        # 第二页 (4个) - 身体感觉
        {"key": "fatigue", "label": "疲劳虚弱", "emoji": "😪"},
        {"key": "dizziness", "label": "头晕目眩", "emoji": "🌀"},
        {"key": "swelling", "label": "身体水肿", "emoji": "🫧"},
        {"key": "sweating", "label": "异常出汗", "emoji": "💧"},
        
        # 第三页 (3个) - 疼痛和不适
        {"key": "neckPain", "label": "颈肩背部疼痛", "emoji": "🤕"},
        {"key": "cough", "label": "持续性咳嗽", "emoji": "😷"},
        {"key": "nausea", "label": "恶心想吐", "emoji": "🤢"},
        
        # 第四页 (3个) - 其他症状
        {"key": "coldLimbs", "label": "手脚发凉", "emoji": "🧊"},
        {"key": "snoring", "label": "睡觉打鼾", "emoji": "😴"},
        {"key": "anxiety", "label": "感到焦虑", "emoji": "😰"}
    ]
    
    return jsonify({"success": True, "symptoms": symptoms})

# 新增接口: 删除医疗记录
@app.route('/api/medical-record/delete/<record_id>', methods=['DELETE'])
def delete_medical_record(record_id):
    """删除指定的医疗记录"""
    try:
        # 查找记录
        record = medical_records_collection.find_one({"_id": ObjectId(record_id)})
        
        if not record:
            return jsonify({"success": False, "message": "记录不存在"}), 404
        
        # 删除文件
        if "storedFileName" in record:
            file_handler.delete_file(record["storedFileName"])
        
        # 删除数据库记录
        medical_records_collection.delete_one({"_id": ObjectId(record_id)})
        
        return jsonify({"success": True, "message": "记录已删除"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"删除失败: {str(e)}"}), 500

# 新增接口: 获取用户资料
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """获取用户基本资料"""
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400
    
    # 查询用户
    user = users_collection.find_one(
        {"userId": user_id},
        {"_id": 0, "basicInfo": 1, "lifestyle": 1, "symptoms": 1, "hasSymptoms": 1, "createdAt": 1}
    )
    
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
    
    # 如果用户有症状数据，丰富症状信息（添加emoji和label）
    if user.get("symptoms") and isinstance(user["symptoms"], list):
        # 获取症状列表的完整信息
        symptoms_list = [
            {"key": "chestPain", "label": "胸痛或胸闷", "emoji": "💔"},
            {"key": "dyspnea", "label": "呼吸急促", "emoji": "😮‍💨"},
            {"key": "arrhythmia", "label": "心律不齐", "emoji": "💗"},
            {"key": "fatigue", "label": "疲劳虚弱", "emoji": "😪"},
            {"key": "dizziness", "label": "头晕目眩", "emoji": "🌀"},
            {"key": "swelling", "label": "身体水肿", "emoji": "🫧"},
            {"key": "sweating", "label": "异常出汗", "emoji": "💧"},
            {"key": "neckPain", "label": "颈肩背部疼痛", "emoji": "🤕"},
            {"key": "cough", "label": "持续性咳嗽", "emoji": "😷"},
            {"key": "nausea", "label": "恶心想吐", "emoji": "🤢"},
            {"key": "coldLimbs", "label": "手脚发凉", "emoji": "🧊"},
            {"key": "snoring", "label": "睡觉打鼾", "emoji": "😴"},
            {"key": "anxiety", "label": "感到焦虑", "emoji": "😰"}
        ]
        
        # 创建一个查找表，以便通过key快速查找症状信息
        symptoms_map = {symptom["key"]: symptom for symptom in symptoms_list}
        
        # 丰富用户的症状数据
        enriched_symptoms = []
        for symptom in user["symptoms"]:
            symptom_key = symptom.get("key")
            if symptom_key in symptoms_map:
                # 添加emoji和label
                enriched_symptom = {
                    "key": symptom_key,
                    "emoji": symptoms_map[symptom_key]["emoji"],
                    "label": symptoms_map[symptom_key]["label"]
                }
                enriched_symptoms.append(enriched_symptom)
        
        # 用丰富后的症状数据替换原始数据
        user["symptoms"] = enriched_symptoms
    
    return jsonify({"success": True, "profile": user})

# 新增接口: 提供上传的文件访问
@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    """提供上传文件的访问"""
    return send_from_directory(config.UPLOAD_FOLDER, filename)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "database": "connected" if client.server_info() else "disconnected"
    })

# 原始的Hello World路由
@app.route('/', methods=['GET'])
def hello_world():
    return "Hello, World!"

from stroke_model import convert_user_data_to_model_format, predict_stroke_risk, determine_risk_level

# Helper function to calculate risk
def calculate_risk(user_id):
    print(f"开始为用户 {user_id} 计算风险...")
    
    # Get user data
    user = users_collection.find_one({"userId": user_id})
    if not user:
        print(f"用户 {user_id} 不存在，无法计算风险")
        return
    
    try:
        # 使用新的机器学习模型进行预测
        # 1. 将用户数据转换为模型所需的格式
        print(f"将用户数据转换为模型格式...")
        model_input_df = convert_user_data_to_model_format(user)
        print(f"模型输入数据形状: {model_input_df.shape}, 列名: {model_input_df.columns.tolist()}")
        
        # 2. 使用模型进行预测
        print(f"使用模型进行预测...")
        risk_probabilities = predict_stroke_risk(model_input_df)
        
        if risk_probabilities is None or len(risk_probabilities) == 0:
            # 如果模型预测失败，回退到简单计算器
            print(f"模型预测返回空结果，回退到简单计算器...")
            calculator = RiskCalculator(user)
            risk_result = calculator.calculate()
            
            # 检查是否有症状，并调整风险值
            if user.get("hasSymptoms") == "有" and user.get("symptoms"):
                symptom_count = len(user.get("symptoms", []))
                
                # 计算高风险症状数量
                high_risk_symptoms = ["chestPain", "dizziness", "dyspnea", "arrhythmia", "neckPain"]
                high_risk_symptom_count = sum(1 for symptom in user.get("symptoms", []) 
                                             if symptom.get("key") in high_risk_symptoms)
                
                print(f"使用简单计算器时考虑症状影响: 总症状数 {symptom_count}, 高风险症状数 {high_risk_symptom_count}")
                
                # 调整风险百分比
                symptom_factor = 2 * symptom_count  # 每个症状增加2%
                high_risk_factor = 3 * high_risk_symptom_count  # 每个高风险症状额外增加3%
                
                adjusted_risk = min(risk_result["riskPercent"] + symptom_factor + high_risk_factor, 100)
                risk_result["riskPercent"] = adjusted_risk
                risk_result["details"]["symptomAdjustment"] = symptom_factor + high_risk_factor
                
                # 根据调整后的风险重新确定风险级别
                if adjusted_risk >= 60:
                    risk_result["riskLevel"] = "高风险"
                    risk_result["riskDescription"] = "您的脑卒中风险较高"
                    risk_result["riskAdvice"] = "建议立即就医，进行专业检查和评估。"
                elif adjusted_risk >= 30:
                    risk_result["riskLevel"] = "中风险"
                    risk_result["riskDescription"] = "您的脑卒中风险中等"
                    risk_result["riskAdvice"] = "建议近期咨询医生，检查相关指标，改善生活习惯，增加体育锻炼，控制体重。"
                
                print(f"调整后的风险百分比: {adjusted_risk}%")
        else:
            # 3. 根据预测概率确定风险级别
            risk_probability = risk_probabilities[0]  # 获取第一个用户的预测结果
            print(f"模型预测风险概率: {risk_probability}")
            risk_result = determine_risk_level(risk_probability)
        
        # Update report with calculated risk
        print(f"更新报告状态为已完成...")
        update_result = reports_collection.update_one(
            {"userId": user_id, "status": "processing"},
            {"$set": {
                "status": "finished",
                "progress": 100,
                "riskPercent": risk_result["riskPercent"],
                "riskLevel": risk_result["riskLevel"],
                "riskDescription": risk_result["riskDescription"],
                "riskAdvice": risk_result["riskAdvice"],
                "details": risk_result["details"],
                "completedAt": datetime.now()
            }}
        )
        
        print(f"报告更新结果: matched={update_result.matched_count}, modified={update_result.modified_count}")
        
        # 检查更新是否成功
        if update_result.matched_count == 0:
            print(f"警告: 未找到用户 {user_id} 的进行中报告记录")
            # 创建一个新的报告
            reports_collection.insert_one({
                "userId": user_id,
                "status": "finished",
                "progress": 100,
                "riskPercent": risk_result["riskPercent"],
                "riskLevel": risk_result["riskLevel"],
                "riskDescription": risk_result["riskDescription"],
                "riskAdvice": risk_result["riskAdvice"],
                "details": risk_result["details"],
                "createdAt": datetime.now(),
                "completedAt": datetime.now()
            })
            print(f"已创建新的报告记录")
    except Exception as e:
        print(f"模型预测失败: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        
        # 如果模型预测失败，回退到简单计算器
        calculator = RiskCalculator(user)
        risk_result = calculator.calculate()
        
        # Update report with calculated risk from simple calculator
        try:
            update_result = reports_collection.update_one(
                {"userId": user_id, "status": "processing"},
                {"$set": {
                    "status": "finished",
                    "progress": 100,
                    "riskPercent": risk_result["riskPercent"],
                    "riskLevel": risk_result["riskLevel"],
                    "riskDescription": risk_result["riskDescription"],
                    "riskAdvice": risk_result["riskAdvice"],
                    "details": risk_result["details"],
                    "completedAt": datetime.now()
                }}
            )
            
            print(f"异常情况下报告更新结果: matched={update_result.matched_count}, modified={update_result.modified_count}")
            
            # 检查更新是否成功
            if update_result.matched_count == 0:
                print(f"警告: 异常情况下未找到用户 {user_id} 的进行中报告记录")
                # 创建一个新的报告
                reports_collection.insert_one({
                    "userId": user_id,
                    "status": "finished",
                    "progress": 100,
                    "riskPercent": risk_result["riskPercent"],
                    "riskLevel": risk_result["riskLevel"],
                    "riskDescription": risk_result["riskDescription"],
                    "riskAdvice": risk_result["riskAdvice"],
                    "details": risk_result["details"],
                    "createdAt": datetime.now(),
                    "completedAt": datetime.now()
                })
                print(f"异常情况下已创建新的报告记录")
        except Exception as inner_e:
            print(f"更新报告时发生错误: {str(inner_e)}")
            traceback.print_exc()  # 打印完整的错误堆栈

# 新增接口: 启动图像检测
@app.route('/api/detect/image', methods=['POST'])
def start_image_detection():
    """启动MRI或CT图像检测"""
    data = request.json
    
    # 验证必要参数
    if not data or not data.get('userId'):
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400
    
    user_id = data.get('userId')
    image_type = data.get('imageType')
    file_id = data.get('fileId')
    
    # 验证图像类型
    if image_type not in ['MRI', 'CT']:
        return jsonify({"success": False, "message": "图像类型必须是'MRI'或'CT'"}), 400
    
    # 验证文件ID
    if not file_id:
        return jsonify({"success": False, "message": "文件ID不能为空"}), 400
    
    # 查找对应的文件记录
    file_record = medical_records_collection.find_one({"_id": ObjectId(file_id)})
    
    if not file_record:
        return jsonify({"success": False, "message": "找不到对应的文件记录"}), 404
    
    # 创建检测任务
    reports_collection.insert_one({
        "userId": user_id,
        "status": "processing",
        "progress": 0,
        "imageType": image_type,
        "fileId": file_id,
        "fileName": file_record.get("fileName", ""),
        "fileUrl": file_record.get("fileUrl", ""),
        "createdAt": datetime.now()
    })
    
    # 在后台线程中执行图像风险计算
    import threading
    thread = threading.Thread(target=process_image_detection, args=(user_id, image_type, file_id))
    thread.daemon = True
    thread.start()
    
    print(f"用户 {user_id} 的{image_type}图像检测已启动，处理在后台线程中进行")
    return jsonify({"success": True, "message": f"{image_type}检测已启动"})

# 辅助函数: 处理图像检测
def process_image_detection(user_id, image_type, file_id):
    """处理图像检测并生成报告"""
    print(f"开始为用户 {user_id} 处理{image_type}图像检测...")
    
    try:
        # 获取文件记录
        file_record = medical_records_collection.find_one({"_id": ObjectId(file_id)})
        if not file_record:
            print(f"错误: 找不到文件ID为 {file_id} 的记录")
            update_image_detection_status(user_id, file_id, "failed", "找不到文件记录")
            return
        
        # 获取文件路径
        file_path = os.path.join(config.UPLOAD_FOLDER, file_record.get("storedFileName", ""))
        if not os.path.exists(file_path):
            print(f"错误: 文件 {file_path} 不存在")
            update_image_detection_status(user_id, file_id, "failed", "文件不存在")
            return
        
        # 更新进度
        update_image_detection_progress(user_id, file_id, 20, "正在分析图像...")
        
        # 导入模型分析模块
        try:
            from brain_image_analyzer import analyze_brain_image
            
            # 更新进度
            update_image_detection_progress(user_id, file_id, 50, "正在进行AI分析...")
            
            # 执行图像分析
            analysis_result = analyze_brain_image(file_path, modality=image_type)
            
            # 检查分析是否成功
            if "error" in analysis_result:
                print(f"图像分析失败: {analysis_result['error']}")
                update_image_detection_status(user_id, file_id, "failed", f"图像分析失败: {analysis_result['error']}")
                return
            
            # 更新进度
            update_image_detection_progress(user_id, file_id, 80, "生成分析报告...")
            
            # 获取预测结果
            prediction = analysis_result["prediction"]
            predicted_class = prediction["class"]
            confidence = prediction["confidence"]
            
            # 构建风险评估结果
            risk_result = {
                "riskPercent": round(confidence * 100, 2),
                "riskLevel": "高风险" if predicted_class in ["缺血性卒中", "出血性卒中"] else "低风险",
                "riskDescription": f"AI诊断结果为{predicted_class}",
                "riskAdvice": "建议立即就医" if predicted_class in ["缺血性卒中", "出血性卒中"] else "建议定期复查",
                "details": {
                    "modelScore": confidence,
                    "predictedClass": predicted_class,
                    "imageType": image_type,
                    "probabilities": prediction["probabilities"]
                },
                "analysis": analysis_result
            }
            
            # 更新报告状态为完成
            update_image_detection_status(user_id, file_id, "finished", risk_result)
            print(f"用户 {user_id} 的{image_type}图像分析已完成")
        except ImportError as e:
            print(f"导入模型分析模块失败: {str(e)}")
            update_image_detection_status(user_id, file_id, "failed", f"导入模型分析模块失败: {str(e)}")
            return
        
    except Exception as e:
        print(f"处理{image_type}图像时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        update_image_detection_status(user_id, file_id, "failed", f"处理失败: {str(e)}")

# 辅助函数: 更新图像检测进度
def update_image_detection_progress(user_id, file_id, progress, message=""):
    """更新图像检测进度"""
    try:
        reports_collection.update_one(
            {
                "userId": user_id,
                "fileId": file_id,
                "status": "processing"
            },
            {"$set": {
                "progress": progress,
                "progressMessage": message
            }}
        )
    except Exception as e:
        print(f"更新进度时发生错误: {str(e)}")

# 辅助函数: 更新图像检测状态
def update_image_detection_status(user_id, file_id, status, result):
    """更新图像检测状态"""
    try:
        update_data = {
            "status": status,
            "progress": 100 if status == "finished" else 0,
            "completedAt": datetime.now()
        }
        
        if status == "finished" and isinstance(result, dict):
            # 如果结果是风险评估结果字典
            update_data.update({
                "riskPercent": result.get("riskPercent", 0),
                "riskLevel": result.get("riskLevel", "未知"),
                "riskDescription": result.get("riskDescription", ""),
                "riskAdvice": result.get("riskAdvice", ""),
                "details": result.get("details", {})
            })
            
            # 如果是分析结果，添加额外的分析数据
            if "analysis" in result:
                update_data.update({
                    "analysisCompleted": True,
                    "prediction": result["analysis"].get("prediction", {}),
                    "visualization_url": result["analysis"].get("visualization_path", "").replace(config.UPLOAD_FOLDER, "/uploads"),
                    "report_url": result["analysis"].get("report_path", "").replace(config.UPLOAD_FOLDER, "/uploads")
                })
        elif status == "failed" and isinstance(result, str):
            # 如果结果是错误消息
            update_data["errorMessage"] = result
        
        reports_collection.update_one(
            {
                "userId": user_id,
                "fileId": file_id
            },
            {"$set": update_data}
        )
    except Exception as e:
        print(f"更新状态时发生错误: {str(e)}")

# 新增接口: 上传MRI或CT图像
@app.route('/api/medical-image/upload', methods=['POST'])
def upload_medical_image():
    """上传MRI或CT图像文件"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "没有文件"}), 400
    
    file = request.files['file']
    user_id = request.form.get('userId')
    image_type = request.form.get('imageType')
    
    # 验证必要参数
    if not user_id:
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400
    
    if not image_type or image_type not in ['MRI', 'CT']:
        return jsonify({"success": False, "message": "图像类型必须是'MRI'或'CT'"}), 400
    
    # 验证文件
    is_valid, error_message = validate_image_file(file, image_type)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400
    
    # 使用文件处理器保存文件
    file_info = file_handler.save_medical_image(file, user_id, image_type)
    
    # 保存记录到数据库
    file_id = medical_records_collection.insert_one({
        "userId": user_id,
        "fileUrl": file_info["fileUrl"],
        "fileName": file_info["originalName"],
        "storedFileName": file_info["fileName"],
        "fileSize": file_info["fileSize"],
        "imageType": image_type,
        "uploadedAt": datetime.now()
    }).inserted_id
    
    return jsonify({
        "success": True, 
        "fileUrl": file_info["fileUrl"],
        "fileId": str(file_id),
        "imageType": image_type
    })

# 新增接口: 兼容前端的图像上传路径
@app.route('/api/image/upload', methods=['POST'])
def upload_image_compat():
    """兼容前端的图像上传路径，重定向到medical-image/upload接口"""
    return upload_medical_image()

# 新增接口: 兼容前端的图像检测路径
@app.route('/api/image/detect', methods=['POST'])
def detect_image_compat():
    """兼容前端的图像检测路径，重定向到detect/image接口"""
    return start_image_detection()

# 新增接口: 图像分析结果获取
@app.route('/api/image/analysis-result', methods=['GET'])
def get_image_analysis_result():
    """获取图像分析结果"""
    file_id = request.args.get('fileId')
    
    if not file_id:
        return jsonify({"success": False, "message": "文件ID不能为空"}), 400
    
    # 查找对应的报告记录
    report = reports_collection.find_one(
        {"fileId": file_id, "status": "finished", "analysisCompleted": True},
        {"_id": 0}
    )
    
    if not report:
        return jsonify({"success": False, "message": "未找到分析完成的报告"}), 404
    
    return jsonify({"success": True, "result": report})

# 新增接口: 获取用户医学图像列表
@app.route('/api/medical-image/list', methods=['GET'])
def get_medical_images():
    """获取用户的医学图像列表"""
    user_id = request.args.get('userId')
    image_type = request.args.get('imageType')  # 可选参数，用于筛选特定类型的图像
    
    if not user_id:
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400
    
    # 构建查询条件
    query = {"userId": user_id}
    if image_type and image_type in ['MRI', 'CT']:
        query["imageType"] = image_type
    
    # 查询数据库
    images = list(medical_records_collection.find(
        query,
        {"_id": 1, "fileUrl": 1, "fileName": 1, "imageType": 1, "uploadedAt": 1}
    ))
    
    # 格式化结果
    result = []
    for image in images:
        if "imageType" in image:  # 确保是医学图像记录
            result.append({
                "imageId": str(image["_id"]),
                "fileName": image.get("fileName", "未命名"),
                "fileUrl": image.get("fileUrl", ""),
                "imageType": image.get("imageType", "未知"),
                "uploadDate": image.get("uploadedAt", datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return jsonify({
        "success": True,
        "images": result
    })

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)