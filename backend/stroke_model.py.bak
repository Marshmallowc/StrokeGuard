"""
脑卒中风险预测模型
"""
import pandas as pd
import numpy as np
import joblib
import os

# --- 尝试导入模型库 ---
try:
    import xgboost as xgb
except ImportError:
    print("错误: XGBoost库未安装。")
    xgb = None
try:
    import lightgbm as lgb
except ImportError:
    print("错误: LightGBM库未安装。")
    lgb = None
try:
    from pytorch_tabnet.tab_model import TabNetClassifier
    import torch
except ImportError:
    print("错误: pytorch-tabnet或PyTorch未安装。")
    TabNetClassifier = None
    torch = None

# --- 定义加载路径 ---
MODEL_DIR = "saved_stroke_model" # 与接口文档保持一致的路径名称

def load_preprocessing_artifacts(model_dir):
    """加载所有预处理相关的对象和信息。"""
    bundle_path = os.path.join(model_dir, "preprocessing_bundle.joblib")
    if not os.path.exists(bundle_path):
        print(f"错误: 预处理信息包 'preprocessing_bundle.joblib' 在 '{model_dir}' 未找到！")
        return None
    try:
        preprocessing_info = joblib.load(bundle_path)
        print("预处理信息包已成功加载。")
        # 从bundle中提取各个组件
        scaler = preprocessing_info.get('scaler')
        final_feature_columns = preprocessing_info.get('final_feature_columns')
        all_categorical_cols_to_encode = preprocessing_info.get('all_categorical_cols_to_encode')
        numerical_cols_to_scale = preprocessing_info.get('numerical_cols_to_scale')
        ds1_symptom_cols = preprocessing_info.get('ds1_symptom_cols')
        filling_values = preprocessing_info.get('filling_values', {}) # 如果没有保存，则为空字典

        if not all([scaler, final_feature_columns, all_categorical_cols_to_encode, numerical_cols_to_scale, ds1_symptom_cols]):
            print("警告: 预处理信息包中缺少一个或多个关键组件！")
            # 你可以根据需要决定是否在这里返回None或抛出错误

        return scaler, final_feature_columns, all_categorical_cols_to_encode, numerical_cols_to_scale, ds1_symptom_cols, filling_values
    except Exception as e:
        print(f"加载 preprocessing_bundle.joblib 时发生错误: {e}")
        return None


