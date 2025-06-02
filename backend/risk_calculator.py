"""
脑卒中风险计算模块
"""

class RiskCalculator:
    """脑卒中风险计算器"""
    
    def __init__(self, user_data):
        """
        初始化风险计算器
        
        Args:
            user_data (dict): 用户数据，包含基本信息、生活方式和症状
        """
        self.user_data = user_data
        self.basic_info = user_data.get("basicInfo", {})
        self.lifestyle = user_data.get("lifestyle", {})
        self.symptoms = user_data.get("symptoms", [])
        
    def calculate(self):
        """
        计算风险评分和级别
        
        Returns:
            dict: 包含风险评分、级别、描述和建议的字典
        """
        # 计算各项分数
        age_score = self._calculate_age_score()
        bmi_score = self._calculate_bmi_score()
        smoking_score = self._calculate_smoking_score()
        symptom_score = self._calculate_symptom_score()
        lifestyle_score = self._calculate_lifestyle_score()
        
        # 计算总分
        total_score = age_score + bmi_score + smoking_score + symptom_score + lifestyle_score
        risk_percent = round(min(total_score, 100), 2)  # 保留两位小数
        
        # 确定风险级别
        risk_level, risk_description, risk_advice = self._determine_risk_level(risk_percent)
        
        return {
            "riskPercent": risk_percent,
            "riskLevel": risk_level,
            "riskDescription": risk_description,
            "riskAdvice": risk_advice,
            "details": {
                "ageScore": age_score,
                "bmiScore": bmi_score,
                "smokingScore": smoking_score,
                "symptomScore": symptom_score,
                "lifestyleScore": lifestyle_score
            }
        }
    
    def _calculate_age_score(self):
        """计算年龄风险分数"""
        age = self.basic_info.get("age", 0)
        
        if age < 40:
            return 0
        elif age < 50:
            return 5
        elif age < 60:
            return 8
        elif age < 70:
            return 10
        else:
            return 15
    
    def _calculate_bmi_score(self):
        """计算BMI风险分数"""
        height = self.basic_info.get("height", 0)
        weight = self.basic_info.get("weight", 0)
        
        # 计算BMI
        if height <= 0 or weight <= 0:
            return 0
            
        bmi = weight / ((height / 100) ** 2)
        
        if bmi < 18.5:
            return 3  # 偏瘦
        elif bmi < 24:
            return 0  # 正常
        elif bmi < 28:
            return 5  # 超重
        elif bmi < 32:
            return 10  # 肥胖
        else:
            return 15  # 重度肥胖
    
    def _calculate_smoking_score(self):
        """计算吸烟风险分数"""
        smoking_status = self.lifestyle.get("smokingStatus", "")
        
        if smoking_status == "吸烟":
            return 15
        elif smoking_status == "已戒烟":
            return 5
        else:
            return 0
    
    def _calculate_symptom_score(self):
        """计算症状风险分数"""
        # 检查是否有症状
        has_symptoms = self.user_data.get("hasSymptoms")
        
        # 如果明确表示无症状，返回0分
        if has_symptoms == "无":
            return 0
        
        # 如果有症状，计算分数
        if has_symptoms == "有":
            # 获取症状列表
            symptoms = self.user_data.get("symptoms", [])
            
            # 高风险症状关键词
            high_risk_symptoms = ["chestPain", "dizziness", "dyspnea", "arrhythmia", "neckPain"]
            
            # 计算有症状的数量和高风险症状数量
            symptom_count = len(symptoms)
            high_risk_count = sum(1 for symptom in symptoms if symptom.get("key") in high_risk_symptoms)
            
            # 根据症状数量和高风险症状数量计算分数
            return high_risk_count * 7 + (symptom_count - high_risk_count) * 3
        
        # 默认情况
        return 0
    
    def _calculate_lifestyle_score(self):
        """计算生活方式风险分数"""
        score = 0
        
        # 居住环境
        if self.lifestyle.get("residenceType") == "农村":
            score += 3
        
        # 工作类型
        work_type = self.lifestyle.get("workType", "")
        if work_type == "体力劳动":
            score += 2
        elif work_type == "长期久坐":
            score += 5
        
        return score
    
    def _determine_risk_level(self, risk_percent):
        """根据风险百分比确定风险级别、描述和建议"""
        if risk_percent < 30:
            return (
                "低风险",
                "您的脑卒中风险较低",
                "建议保持健康生活方式，定期体检。"
            )
        elif risk_percent < 60:
            return (
                "中风险",
                "您的脑卒中风险中等",
                "建议近期咨询医生，检查相关指标，改善生活习惯，增加体育锻炼，控制体重。"
            )
        else:
            return (
                "高风险",
                "您的脑卒中风险较高",
                "建议立即就医，进行专业检查和评估。"
            ) 