"""
脑部图像分析模块 - 提供CT和MRI图像的脑卒中分析
"""
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from datetime import datetime
import sys

# 添加models目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入自定义的DFDN模型
from models.dfdn import DynamicFeatureDecouplingNetwork

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'FangSong', 'Arial']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
plt.rcParams['figure.figsize'] = [12, 8]  # 设置默认图像大小
plt.rcParams['figure.dpi'] = 150  # 提高DPI

# 设置全局变量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'ctMRImodel')
RESULTS_DIR = os.path.join(BASE_DIR, 'uploads', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# 创建自定义颜色映射
colors = [(0, 0, 0.5), (0, 0, 1), (0, 0.5, 1), (0, 1, 1), (0.5, 1, 0.5), 
          (1, 1, 0), (1, 0.5, 0), (1, 0, 0), (0.5, 0, 0)]
custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors, N=256)

def preprocess_image(image_path, target_size=(256, 256)):
    """预处理图像"""
    print(f"正在处理图像: {image_path}")
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"找不到图像文件: {image_path}")
    
    try:
        # 使用PIL读取图像，更好地处理中文路径
        pil_image = Image.open(image_path).convert('L')  # 转换为灰度图
        image = np.array(pil_image)
        
        # 调整大小
        resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
        
        # 归一化
        if resized.max() > resized.min():
            normalized = (resized - resized.min()) / (resized.max() - resized.min())
        else:
            normalized = np.zeros_like(resized, dtype=np.float32)
        
        # 添加批次和通道维度
        normalized = normalized[np.newaxis, ..., np.newaxis]
        
        return normalized, image
    except Exception as e:
        print(f"读取图像时出错: {e}")
        raise ValueError(f"无法读取图像: {image_path}")

def load_model(modality='CT'):
    """加载预训练模型"""
    print(f"正在加载{modality}模型...")
    
    model = DynamicFeatureDecouplingNetwork(
        input_shape=(256, 256, 1),
        modality=modality
    )
    
    model_path = os.path.join(MODELS_DIR, f'dfdn_{modality.lower()}_model.h5')
    
    if os.path.exists(model_path):
        model.load_model(model_path)
        print(f"成功加载模型: {model_path}")
    else:
        raise FileNotFoundError(f"找不到模型文件: {model_path}")
    
    return model

def create_feature_heatmap(pathology_features, image_shape=(256, 256)):
    """从病灶特征创建热力图"""
    # 重塑特征为2D网格 - 按照文档中的方法实现
    feature_map = np.sum(pathology_features[0].reshape(-1, 16, 8), axis=-1)
    feature_map = cv2.resize(feature_map, image_shape)
    
    # 归一化热力图
    if feature_map.max() > feature_map.min():
        feature_map = (feature_map - feature_map.min()) / (feature_map.max() - feature_map.min())
    else:
        feature_map = np.zeros_like(feature_map, dtype=np.float32)
    
    return feature_map

def analyze_features(pathology_features, physiology_features):
    """分析特征向量的特性"""
    # 提取特征统计信息
    path_stats = {
        '均值': np.mean(pathology_features),
        '标准差': np.std(pathology_features),
        '最大值': np.max(pathology_features),
        '最小值': np.min(pathology_features),
        '中位数': np.median(pathology_features),
        '非零占比': np.count_nonzero(pathology_features) / pathology_features.size
    }
    
    phys_stats = {
        '均值': np.mean(physiology_features),
        '标准差': np.std(physiology_features),
        '最大值': np.max(physiology_features),
        '最小值': np.min(physiology_features),
        '中位数': np.median(physiology_features),
        '非零占比': np.count_nonzero(physiology_features) / physiology_features.size
    }
    
    # 计算特征向量的余弦相似度
    path_norm = np.linalg.norm(pathology_features)
    phys_norm = np.linalg.norm(physiology_features)
    
    if path_norm > 0 and phys_norm > 0:
        cosine_similarity = np.dot(pathology_features.flatten(), physiology_features.flatten()) / (path_norm * phys_norm)
    else:
        cosine_similarity = 0
    
    # 计算特征向量的相关系数
    correlation = np.corrcoef(pathology_features.flatten(), physiology_features.flatten())[0, 1]
    
    feature_analysis = {
        '病灶特征统计': path_stats,
        '生理特征统计': phys_stats,
        '特征相似度': {
            '余弦相似度': cosine_similarity,
            '相关系数': correlation
        }
    }
    
    return feature_analysis