def load_models(model_dir, l0_model_names_order):
    """加载所有Level 0模型和元学习器。"""
    loaded_l0_models = {}
    meta_model_loaded = None
    try:
        # 加载Level 0模型
        for model_name in l0_model_names_order:
            if model_name == "XGBoost" and xgb:
                model_path = os.path.join(model_dir, "final_xgb_model.json")
                if os.path.exists(model_path):
                    xgb_model = xgb.XGBClassifier(enable_categorical=False)
                    xgb_model.load_model(model_path)
                    # 禁用XGBoost的特征名称检查
                    if hasattr(xgb_model, 'get_booster'):
                        try:
                            xgb_model.get_booster().feature_names = None
                        except:
                            print("无法设置feature_names=None，但将继续尝试使用模型")
                    loaded_l0_models["XGBoost"] = xgb_model
                    print("XGBoost模型已加载。")
                else: print(f"警告: XGBoost模型文件 {model_path} 未找到。")
            elif model_name == "LightGBM" and lgb:
                model_path = os.path.join(model_dir, "final_lgb_model.joblib")
                if os.path.exists(model_path):
                    loaded_l0_models["LightGBM"] = joblib.load(model_path)
                    print("LightGBM模型已加载。")
                else: print(f"警告: LightGBM模型文件 {model_path} 未找到。")
            elif model_name == "TabNet" and TabNetClassifier and torch:
                model_path = os.path.join(model_dir, "final_tabnet_model.zip") # TabNet保存为zip
                if os.path.exists(model_path):
                    tab_model = TabNetClassifier()
                    tab_model.load_model(model_path)
                    loaded_l0_models["TabNet"] = tab_model
                    print("TabNet模型已加载。")
                else: print(f"警告: TabNet模型文件 {model_path} 未找到。")
        
        # 加载元学习器
        meta_model_path = os.path.join(model_dir, "final_meta_learner.joblib")
        if os.path.exists(meta_model_path):
            meta_model_loaded = joblib.load(meta_model_path)
            print("元学习器已加载。")
        else:
            print(f"错误: 元学习器文件 {meta_model_path} 未找到！")
            return None, None # 元学习器是必需的

        # 检查是否所有在l0_model_names_order中的模型都被成功加载了
        if len(loaded_l0_models) != len(l0_model_names_order):
            print("警告: 并非所有在l0_model_names_order中指定的Level 0模型都被成功加载。")
            print(f"期望模型: {l0_model_names_order}")
            print(f"实际加载的模型: {list(loaded_l0_models.keys())}")
        
        return loaded_l0_models, meta_model_loaded

    except Exception as e:
        print(f"加载模型时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def preprocess_new_data(new_data_df, 
                       scaler,
                       all_categorical_cols_to_encode,
                       numerical_cols_to_scale,
                       ds1_symptom_cols,
                       final_feature_columns,
                       filling_values):
    """
    对新的输入数据应用与训练时完全相同的预处理步骤。
    """
    print("--- 开始预处理新数据 ---")
    processed_df = new_data_df.copy()

    # 1. 标准化列名
    processed_df.columns = processed_df.columns.str.lower().str.replace(' ', '_').str.replace('&', 'and').str.replace('/', '_').str.replace('(', '').str.replace(')', '')
    print("  步骤1: 列名已标准化。")

    # 2. 确保所有期望的原始列都存在，并处理缺失值
    expected_raw_cols_set = set(all_categorical_cols_to_encode + numerical_cols_to_scale + ds1_symptom_cols +
                               ['age','gender', 'hypertension', 'heart_disease', 'ever_married',
                                'work_type', 'residence_type', 'avg_glucose_level', 'bmi',
                                'smoking_status','stroke_risk_percentage_ds1'])

    for col in expected_raw_cols_set:
        if col not in processed_df.columns:
            print(f"  警告: 新数据中缺少原始列 '{col}'. 将根据策略填充。")
            if col in ds1_symptom_cols or col == 'hypertension' or col == 'heart_disease':
                processed_df[col] = filling_values.get(f'default_{col}', 0)
            elif col == 'stroke_risk_percentage_ds1':
                processed_df[col] = filling_values.get('ds1_stroke_risk_mean_fill', 55.0)
            elif col == 'avg_glucose_level':
                 processed_df[col] = filling_values.get('ds2_avg_glucose_median_for_ds1_rows', 90.0)
            elif col == 'bmi':
                 processed_df[col] = filling_values.get('ds2_bmi_median_for_ds1_rows', 28.0)
            elif col in all_categorical_cols_to_encode:
                processed_df[col] = filling_values.get(f'default_cat_{col}', 'Unknown')
            else: # 其他数值列
                processed_df[col] = filling_values.get(f'default_num_{col}', 0.0)
    print("  步骤2: 期望列检查与初步缺失处理完成。")

    # 3. 特定列的类型转换和映射
    if 'ever_married' in processed_df.columns and processed_df['ever_married'].dtype == 'object':
        processed_df['ever_married'] = processed_df['ever_married'].map({'Yes': 1, 'No': 0}).fillna(filling_values.get('default_ever_married_fill', 0)).astype(int)
    
    for col_name in ['hypertension', 'heart_disease', 'ever_married']:
         if col_name in processed_df.columns:
            processed_df[col_name] = pd.to_numeric(processed_df[col_name], errors='coerce').fillna(filling_values.get(f'default_{col_name}', 0)).astype(int)

    for col_name in ds1_symptom_cols:
        if col_name in processed_df.columns:
            processed_df[col_name] = pd.to_numeric(processed_df[col_name], errors='coerce').fillna(filling_values.get(f'default_{col_name}', 0)).astype(int)
    
    for col_name in ['smoking_status', 'gender', 'work_type', 'residence_type'] + [col for col in all_categorical_cols_to_encode if 'group' in col or 'category' in col]:
        if col_name in processed_df.columns and processed_df[col_name].isnull().any():
            processed_df[col_name] = processed_df[col_name].fillna(filling_values.get(f'default_cat_{col_name}', 'Unknown'))
    print("  步骤3: 特定列类型转换和映射完成。")

    # 4. 特征工程
    print("  步骤4: 应用特征工程...")
    symptom_cols_present = [s_col for s_col in ds1_symptom_cols if s_col in processed_df.columns]
    processed_df['num_symptoms_ds1'] = processed_df[symptom_cols_present].sum(axis=1) if symptom_cols_present else 0

    processed_df['bmi_x_age'] = processed_df['bmi'].astype(float) * processed_df['age'].astype(float) if 'bmi' in processed_df.columns and 'age' in processed_df.columns else 0.0
    processed_df['glucose_x_hypertension'] = processed_df['avg_glucose_level'].astype(float) * processed_df['hypertension'].astype(float) if 'avg_glucose_level' in processed_df.columns and 'hypertension' in processed_df.columns else 0.0

    age_bins = [0, 18, 35, 50, 65, float('inf')]; age_labels = ['0-18', '19-35', '36-50', '51-65', '65+']
    if 'age' in processed_df.columns:
        processed_df['age_group'] = pd.cut(processed_df['age'], bins=age_bins, labels=age_labels, right=True)
        if 'Unknown' not in processed_df['age_group'].cat.categories: processed_df['age_group'] = processed_df['age_group'].cat.add_categories('Unknown')
        processed_df['age_group'] = processed_df['age_group'].fillna('Unknown')
    else: processed_df['age_group'] = 'Unknown'

    if 'bmi' in processed_df.columns:
        bmi_bins = [0, 18.5, 24.9, 29.9, 34.9, 39.9, float('inf')]; bmi_labels = ['Underweight', 'Normal', 'Overweight', 'Obese_Class1', 'Obese_Class2', 'Obese_Class3']
        processed_df['bmi_category'] = pd.cut(processed_df['bmi'], bins=bmi_bins, labels=bmi_labels, right=False)
        if 'Unknown' not in processed_df['bmi_category'].cat.categories: processed_df['bmi_category'] = processed_df['bmi_category'].cat.add_categories('Unknown')
        processed_df['bmi_category'] = processed_df['bmi_category'].fillna('Unknown')
    else: processed_df['bmi_category'] = 'Unknown'

    if 'avg_glucose_level' in processed_df.columns:
        glucose_bins = [0, 100, 126, float('inf')]; glucose_labels = ['Normal_Glucose', 'Prediabetes_Glucose', 'Diabetes_Glucose']
        processed_df['glucose_category'] = pd.cut(processed_df['avg_glucose_level'], bins=glucose_bins, labels=glucose_labels, right=False)
        if 'Unknown' not in processed_df['glucose_category'].cat.categories: processed_df['glucose_category'] = processed_df['glucose_category'].cat.add_categories('Unknown')
        processed_df['glucose_category'] = processed_df['glucose_category'].fillna('Unknown')
    else: processed_df['glucose_category'] = 'Unknown'

    if 'smoking_status' in processed_df.columns:
        processed_df['is_smoker'] = processed_df['smoking_status'].apply(lambda x: 1 if str(x) in ['smokes', 'formerly smoked'] else 0)
        processed_df['smoking_and_hypertension'] = processed_df['is_smoker'] * processed_df['hypertension'].astype(int) if 'hypertension' in processed_df.columns else 0
        if 'bmi' in processed_df.columns:
            is_bmi_high_series = processed_df['bmi'].apply(lambda x: 1 if pd.to_numeric(x, errors='coerce') >= 25 else 0)
            processed_df['bmi_high_and_smoking'] = is_bmi_high_series * processed_df['is_smoker']
        else: processed_df['bmi_high_and_smoking'] = 0
    else: processed_df['is_smoker'] = 0; processed_df['smoking_and_hypertension'] = 0; processed_df['bmi_high_and_smoking'] = 0
    print("  特征工程应用完毕。")

    # 5. 独热编码
    actual_cols_to_dummify = [col for col in all_categorical_cols_to_encode if col in processed_df.columns]
    if actual_cols_to_dummify:
        print(f"  步骤5: 将对以下列进行独热编码: {actual_cols_to_dummify}")
        processed_df = pd.get_dummies(processed_df, columns=actual_cols_to_dummify, dummy_na=False)
    else: print("  警告: 没有在当前数据中找到需要独热编码的列。")
    print("  独热编码完成。")

    # 6. 对齐特征列
    print("  步骤6: 对齐特征列...")
    if not final_feature_columns:
        raise ValueError("错误: final_feature_columns 列表为空。")
        current_cols = set(processed_df.columns)
        expected_cols = set(final_feature_columns)
        missing_cols = list(expected_cols - current_cols)
        if missing_cols:
            for c in missing_cols:
                processed_df[c] = 0 
        extra_cols = list(current_cols - expected_cols)
        if extra_cols:
            processed_df = processed_df.drop(columns=extra_cols)
        processed_df = processed_df[final_feature_columns]
    print("  特征列已对齐。")

    # 7. 缩放数值特征
    cols_to_scale_in_final_df = [col for col in numerical_cols_to_scale if col in processed_df.columns]
    if cols_to_scale_in_final_df and scaler:
        print(f"  步骤7: 将对以下数值列进行缩放: {cols_to_scale_in_final_df[:5]}...")
        processed_df[cols_to_scale_in_final_df] = scaler.transform(processed_df[cols_to_scale_in_final_df])
        print("  数值特征已缩放。")

    # 8. 转换为 float32
    print("  步骤8: 转换为float32...")
    try:
        processed_df = processed_df.astype('float32')
    except ValueError as e:
        print(f"astype('float32') 转换失败: {e}")
        for col in processed_df.columns:
            if not pd.api.types.is_numeric_dtype(processed_df[col]):
                print(f"错误转换的列 '{col}' 类型: {processed_df[col].dtype}, 值 (前5): {processed_df[col].unique()[:5]}")
        raise
    print("--- 数据预处理完成 ---")
    return processed_df


