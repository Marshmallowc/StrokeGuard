import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model, optimizers
import matplotlib.pyplot as plt
from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.layers import Input, Dense, Flatten, Dropout, GlobalAveragePooling2D, LayerNormalization, MultiHeadAttention, Activation, Add, GlobalAveragePooling1D
from tqdm import tqdm

class DynamicFeatureDecouplingNetwork:
    """
    动态特征解耦网络(DFDN)
    用于分离医学影像中的病灶特征与生理噪声，基于Transformer和对比学习
    """
    
    def __init__(
        self, 
        input_shape=(256, 256, 1),
        embedding_dim=256,
        num_transformer_blocks=6,
        num_heads=8,
        mlp_units=512,
        dropout_rate=0.1,
        temperature=0.07,  # 降低温度参数
        contrastive_weight=0.01,  # 降低对比损失权重
        ortho_weight=0.01,  # 降低正交损失权重
        modality='CT'
    ):
        self.input_shape = input_shape
        self.embedding_dim = embedding_dim
        self.num_transformer_blocks = num_transformer_blocks
        self.num_heads = num_heads
        self.mlp_units = mlp_units
        self.dropout_rate = dropout_rate
        self.temperature = temperature
        self.contrastive_weight = contrastive_weight
        self.ortho_weight = ortho_weight
        self.modality = modality
        
        # 初始化模型
        self.encoder = self._build_encoder()
        self.pathology_decoder = self._build_decoder("pathology")
        self.physiology_decoder = self._build_decoder("physiology")
        self.classifier = self._build_classifier()
        
        # 创建训练模型
        self.dfdn_model = self._build_dfdn_model()
        self.contrastive_model = self._build_contrastive_model()
        
        # 初始化指标
        self.ct_accuracy = tf.keras.metrics.CategoricalAccuracy(name='ct_accuracy')
        self.mri_accuracy = tf.keras.metrics.CategoricalAccuracy(name='mri_accuracy')
        
        # 初始化损失函数
        self.ct_classification_loss = tf.keras.losses.CategoricalCrossentropy(
            label_smoothing=0.1  # 添加标签平滑
        )
        self.mri_classification_loss = tf.keras.losses.CategoricalCrossentropy(
            label_smoothing=0.1  # 添加标签平滑
        )
    
    def _build_encoder(self):
        """构建编码器，使用ResNet作为特征提取器，然后接Transformer"""
        # 输入层
        inputs = Input(shape=self.input_shape)
        
        # 使用ResNet50V2作为特征提取器的基础
        # 如果输入是单通道，复制到3通道
        if self.input_shape[-1] == 1:
            # 指定输出形状为输入的前两个维度保持不变，通道数变为3
            x = layers.Lambda(
                lambda x: tf.repeat(x, 3, axis=-1),
                output_shape=(self.input_shape[0], self.input_shape[1], 3)
            )(inputs)
        else:
            x = inputs
        
        # 使用预训练的ResNet，但去掉顶层
        base_model = ResNet50V2(
            include_top=False,
            weights='imagenet',
            input_shape=(self.input_shape[0], self.input_shape[1], 3)
        )
        # 冻结底层
        for layer in base_model.layers[:100]:
            layer.trainable = False
            
        x = base_model(x)
        
        # 将特征图转换为序列
        # 使用Keras层而不是直接调用tf函数
        reshape_layer = layers.Reshape((-1, tf.keras.backend.int_shape(x)[-1]))(x)
        sequence = reshape_layer
        
        # 获取实际特征维度以匹配Transformer
        feature_dim = tf.keras.backend.int_shape(sequence)[-1]
        
        # 调整特征维度到embedding_dim
        sequence = Dense(self.embedding_dim)(sequence)
        
        # 使用一个更简单、更直接的方法添加位置编码
        # 先提取序列长度作为常量
        seq_shape = tf.keras.backend.int_shape(sequence)
        embed_dim = seq_shape[-1]
        
        # 创建单独的位置编码层
        class PositionalEncoding(layers.Layer):
            def __init__(self, embed_dim, **kwargs):
                super(PositionalEncoding, self).__init__(**kwargs)
                self.embed_dim = embed_dim
                
            def call(self, inputs):
                # 获取输入的数据类型，用于确保类型一致性
                input_dtype = inputs.dtype
                
                seq_length = tf.shape(inputs)[1]
                # 创建位置索引 - 使用float32进行计算，降低数值误差
                positions = tf.range(start=0, limit=seq_length, delta=1, dtype=tf.float32)
                # 创建维度索引
                dimensions = tf.range(start=0, limit=self.embed_dim, delta=1, dtype=tf.float32)
                
                # 创建维度常数
                dim_mat = tf.pow(
                    10000.0,
                    (2 * (dimensions // 2)) / tf.cast(self.embed_dim, tf.float32)
                )
                
                # 创建位置矩阵
                pos_mat = tf.expand_dims(positions, -1)  # [seq_len, 1]
                dim_mat = tf.expand_dims(dim_mat, 0)     # [1, dim]
                
                # 计算角度
                angle = pos_mat / dim_mat  # [seq_len, dim]
                
                # 应用sin和cos
                pos_encoding = tf.where(
                    tf.cast(tf.range(self.embed_dim) % 2, tf.bool),
                    tf.cos(angle),   # 奇数维度
                    tf.sin(angle)    # 偶数维度
                )
                
                # 添加批次维度
                pos_encoding = tf.expand_dims(pos_encoding, 0)  # [1, seq_len, dim]
                
                # 将位置编码转换为与输入相同的数据类型
                pos_encoding = tf.cast(pos_encoding, input_dtype)
                
                # 将位置编码添加到输入中
                return inputs + pos_encoding
                
            def compute_output_shape(self, input_shape):
                return input_shape
        
        # 应用位置编码
        sequence = PositionalEncoding(embed_dim)(sequence)
        
        # Transformer编码器
        for _ in range(self.num_transformer_blocks):
            sequence = self._transformer_block(
                sequence, 
                self.embedding_dim, 
                self.num_heads, 
                self.mlp_units, 
                self.dropout_rate
            )
        
        # 输出模型
        encoder_model = Model(inputs=inputs, outputs=sequence, name="encoder")
        return encoder_model

    def _transformer_block(self, x, embed_dim, num_heads, mlp_units, dropout_rate):
        """Transformer块实现"""
        # 多头自注意力
        attention_output = MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim // num_heads
        )(x, x)
        attention_output = Dropout(dropout_rate)(attention_output)
        
        # 第一个残差连接和标准化
        x1 = Add()([x, attention_output])
        x1 = LayerNormalization(epsilon=1e-6)(x1)
        
        # 前馈神经网络
        ffn_output = Dense(mlp_units, activation='relu')(x1)
        ffn_output = Dense(embed_dim)(ffn_output)
        ffn_output = Dropout(dropout_rate)(ffn_output)
        
        # 第二个残差连接和标准化
        x2 = Add()([x1, ffn_output])
        output = LayerNormalization(epsilon=1e-6)(x2)
        
        return output
    
    def _build_decoder(self, decoder_type):
        """构建解码器（病灶特征解码器或生理特征解码器）"""
        # 输入是编码器的输出
        inputs = Input(shape=(None, self.embedding_dim))
        
        # 不同类型的解码器可以使用不同的结构
        x = inputs
        
        # Transformer解码器块
        for _ in range(3):  # 使用较少的Transformer块
            x = self._transformer_block(
                x, 
                self.embedding_dim, 
                self.num_heads, 
                self.mlp_units, 
                self.dropout_rate
            )
        
        # 使用全局平均池化直接处理序列，避免reshape
        x = GlobalAveragePooling1D()(x)
        
        # 全连接层
        x = Dense(512, activation='relu')(x)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(256, activation='relu')(x)
        
        # 不同类型的解码器有不同的目标
        if decoder_type == "pathology":
            # 病灶特征解码器
            feature_output = Dense(128, name="pathology_features")(x)
        else:
            # 生理特征解码器
            feature_output = Dense(128, name="physiology_features")(x)
        
        decoder_model = Model(inputs=inputs, outputs=feature_output, name=f"{decoder_type}_decoder")
        return decoder_model
    
    def _build_classifier(self):
        """构建分类器，用于卒中类型分类"""
        # 输入是病灶特征
        inputs = Input(shape=(128,))
        
        # 分类器网络
        x = Dense(64, activation='relu')(inputs)
        x = Dropout(self.dropout_rate)(x)
        
        # 多分类输出（正常、缺血性、出血性）
        outputs = Dense(3, activation='softmax', name="stroke_classification")(x)
        
        classifier_model = Model(inputs=inputs, outputs=outputs, name="classifier")
        return classifier_model
    
    def _build_dfdn_model(self):
        """构建完整的DFDN模型"""
        # 输入图像
        inputs = Input(shape=self.input_shape)
        
        # 编码器
        encoded_features = self.encoder(inputs)
        
        # 解耦为病灶特征和生理特征
        pathology_features = self.pathology_decoder(encoded_features)
        physiology_features = self.physiology_decoder(encoded_features)
        
        # 分类器
        classification_outputs = self.classifier(pathology_features)
        
        # 创建端到端模型
        dfdn_model = Model(
            inputs=inputs, 
            outputs=[classification_outputs, pathology_features, physiology_features],
            name="DFDN_Model"
        )
        
        return dfdn_model
    
    def _build_contrastive_model(self):
        """构建对比学习模型"""
        # 输入两张图像
        input_1 = Input(shape=self.input_shape)
        input_2 = Input(shape=self.input_shape)
        
        # 通过编码器和解码器
        encoded_1 = self.encoder(input_1)
        encoded_2 = self.encoder(input_2)
        
        pathology_1 = self.pathology_decoder(encoded_1)
        pathology_2 = self.pathology_decoder(encoded_2)
        
        physiology_1 = self.physiology_decoder(encoded_1)
        physiology_2 = self.physiology_decoder(encoded_2)
        
        # 创建对比学习模型
        contrastive_model = Model(
            inputs=[input_1, input_2], 
            outputs=[
                pathology_1, pathology_2, 
                physiology_1, physiology_2
            ],
            name="Contrastive_Model"
        )
        
        return contrastive_model
    
    def contrastive_loss(self, features_1, features_2):
        """对比损失计算 - 修改为正样本对的正确计算方式"""
        # L2归一化
        features_1_norm = tf.math.l2_normalize(features_1, axis=1)
        features_2_norm = tf.math.l2_normalize(features_2, axis=1)
        
        # 计算相似度矩阵
        similarity_matrix = tf.matmul(features_1_norm, features_2_norm, transpose_b=True) / self.temperature
        
        # 创建标签 - 对角线上的元素为正样本对
        batch_size = tf.shape(features_1)[0]
        labels = tf.eye(batch_size)  # 创建单位矩阵作为正样本对的标签
        
        # 计算对比损失
        loss = tf.reduce_mean(
            tf.keras.losses.binary_crossentropy(
                labels,
                tf.nn.sigmoid(similarity_matrix),
                from_logits=False
            )
        )
        
        return loss
        
    def orthogonality_loss(self, pathology_features, physiology_features):
        """正交损失 - 修改为计算每个样本内部特征的正交性"""
        # 获取输入的数据类型
        compute_dtype = tf.float32
        
        # 如果是混合精度环境，并且输入是float16
        if pathology_features.dtype == tf.float16:
            # 临时转换到float32进行精确计算
            p_feat = tf.cast(pathology_features, compute_dtype)
            ph_feat = tf.cast(physiology_features, compute_dtype)
            
            # L2归一化
            p_feat_norm = tf.math.l2_normalize(p_feat, axis=1)
            ph_feat_norm = tf.math.l2_normalize(ph_feat, axis=1)
            
            # 计算每个样本的点积
            dot_products = tf.reduce_sum(p_feat_norm * ph_feat_norm, axis=1)
            
            # 计算正交损失（点积的平方的均值）
            ortho_loss = tf.reduce_mean(tf.square(dot_products))
            
            # 转换回输入类型
            return tf.cast(ortho_loss, pathology_features.dtype)
        else:
            # 正常处理流程
            # L2归一化
            p_feat_norm = tf.math.l2_normalize(pathology_features, axis=1)
            ph_feat_norm = tf.math.l2_normalize(physiology_features, axis=1)
            
            # 计算每个样本的点积
            dot_products = tf.reduce_sum(p_feat_norm * ph_feat_norm, axis=1)
            
            # 计算正交损失（点积的平方的均值）
            ortho_loss = tf.reduce_mean(tf.square(dot_products))
            
            return ortho_loss
    
    def get_balanced_sample_weights(self, labels):
        """计算平衡的样本权重用于不平衡数据集"""
        # 计算每个类别的权重
        class_counts = tf.math.bincount(tf.cast(tf.argmax(labels, axis=1), tf.int32))
        # 将total_samples转换为float32，以确保除法兼容性
        total_samples = tf.cast(tf.reduce_sum(class_counts), tf.float32)
        num_classes = tf.cast(tf.shape(class_counts)[0], tf.float32)
        class_counts_float = tf.cast(class_counts, tf.float32)
        class_weights = total_samples / (num_classes * class_counts_float)
        
        # 为每个样本分配权重
        sample_weights = tf.gather(class_weights, tf.argmax(labels, axis=1))
        
        return sample_weights
    
    @tf.function
    def train_step(self, batch_data):
        """优化的训练步骤"""
        # 解包批次数据
        images, labels = batch_data
        
        # 使用单个梯度带进行所有计算
        with tf.GradientTape() as tape:
            # 前向传播
            outputs = self.dfdn_model(images, training=True)
            classification_output, pathology_features, physiology_features = outputs
            
            # 计算分类损失
            classification_loss = self.ct_classification_loss(labels, classification_output)
            
            # 计算对比损失
            contrastive_loss = self.contrastive_loss(pathology_features, physiology_features)
            
            # 计算正交损失
            ortho_loss = self.orthogonality_loss(pathology_features, physiology_features)
            
            # 计算总损失，确保所有损失使用相同的数据类型
            total_loss = classification_loss
            
            # 添加对比损失和正交损失，使用tf.clip_by_value确保数值稳定
            if not tf.math.is_nan(contrastive_loss):
                total_loss = total_loss + self.contrastive_weight * tf.clip_by_value(
                    contrastive_loss, -1e6, 1e6
                )
            
            if not tf.math.is_nan(ortho_loss):
                total_loss = total_loss + self.ortho_weight * tf.clip_by_value(
                    ortho_loss, -1e6, 1e6
                )
        
        # 计算梯度
        gradients = tape.gradient(total_loss, self.dfdn_model.trainable_variables)
        
        # 应用梯度裁剪
        gradients = [tf.clip_by_norm(g, 1.0) for g in gradients if g is not None]
        
        # 应用梯度
        self.dfdn_model.optimizer.apply_gradients(zip(gradients, self.dfdn_model.trainable_variables))
        
        # 更新指标
        self.ct_accuracy.update_state(labels, classification_output)
        
        # 返回损失和准确率
        return {
            'total_loss': total_loss,
            'classification_loss': classification_loss,
            'contrastive_loss': contrastive_loss,
            'ortho_loss': ortho_loss,
            'accuracy': self.ct_accuracy.result()
        }
    
    def compile_model(self):
        """编译模型，支持混合精度训练和XLA加速"""
        # 创建优化器，使用更保守的学习率
        optimizer = optimizers.Adam(
            learning_rate=0.0001,  # 降低学习率
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-07
        )
        
        # 检查是否使用了混合精度
        if tf.keras.mixed_precision.global_policy().name == 'mixed_float16':
            print("使用混合精度训练 (mixed_float16)")
            # 使用损失缩放以避免数值下溢
            optimizer = tf.keras.mixed_precision.LossScaleOptimizer(optimizer)
            
        # 启用XLA JIT编译加速
        tf.config.optimizer.set_jit(True)
        print("已启用XLA JIT编译加速")
        
        # 主模型编译
        self.dfdn_model.compile(
            optimizer=optimizer,
            loss={
                "stroke_classification": "categorical_crossentropy",
                "pathology_features": lambda y_true, y_pred: 0.0,  # 占位符
                "physiology_features": lambda y_true, y_pred: 0.0   # 占位符
            },
            loss_weights={
                "stroke_classification": 1.0,
                "pathology_features": 0.0,
                "physiology_features": 0.0
            },
            metrics={
                "stroke_classification": ["accuracy"]
            },
            # 提升准确率计算性能
            run_eagerly=False
        )
        
        # 预先缓存性能关键函数
        self._cached_ce_loss = tf.keras.losses.CategoricalCrossentropy(
            from_logits=False, 
            reduction=tf.keras.losses.Reduction.NONE,
            label_smoothing=0.1  # 添加标签平滑
        )
    
    def train(self, 
             train_data, 
             validation_data=None,
             epochs=50,
             batch_size=128,  # 增大批处理大小以提高GPU利用率
             early_stopping_patience=10,
             model_save_path=None):
        """
        训练模型
        
        参数:
        train_data: 元组 (x_train, y_train)
        validation_data: 元组 (x_val, y_val) 或 None
        epochs: 训练轮数
        batch_size: 批次大小
        early_stopping_patience: 早停耐心值
        model_save_path: 模型保存路径
        """
        # 编译模型
        self.compile_model()
        
        # 准备数据
        x_train, y_train = train_data
        if validation_data:
            x_val, y_val = validation_data
            
        # 创建优化的数据集
        print(f"创建优化的数据管道，批处理大小: {batch_size}")
        train_dataset = self.create_optimized_dataset(x_train, y_train, batch_size, is_training=True)
        if validation_data:
            val_dataset = self.create_optimized_dataset(x_val, y_val, batch_size, is_training=False)
            
        # 计算步数
        steps_per_epoch = len(x_train) // batch_size
        if len(x_train) % batch_size != 0:
            steps_per_epoch += 1
            
        validation_steps = None
        if validation_data:
            validation_steps = len(x_val) // batch_size
            if len(x_val) % batch_size != 0:
                validation_steps += 1
                
        # 使用优化的数据集API训练
        return self.train_with_datasets(
            train_dataset, 
            val_dataset if validation_data else None,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
            validation_steps=validation_steps,
            early_stopping_patience=early_stopping_patience,
            model_save_path=model_save_path
        )
        
        # 训练历史记录
        history = {
            "total_loss": [],
            "classification_loss": [],
            "contrastive_loss": [],
            "pathology_contrastive_loss": [],
            "physiology_contrastive_loss": [],
            "orthogonality_loss": [],
            "val_accuracy": [] if validation_data else None
        }
        
        # 早停设置
        best_val_accuracy = 0
        patience_counter = 0
        
        # 训练循环
        for epoch in range(epochs):
            print(f"Epoch {epoch+1}/{epochs}")
            
            # 打乱训练数据
            indices = np.random.permutation(len(x_train))
            x_train_shuffled = x_train[indices]
            y_train_shuffled = y_train[indices]
            sample_weights_shuffled = sample_weights.numpy()[indices] if sample_weights is not None else None
            
            # 批次训练
            epoch_losses = {k: [] for k in history.keys() if k != "val_accuracy"}
            n_batches = int(np.ceil(len(x_train) / batch_size))
            
            for batch in range(n_batches):
                start_idx = batch * batch_size
                end_idx = min((batch + 1) * batch_size, len(x_train))
                
                x_batch = x_train_shuffled[start_idx:end_idx]
                y_batch = y_train_shuffled[start_idx:end_idx]
                sw_batch = sample_weights_shuffled[start_idx:end_idx] if sample_weights_shuffled is not None else None
                
                # 执行一步训练
                batch_losses = self.custom_train_step(x_batch, y_batch, sw_batch)
                
                # 记录损失
                for k, v in batch_losses.items():
                    if k in epoch_losses:
                        epoch_losses[k].append(v.numpy())
                
                # 打印进度
                if (batch + 1) % 10 == 0:
                    print(f"  Batch {batch+1}/{n_batches}, Loss: {batch_losses['total_loss']:.4f}")
            
            # 计算并存储本轮的平均损失
            for k, v in epoch_losses.items():
                avg_loss = np.mean(v)
                history[k].append(avg_loss)
                print(f"  {k}: {avg_loss:.4f}")
            
            # 验证评估
            if validation_data:
                # 预测验证集
                val_preds = self.dfdn_model.predict(x_val)[0]
                val_accuracy = np.mean(np.argmax(val_preds, axis=1) == np.argmax(y_val, axis=1))
                history["val_accuracy"].append(val_accuracy)
                print(f"  val_accuracy: {val_accuracy:.4f}")
                
                # 早停检查
                if val_accuracy > best_val_accuracy:
                    best_val_accuracy = val_accuracy
                    patience_counter = 0
                    # 保存最佳模型
                    if model_save_path:
                        self.dfdn_model.save_weights(model_save_path)
                        print(f"  Model saved to {model_save_path}")
                else:
                    patience_counter += 1
                    if patience_counter >= early_stopping_patience:
                        print(f"Early stopping triggered after {epoch+1} epochs")
                        break
        
        # 如果使用了早停且保存了模型，加载最佳模型
        if validation_data and model_save_path and os.path.exists(model_save_path):
            self.dfdn_model.load_weights(model_save_path)
        
        return history
    
    def train_with_datasets(self, 
                           train_dataset, 
                           validation_dataset=None,
                           epochs=50,
                           steps_per_epoch=None,
                           validation_steps=None,
                           early_stopping_patience=10,
                           model_save_path=None):
        """
        使用TensorFlow数据集API训练模型，支持混合精度训练
        """
        # 编译模型
        self.compile_model()
        
        # 配置GPU内存增长以最大化性能
        try:
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    # 允许GPU内存增长
                    tf.config.experimental.set_memory_growth(gpu, True)
                print(f"已为GPU优化内存配置")
        except Exception as e:
            print(f"GPU配置异常: {e}")
            # 继续执行，即使GPU配置失败
        
        # 训练历史记录 - 只跟踪实际使用的指标
        history = {
            "total_loss": [],
            "classification_loss": [],
            "contrastive_loss": [],
            "val_accuracy": [] if validation_dataset else None
        }
        
        # 早停设置
        best_val_accuracy = 0
        patience_counter = 0
        
        # 训练循环
        for epoch in range(epochs):
            print(f"Epoch {epoch+1}/{epochs}")
            
            # 重置度量
            epoch_losses = {k: [] for k in history.keys() if k != "val_accuracy"}
            
            # 创建进度条
            progress_bar = tqdm(total=steps_per_epoch, desc=f"Training")
            
            # 训练一个epoch
            for step, batch_data in enumerate(train_dataset):
                if step >= steps_per_epoch:
                    break
                
                # 解包批次数据
                if len(batch_data) == 3:  # 包含样本权重
                    x_batch, y_batch, sample_weights = batch_data
                else:  # 不包含样本权重
                    x_batch, y_batch = batch_data
                    sample_weights = None
                
                # 执行一步训练
                batch_losses = self.train_step((x_batch, y_batch))
                
                # 记录损失 - 只记录实际使用的指标
                for k in epoch_losses.keys():
                    if k in batch_losses:
                        epoch_losses[k].append(batch_losses[k].numpy())
                
                # 更新进度条
                progress_bar.update(1)
                progress_bar.set_postfix({"loss": float(batch_losses['total_loss'])})
            
            progress_bar.close()
            
            # 计算并存储本轮的平均损失
            for k, v in epoch_losses.items():
                if v:  # 确保列表不为空
                    avg_loss = np.mean(v)
                    history[k].append(avg_loss)
                    print(f"  {k}: {avg_loss:.4f}")
            
            # 验证评估
            if validation_dataset:
                # 重置验证指标
                val_correct = 0
                val_total = 0
                
                # 创建验证进度条
                val_progress = tqdm(total=validation_steps, desc="Validation")
                
                # 验证
                for step, batch_data in enumerate(validation_dataset):
                    if step >= validation_steps:
                        break
                    
                    # 解包批次数据
                    if len(batch_data) == 3:  # 包含样本权重
                        x_val_batch, y_val_batch, _ = batch_data
                    else:  # 不包含样本权重
                        x_val_batch, y_val_batch = batch_data
                    
                    # 预测验证batch
                    val_preds = self.dfdn_model(x_val_batch, training=False)[0]
                    
                    # 计算准确率
                    val_correct_batch = tf.reduce_sum(
                        tf.cast(
                            tf.equal(
                                tf.argmax(val_preds, axis=1),
                                tf.argmax(y_val_batch, axis=1)
                            ),
                            tf.float32
                        )
                    )
                    val_correct += val_correct_batch
                    val_total += tf.shape(x_val_batch)[0]
                    
                    # 更新进度条
                    val_progress.update(1)
                
                val_progress.close()
                
                # 计算验证准确率
                val_accuracy = val_correct / tf.cast(val_total, tf.float32)
                history["val_accuracy"].append(val_accuracy.numpy())
                print(f"  val_accuracy: {val_accuracy:.4f}")
                
                # 早停检查
                if val_accuracy > best_val_accuracy:
                    best_val_accuracy = val_accuracy
                    patience_counter = 0
                    # 保存最佳模型
                    if model_save_path:
                        self.dfdn_model.save_weights(model_save_path)
                        print(f"  Model saved to {model_save_path}")
                else:
                    patience_counter += 1
                    if patience_counter >= early_stopping_patience:
                        print(f"Early stopping triggered after {epoch+1} epochs")
                        break
        
        # 如果使用了早停且保存了模型，加载最佳模型
        if validation_dataset and model_save_path and os.path.exists(model_save_path):
            self.dfdn_model.load_weights(model_save_path)
        
        return history
    
    def visualize_features(self, x_batch, y_batch, save_path=None):
        """可视化病灶特征和生理特征"""
        # 获取特征
        _, pathology_features, physiology_features = self.dfdn_model.predict(x_batch)
        
        # 使用t-SNE降维
        from sklearn.manifold import TSNE
        tsne = TSNE(n_components=2, random_state=42)
        
        # 拼接特征以便进行t-SNE
        combined_features = np.concatenate([
            pathology_features, 
            physiology_features
        ], axis=0)
        
        # 特征类型标签
        feature_types = np.array(['Pathology'] * len(pathology_features) + 
                               ['Physiology'] * len(physiology_features))
        
        # 类别标签（重复两次，因为有两种特征）
        class_labels = np.argmax(y_batch, axis=1)
        class_names = ['Normal', 'Ischemic', 'Hemorrhagic']
        class_labels_str = np.array([class_names[i] for i in class_labels])
        class_labels_str = np.concatenate([class_labels_str, class_labels_str])
        
        # 应用t-SNE
        embedded_features = tsne.fit_transform(combined_features)
        
        # 可视化
        plt.figure(figsize=(12, 10))
        
        # 为不同类型和类别创建不同的标记和颜色
        markers = {'Pathology': 'o', 'Physiology': 'x'}
        colors = {'Normal': 'green', 'Ischemic': 'blue', 'Hemorrhagic': 'red'}
        
        for feature_type in np.unique(feature_types):
            for class_name in np.unique(class_labels_str):
                # 选择当前组合的数据点
                mask = (feature_types == feature_type) & (class_labels_str == class_name)
                plt.scatter(
                    embedded_features[mask, 0], 
                    embedded_features[mask, 1],
                    marker=markers[feature_type],
                    c=colors[class_name],
                    alpha=0.7,
                    label=f"{feature_type}-{class_name}"
                )
        
        plt.legend()
        plt.title(f'{self.modality} Dynamic Feature Decoupling Visualization')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Visualization saved to {save_path}")
        
        plt.show()
    
    def predict(self, x):
        """模型预测"""
        classification_output, _, _ = self.dfdn_model.predict(x)
        return classification_output
    
    def create_optimized_dataset(self, x_data, y_data, batch_size, is_training=True):
        """创建高效的TensorFlow数据管道以提高GPU利用率
        
        参数:
        x_data: 输入数据
        y_data: 标签数据
        batch_size: 批处理大小
        is_training: 是否用于训练
        
        返回:
        优化的tf.data.Dataset对象
        """
        # 计算平衡样本权重（如果是训练集）
        if is_training:
            sample_weights = self.get_balanced_sample_weights(y_data)
            # 创建包含样本权重的数据集
            dataset = tf.data.Dataset.from_tensor_slices((x_data, y_data, sample_weights))
            dataset = dataset.shuffle(buffer_size=len(x_data), reshuffle_each_iteration=True)
        else:
            dataset = tf.data.Dataset.from_tensor_slices((x_data, y_data))
        
        # 配置数据集性能优化
        dataset = dataset.batch(batch_size, drop_remainder=is_training)
        
        # 使用并行处理器数量进行并行处理
        dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)
        
        # 启用缓存来减少CPU-GPU数据传输瓶颈
        if not is_training:  # 验证集可以完全缓存
            dataset = dataset.cache()
        
        # 如果GPU内存充足，可以考虑设置更大的预取值
        dataset = dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
        
        return dataset
    
    def extract_features(self, x):
        """提取特征用于下游任务"""
        _, pathology_features, physiology_features = self.dfdn_model.predict(x)
        return pathology_features, physiology_features
    
    def save_model(self, path):
        """保存模型"""
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.dfdn_model.save_weights(path)
        
    def load_model(self, path):
        """加载模型"""
        self.dfdn_model.load_weights(path)

# 示例用法
if __name__ == "__main__":
    # 创建模型实例
    model = DynamicFeatureDecouplingNetwork(
        input_shape=(256, 256, 1),
        modality='CT'
    )
    
    # 编译模型
    model.compile_model()
    
    # 打印模型结构
    model.dfdn_model.summary() 