def create_advanced_visualization(original_image, feature_map, probabilities, class_names, 
                                 predicted_class, confidence, feature_analysis, save_path):
    """创建高级可视化分析图"""
    # 创建一个复杂的图形布局
    fig = plt.figure(figsize=(18, 12), dpi=150)
    gs = gridspec.GridSpec(3, 3, height_ratios=[1, 1, 0.8])
    
    # 标题
    plt.suptitle(f"脑卒中AI辅助诊断分析报告 - {predicted_class}", fontsize=20, fontweight='bold')
    
    # 1. 原始图像
    ax1 = plt.subplot(gs[0, 0])
    ax1.imshow(original_image, cmap='gray')
    ax1.set_title('原始医学影像', fontsize=14)
    ax1.axis('off')
    
    # 2. 热力图
    ax2 = plt.subplot(gs[0, 1])
    ax2.imshow(original_image, cmap='gray')
    im = ax2.imshow(feature_map, cmap=custom_cmap, alpha=0.6)
    ax2.set_title('病灶特征热力图', fontsize=14)
    ax2.axis('off')
    cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label('特征强度')
    
    # 3. 热力图轮廓
    ax3 = plt.subplot(gs[0, 2])
    # 创建轮廓图
    ax3.imshow(original_image, cmap='gray')
    contour = ax3.contour(feature_map, levels=5, colors='red', alpha=0.8)
    ax3.clabel(contour, inline=True, fontsize=8)
    ax3.set_title('病灶区域轮廓图', fontsize=14)
    ax3.axis('off')
    
    # 4. 分类概率条形图
    ax4 = plt.subplot(gs[1, 0])
    bar_colors = ['green', 'blue', 'red']
    bars = ax4.bar(class_names, probabilities, color=bar_colors)
    ax4.set_ylim(0, 1.0)
    ax4.set_ylabel('概率', fontsize=12)
    ax4.set_title('分类概率分布', fontsize=14)
    
    # 添加数值标签
    for bar, prob in zip(bars, probabilities):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{prob:.4f}', ha='center', va='bottom', fontsize=10)
    
    # 突出显示预测类别
    pred_idx = class_names.index(predicted_class)
    bars[pred_idx].set_edgecolor('black')
    bars[pred_idx].set_linewidth(2)
    
    # 5. 特征统计分析
    ax5 = plt.subplot(gs[1, 1:])
    
    # 准备数据
    import pandas as pd
    feature_stats = pd.DataFrame({
        '病灶特征': [feature_analysis['病灶特征统计'][k] for k in ['均值', '标准差', '最大值', '最小值', '中位数', '非零占比']],
        '生理特征': [feature_analysis['生理特征统计'][k] for k in ['均值', '标准差', '最大值', '最小值', '中位数', '非零占比']]
    }, index=['均值', '标准差', '最大值', '最小值', '中位数', '非零占比'])
    
    # 绘制热图
    sns.heatmap(feature_stats, annot=True, cmap='coolwarm', fmt='.4f', ax=ax5)
    ax5.set_title('特征统计分析', fontsize=14)
    
    # 6. 诊断结论与置信度
    ax6 = plt.subplot(gs[2, :])
    ax6.axis('off')
    
    # 创建文本框
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    
    # 诊断结论
    conclusion_text = f"""
    诊断结论: {predicted_class}
    置信度: {confidence:.4f} ({confidence*100:.1f}%)
    
    特征相似度分析:
    • 病灶特征与生理特征余弦相似度: {feature_analysis['特征相似度']['余弦相似度']:.4f}
    • 病灶特征与生理特征相关系数: {feature_analysis['特征相似度']['相关系数']:.4f}
    
    诊断建议:
    • {'高度可能' if confidence > 0.9 else '中度可能' if confidence > 0.7 else '低度可能'}为{predicted_class}
    • {'建议进一步临床确认' if confidence < 0.9 else '诊断结果可信度高'}
    """
    
    ax6.text(0.5, 0.5, conclusion_text, transform=ax6.transAxes, fontsize=12,
            verticalalignment='center', horizontalalignment='center', bbox=props)
    
    # 保存图像
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def save_analysis_report(image_path, modality, result, feature_analysis, save_path):
    """保存分析报告为文本文件"""
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"脑卒中AI辅助诊断系统 - 分析报告\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"图像路径: {image_path}\n")
        f.write(f"使用模型: {modality}\n\n")
        
        f.write("-" * 40 + "\n")
        f.write("诊断结果\n")
        f.write("-" * 40 + "\n")
        f.write(f"分类结果: {result['class']}\n")
        f.write(f"置信度: {result['confidence']:.4f}\n\n")
        
        f.write("类别概率:\n")
        for class_name, prob in result['probabilities'].items():
            f.write(f"  {class_name}: {prob:.4f}\n")
        f.write("\n")
        
        f.write("-" * 40 + "\n")
        f.write("特征分析\n")
        f.write("-" * 40 + "\n")
        
        f.write("病灶特征统计:\n")
        for key, value in feature_analysis['病灶特征统计'].items():
            f.write(f"  {key}: {value:.6f}\n")
        f.write("\n")
        
        f.write("生理特征统计:\n")
        for key, value in feature_analysis['生理特征统计'].items():
            f.write(f"  {key}: {value:.6f}\n")
        f.write("\n")
        
        f.write("特征相似度分析:\n")
        for key, value in feature_analysis['特征相似度'].items():
            f.write(f"  {key}: {value:.6f}\n")
        f.write("\n")
        
        f.write("-" * 40 + "\n")
        f.write("诊断建议\n")
        f.write("-" * 40 + "\n")
        
        confidence = result['confidence']
        if confidence > 0.9:
            confidence_level = "高度可能"
        elif confidence > 0.7:
            confidence_level = "中度可能"
        else:
            confidence_level = "低度可能"
        
        f.write(f"• {confidence_level}为{result['class']}\n")
        f.write(f"• {'建议进一步临床确认' if confidence < 0.9 else '诊断结果可信度高'}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("注: 本报告由AI辅助诊断系统自动生成，仅供医学参考，不能替代专业医生的诊断。\n")
        f.write("=" * 80 + "\n")

def predict_and_visualize(image_path, modality='CT', output_dir=None):
    """预测图像并可视化结果"""
    if output_dir is None:
        output_dir = RESULTS_DIR
    
    # 预处理图像
    preprocessed, original_image = preprocess_image(image_path)
    
    # 加载模型
    model = load_model(modality)
    
    # 预测
    predictions = model.predict(preprocessed)
    class_names = ['正常', '缺血性卒中', '出血性卒中']
    pred_class_idx = np.argmax(predictions[0])
    confidence = predictions[0][pred_class_idx]
    predicted_class = class_names[pred_class_idx]
    
    # 提取特征
    pathology_features, physiology_features = model.extract_features(preprocessed)
    
    # 创建结果字典
    result = {
        'class': predicted_class,
        'confidence': float(confidence),
        'probabilities': {class_names[i]: float(predictions[0][i]) for i in range(len(class_names))},
        'pathology_features': pathology_features.tolist(),  # 转换为列表以便JSON序列化
        'physiology_features': physiology_features.tolist()
    }
    
    # 生成热力图
    feature_map = create_feature_heatmap(pathology_features, original_image.shape)
    
    # 分析特征
    feature_analysis = analyze_features(pathology_features, physiology_features)
    
    # 创建结果目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    base_name = os.path.basename(image_path).split('.')[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path_base = os.path.join(output_dir, f"{base_name}_{modality}_{timestamp}")
    
    # 创建高级可视化
    visualization_path = f"{save_path_base}_analysis.png"
    create_advanced_visualization(
        original_image, 
        feature_map, 
        predictions[0], 
        class_names, 
        predicted_class, 
        confidence, 
        feature_analysis,
        visualization_path
    )
    
    # 保存分析报告
    report_path = f"{save_path_base}_report.txt"
    save_analysis_report(
        image_path,
        modality,
        result,
        feature_analysis,
        report_path
    )
    
    # 打印预测结果
    print("\n------- 预测结果 -------")
    print(f"分类结果: {result['class']}")
    print(f"置信度: {result['confidence']:.4f}")
    print("\n类别概率:")
    for class_name, prob in result['probabilities'].items():
        print(f"  {class_name}: {prob:.4f}")
    
    print(f"\n详细分析结果已保存到: {visualization_path}")
    print(f"分析报告已保存到: {report_path}")
    
    # 返回结果和文件路径
    return {
        "prediction": result,
        "visualization_path": visualization_path,
        "report_path": report_path,
        "feature_analysis": feature_analysis
    }

def analyze_brain_image(image_path, modality='CT'):
    """分析脑部图像并返回结果"""
    try:
        return predict_and_visualize(image_path, modality)
    except Exception as e:
        print(f"分析图像时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "success": False
        } 