def predict_stroke_risk(new_patient_data_df):
    """
    加载保存的模型和预处理对象，对新患者数据进行预测。
    """
    print("开始加载模型和预处理对象...")
    
    # 保存原始症状数据，用于日志记录和特征工程
    symptom_cols = [
        'chest_pain', 'shortness_of_breath', 'irregular_heartbeat', 'fatigue_and_weakness', 
        'dizziness', 'swelling_edema', 'pain_in_neck_jaw_shoulder_back', 'excessive_sweating', 
        'persistent_cough', 'nausea_vomiting', 'high_blood_pressure', 'chest_discomfort_activity', 
        'cold_hands_feet', 'snoring_sleep_apnea', 'anxiety_feeling_of_doom'
    ]
    
    original_symptom_data = {}
    for col in symptom_cols:
        if col in new_patient_data_df.columns:
            original_symptom_data[col] = new_patient_data_df[col].copy()
            print(f"原始症状数据: {col} = {new_patient_data_df[col].values}")
    
    try:
        # 1. 加载预处理组件
        preprocessing_info = load_preprocessing_artifacts(MODEL_DIR)
        if preprocessing_info is None:
            print("预处理组件加载失败")
            return None
            
        scaler, final_feature_columns, all_categorical_cols_to_encode, \
        numerical_cols_to_scale, ds1_symptom_cols, filling_values = preprocessing_info
        
        # 2. 加载 Level 0 模型名称顺序
        l0_order_path = os.path.join(MODEL_DIR, "l0_model_names_order.joblib")
        if not os.path.exists(l0_order_path):
            print(f"错误: Level 0 模型顺序文件 'l0_model_names_order.joblib' 在 '{MODEL_DIR}' 未找到！")
            return None
        try:
            l0_model_names_order = joblib.load(l0_order_path)
            print(f"Level 0 模型顺序已加载: {l0_model_names_order}")
        except Exception as e:
            print(f"加载 l0_model_names_order.joblib 时发生错误: {e}")
            return None
            
        # 3. 加载模型
        loaded_l0_models, meta_model_loaded = load_models(MODEL_DIR, l0_model_names_order)
        if loaded_l0_models is None or meta_model_loaded is None:
            print("一个或多个模型未能加载，中止预测。")
            return None
        if len(loaded_l0_models) != len(l0_model_names_order):
            print("警告: 加载的Level 0模型数量与期望的顺序列表数量不符。")

    except Exception as e:
        print(f"错误：加载模型或预处理组件时发生未知错误: {e}")
        import traceback
        traceback.print_exc()
        return None

    print("\n对新数据进行预处理...")
    try:
        # 4. 添加症状特征工程
        enhanced_df = new_patient_data_df.copy()
        # 计算症状总数作为特征
        if symptom_cols:
            symptom_cols_present = [col for col in symptom_cols if col in enhanced_df.columns]
            if symptom_cols_present:
                enhanced_df['num_symptoms'] = enhanced_df[symptom_cols_present].sum(axis=1)
                print(f"添加症状总数特征: {enhanced_df['num_symptoms'].values}")
            
            # 高风险症状标记 (胸痛、呼吸急促、心律不齐)
            high_risk_symptoms = ['chest_pain', 'shortness_of_breath', 'irregular_heartbeat']
            high_risk_present = [col for col in high_risk_symptoms if col in enhanced_df.columns]
            if high_risk_present:
                enhanced_df['high_risk_symptoms'] = enhanced_df[high_risk_present].sum(axis=1)
                print(f"添加高风险症状标记: {enhanced_df['high_risk_symptoms'].values}")
                
                # 为高风险症状添加加权因子
                for col in high_risk_present:
                    if col in enhanced_df.columns:
                        enhanced_df[f"{col}_weighted"] = enhanced_df[col] * 1.5
                        print(f"添加高风险症状加权: {col}_weighted = {enhanced_df[f'{col}_weighted'].values}")
        
        # 5. 执行预处理
        X_processed_new = preprocess_new_data(
            enhanced_df, 
            scaler, 
            all_categorical_cols_to_encode,
            numerical_cols_to_scale,
            ds1_symptom_cols,
            final_feature_columns,
            filling_values
        )
        
        if X_processed_new.empty:
            print("预处理返回空DataFrame，预测中止。")
            return None
            
        print(f"预处理后新数据形状: {X_processed_new.shape}")
        if X_processed_new.shape[1] != len(final_feature_columns):
            print(f"错误: 预处理后特征数量 ({X_processed_new.shape[1]}) 与训练时 ({len(final_feature_columns)}) 不符！")
            return None

    except Exception as e:
        print(f"错误：预处理新数据时失败: {e}")
        import traceback
        traceback.print_exc()
        return None

    print("\n获取Level 0模型的预测...")
    l0_predictions_new_dict = {}
    for model_name in l0_model_names_order:
        if model_name in loaded_l0_models:
            model = loaded_l0_models[model_name]
            try:
                # 为XGBoost模型特殊处理
                if model_name == "XGBoost":
                    # 使用NumPy数组而不是DataFrame来避免特征名称检查
                    print(f"使用NumPy数组格式预测XGBoost模型")
                    l0_predictions_new_dict[model_name] = model.predict_proba(X_processed_new.values)[:, 1]
                elif model_name == "TabNet":
                    # TabNet期望NumPy数组
                    l0_predictions_new_dict[model_name] = model.predict_proba(X_processed_new.values)[:, 1]
                else:
                    # 对所有其他模型使用标准predict_proba
                    l0_predictions_new_dict[model_name] = model.predict_proba(X_processed_new)[:, 1]
                print(f"  {model_name} 预测完成。预测值: {l0_predictions_new_dict[model_name]}")
            except Exception as e:
                print(f"  {model_name} 预测失败: {str(e)}")
                import traceback
                traceback.print_exc()
                # 如果某个模型失败，尝试继续使用其他模型
                continue
        else:
            print(f"错误: 模型 '{model_name}' 未加载，无法继续预测。")
            return None

    print("\n构建元特征...")
    meta_features_new_list = [l0_predictions_new_dict[model_name] for model_name in l0_model_names_order]
    meta_features_new = np.column_stack(meta_features_new_list)
    print(f"新数据元特征形状: {meta_features_new.shape}")

    print("\n进行最终预测...")
    final_risk_proba = meta_model_loaded.predict_proba(meta_features_new)[:, 1]
    print(f"最终风险预测概率: {final_risk_proba}")
    return final_risk_proba


# 将用户数据转换为模型所需的格式
def convert_user_data_to_model_format(user_data):
    """
    将用户数据转换为模型所需的格式
    """
    # 基础信息
    basic_info = user_data.get("basicInfo", {})
    lifestyle = user_data.get("lifestyle", {})
    has_symptoms = user_data.get("hasSymptoms")
    symptoms_list = user_data.get("symptoms", [])
    
    print(f"用户基本信息: {basic_info}")
    print(f"用户生活方式: {lifestyle}")
    print(f"用户是否有症状: {has_symptoms}")
    print(f"用户症状列表: {symptoms_list}")
    
    # 创建数据字典
    data = {
        'age': [basic_info.get("age", 0)],
        'gender': [basic_info.get("gender", "Unknown")],
        'hypertension': [basic_info.get("hypertension", 0)],  # 使用用户提供的值
        'heart_disease': [basic_info.get("heartDisease", 0)],  # 使用用户提供的值
        'ever_married': ['Yes' if lifestyle.get("maritalStatus") == "有" else 'No'],
        'work_type': [map_work_type(lifestyle.get("workType", ""))],
        'residence_type': [map_residence_type(lifestyle.get("residenceType", ""))],
        'avg_glucose_level': [basic_info.get("avgGlucoseLevel", 90.0)],  # 使用用户提供的值
        'bmi': [calculate_bmi(basic_info.get("height", 0), basic_info.get("weight", 0))],
        'smoking_status': [map_smoking_status(lifestyle.get("smokingStatus", ""))],
    }
    
    # 获取用户选择的症状键列表
    symptom_keys = []
    if has_symptoms == "有" and symptoms_list:
        symptom_keys = [symptom.get("key") for symptom in symptoms_list]
    
    print(f"用户选择的症状键: {symptom_keys}")
    
    # 前端症状键到模型期望列名的映射
    symptom_mapping = {
        "chestPain": "chest_pain",
        "dyspnea": "shortness_of_breath",
        "arrhythmia": "irregular_heartbeat",
        "fatigue": "fatigue_and_weakness",
        "dizziness": "dizziness",
        "swelling": "swelling_edema",
        "neckPain": "pain_in_neck_jaw_shoulder_back",
        "sweating": "excessive_sweating",
        "cough": "persistent_cough",
        "nausea": "nausea_vomiting",
        "highBloodPressure": "high_blood_pressure",
        "chestDiscomfort": "chest_discomfort_activity", 
        "coldLimbs": "cold_hands_feet",
        "snoring": "snoring_sleep_apnea",
        "anxiety": "anxiety_feeling_of_doom"
    }
    
    # 为模型期望的每个症状列创建对应的值
    model_symptom_cols = [
        'chest_pain', 'shortness_of_breath', 'irregular_heartbeat', 'fatigue_and_weakness', 
        'dizziness', 'swelling_edema', 'pain_in_neck_jaw_shoulder_back', 'excessive_sweating', 
        'persistent_cough', 'nausea_vomiting', 'high_blood_pressure', 'chest_discomfort_activity', 
        'cold_hands_feet', 'snoring_sleep_apnea', 'anxiety_feeling_of_doom'
    ]
    
    # 为每个模型症状列添加值
    for col in model_symptom_cols:
        # 默认为0
        value = 0
        # 检查是否有对应的前端症状被选中
        for front_key, model_col in symptom_mapping.items():
            if model_col == col and front_key in symptom_keys:
                value = 1
                print(f"设置症状 {col} (前端键: {front_key}) = 1")
                break
        data[col] = [value]
    
    return pd.DataFrame(data)


# 辅助函数：映射工作类型
def map_work_type(work_type):
    mapping = {
        "个体经营": "Self-employed",
        "政府工作": "Govt_job",
        "私营企业": "Private",
        "儿童": "children",
        "无": "Never_worked",
        "其他": "Other"
    }
    return mapping.get(work_type, "Private")


# 辅助函数：映射居住类型
def map_residence_type(residence_type):
    if residence_type == "城市":
        return "Urban"
    else:
        return "Rural"


# 辅助函数：映射吸烟状态
def map_smoking_status(smoking_status):
    mapping = {
        "吸烟": "smokes",
        "从未吸烟": "never smoked",
        "曾经吸烟": "formerly smoked",
        "未知": "Unknown"
    }
    return mapping.get(smoking_status, "Unknown")


# 辅助函数：计算BMI
def calculate_bmi(height, weight):
    if height <= 0 or weight <= 0:
        return 25.0  # 默认值
    return weight / ((height / 100) ** 2)


# 辅助函数：根据风险概率确定风险级别和建议
def determine_risk_level(risk_probability):
    risk_percent = round(risk_probability * 100, 2)  # 保留两位小数
    
    if risk_percent < 30:
        return {
            "riskPercent": risk_percent,
            "riskLevel": "低风险",
            "riskDescription": "您的脑卒中风险较低",
            "riskAdvice": "建议保持健康生活方式，定期体检。",
            "details": {
                "modelScore": risk_percent
            }
        }
    elif risk_percent < 60:
        return {
            "riskPercent": risk_percent,
            "riskLevel": "中风险",
            "riskDescription": "您的脑卒中风险中等",
            "riskAdvice": "建议近期咨询医生，检查相关指标，改善生活习惯，增加体育锻炼，控制体重。",
            "details": {
                "modelScore": risk_percent
            }
        }
    else:
        return {
            "riskPercent": risk_percent,
            "riskLevel": "高风险",
            "riskDescription": "您的脑卒中风险较高",
            "riskAdvice": "建议立即就医，进行专业检查和评估。",
            "details": {
                "modelScore": risk_percent
            }
        } 