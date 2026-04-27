"""
DeepfakeBench 单张图片推理封装
支持：人脸检测(MTCNN) -> 对齐裁剪 -> 预处理 -> 模型推理 -> 返回概率
"""
import os
import sys
import yaml
import torch
import numpy as np
from PIL import Image
from typing import Dict, Optional, Tuple
import importlib.util
import types

# 将 DeepfakeBench training 目录加入 Python 路径
DFB_TRAINING_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'third_party', 'DeepfakeBench', 'training'
)
if DFB_TRAINING_PATH not in sys.path:
    sys.path.insert(0, DFB_TRAINING_PATH)

# 先导入 registry（不触发 detectors/__init__.py）
from metrics.registry import DETECTOR

# --- 策略：把 training/detectors 注册为一个 package，但绕过 __init__.py 中全部检测器的导入 ---
# 1. 注册 detectors 包本身
detectors_pkg = types.ModuleType('detectors')
detectors_pkg.__path__ = [os.path.join(DFB_TRAINING_PATH, 'detectors')]
detectors_pkg.__package__ = 'detectors'
detectors_pkg.DETECTOR = DETECTOR
sys.modules['detectors'] = detectors_pkg

# 2. 按需加载 detectors 包内部的子模块（按顺序处理依赖）
def _load_module_from_file(pkg_name: str, module_name: str, file_name: str):
    full_name = f'{pkg_name}.{module_name}'
    file_path = os.path.join(DFB_TRAINING_PATH, pkg_name, file_name)
    spec = importlib.util.spec_from_file_location(full_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    setattr(sys.modules[pkg_name], module_name, module)
    return module

# 按需加载检测器模块（绕过 detectors/__init__.py 中全部 36 个检测器的同时导入）
_load_module_from_file('detectors', 'base_detector', 'base_detector.py')
_load_module_from_file('detectors', 'resnet34_detector', 'resnet34_detector.py')
_load_module_from_file('detectors', 'capsule_net_detector', 'capsule_net_detector.py')
_load_module_from_file('detectors', 'core_detector', 'core_detector.py')
_load_module_from_file('detectors', 'efficientnetb4_detector', 'efficientnetb4_detector.py')

from torchvision import transforms

# 尝试导入 MTCNN 进行人脸检测
try:
    from facenet_pytorch import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    MTCNN_AVAILABLE = False
    MTCNN = None

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DeepfakeInference:
    """
    封装 DeepfakeBench 模型的加载与单张图片推理。
    """

    def __init__(
        self,
        detector_config_path: str,
        weights_path: Optional[str] = None,
        resolution: int = 256,
        use_face_detect: bool = True,
    ):
        """
        Args:
            detector_config_path: 检测器 YAML 配置文件路径 (如 resnet34.yaml)
            weights_path: 预训练权重路径，None 则使用随机初始化权重
            resolution: 输入网络的图像尺寸
            use_face_detect: 是否使用 MTCNN 进行人脸检测与裁剪
        """
        self.resolution = resolution
        self.use_face_detect = use_face_detect and MTCNN_AVAILABLE

        # 1. 读取 detector 配置
        with open(detector_config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 2. 合并 test_config.yaml 中的通用配置（与官方 test.py 保持一致）
        test_config_path = os.path.join(DFB_TRAINING_PATH, 'config', 'test_config.yaml')
        if os.path.exists(test_config_path):
            with open(test_config_path, 'r', encoding='utf-8') as f:
                test_config = yaml.safe_load(f)
            self.config.update(test_config)
            if 'label_dict' in self.config:
                test_config['label_dict'] = self.config['label_dict']

        # 3. 针对特定检测器：如果提供了用户权重，跳过 backbone ImageNet 预训练加载
        if weights_path:
            self.config['pretrained'] = False  # 使用布尔值 False，跳过 backbone ImageNet 预训练加载
            if self.config.get('model_name') == 'core':
                # monkey-patch CoreDetector.build_backbone 跳过 torch.load
                core_mod = sys.modules.get('detectors.core_detector')
                if core_mod:
                    def _build_backbone_no_pretrain(self, config):
                        from metrics.registry import BACKBONE
                        import logging
                        backbone_class = BACKBONE[config['backbone_name']]
                        model_config = config['backbone_config']
                        backbone = backbone_class(model_config)
                        logging.getLogger(__name__).info('跳过 ImageNet 预训练权重，直接使用用户提供的完整权重')
                        return backbone
                    core_mod.CoreDetector.build_backbone = _build_backbone_no_pretrain

        # 4. 实例化模型
        model_name = self.config['model_name']
        model_class = DETECTOR[model_name]
        self.model = model_class(self.config).to(DEVICE)
        self.model.eval()

        # 5. 加载权重
        if weights_path and os.path.exists(weights_path):
            ckpt = torch.load(weights_path, map_location=DEVICE)
            self.model.load_state_dict(ckpt, strict=True)
            print(f"[DeepfakeInference] 权重加载成功: {weights_path}")
        else:
            print(f"[DeepfakeInference] 警告: 未提供权重文件或文件不存在，使用随机初始化权重")

        # 5. 初始化人脸检测器
        if self.use_face_detect:
            self.mtcnn = MTCNN(
                image_size=self.resolution,
                margin=20,
                min_face_size=40,
                thresholds=[0.6, 0.7, 0.7],
                factor=0.709,
                post_process=False,  # 我们手动做归一化
                device=DEVICE,
                keep_all=False,      # 只取最大的人脸
            )
        else:
            self.mtcnn = None
            if use_face_detect and not MTCNN_AVAILABLE:
                print("[DeepfakeInference] 警告: facenet-pytorch 未安装，跳过人脸检测")

        # 6. 定义图像预处理 (与官方一致: mean=0.5, std=0.5)
        self.transform = transforms.Compose([
            transforms.Resize((self.resolution, self.resolution)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

    def _detect_face(self, image: Image.Image) -> Optional[Image.Image]:
        """
        使用 MTCNN 检测并裁剪人脸。
        Returns:
            裁剪后的人脸 PIL.Image，如果检测不到人脸则返回 None
        """
        if self.mtcnn is None:
            return image

        # MTCNN 期望输入 numpy array (H, W, C) uint8
        img_np = np.array(image)
        face_tensor = self.mtcnn(img_np)

        if face_tensor is None:
            return None

        # face_tensor 是 [C, H, W] 0-255 范围，转回 PIL
        face_np = face_tensor.permute(1, 2, 0).cpu().numpy().astype(np.uint8)
        return Image.fromarray(face_np)

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Dict:
        """
        对单张图片进行 deepfake 检测。

        Args:
            image: PIL.Image (RGB)

        Returns:
            dict: {
                'success': bool,
                'is_fake': bool,       # True=伪造, False=真实
                'confidence': float,   # 伪造概率 0.0~1.0
                'message': str,
                'has_face': bool,      # 是否检测到了人脸
            }
        """
        # 1. 人脸检测
        face_img = self._detect_face(image)
        if face_img is None:
            return {
                'success': False,
                'is_fake': None,
                'confidence': None,
                'message': '未检测到人脸，请上传包含清晰人脸的图片',
                'has_face': False,
            }

        # 2. 预处理
        input_tensor = self.transform(face_img).unsqueeze(0).to(DEVICE)  # [1, 3, H, W]

        # 3. 构建 data_dict (与官方 test.py 保持一致)
        data_dict = {
            'image': input_tensor,
            'label': torch.tensor([0]).to(DEVICE),  # dummy label
            'mask': None,
            'landmark': None,
        }

        # 4. 推理
        predictions = self.model(data_dict, inference=True)
        prob = predictions['prob'].cpu().numpy()[0]  # shape 取决于输出

        # 处理不同模型的输出格式：
        # 通常 prob 是 [batch_size, num_classes] 的 softmax 输出
        # 我们取伪造类别的概率 (index=1)
        if prob.ndim > 0 and prob.shape[0] > 1:
            fake_prob = float(prob[1])
        else:
            # 有些模型直接输出单值 sigmoid
            fake_prob = float(prob) if np.isscalar(prob) else float(prob.item())

        # 5. 后处理（对 sigmoid 输出做校准，保证在 0~1 之间）
        fake_prob = np.clip(fake_prob, 0.0, 1.0)

        is_fake = fake_prob > 0.5

        if is_fake:
            msg = f"该图片被判定为 **伪造人脸**，伪造概率 {fake_prob*100:.1f}%"
        else:
            msg = f"该图片被判定为 **真实人脸**，伪造概率 {fake_prob*100:.1f}%"

        return {
            'success': True,
            'is_fake': bool(is_fake),
            'confidence': float(fake_prob),
            'message': msg,
            'has_face': True,
        }


# ================= 便捷函数 =================

def load_default_model(
    detector_name: str = "resnet34",
    weights_path: Optional[str] = None,
) -> DeepfakeInference:
    """
    根据检测器名称快速加载默认配置的模型。

    Args:
        detector_name: 检测器名称，如 resnet34, xception, efficientnetb4 等
        weights_path: 预训练权重路径

    Returns:
        DeepfakeInference 实例
    """
    config_path = os.path.join(
        DFB_TRAINING_PATH, 'config', 'detector', f'{detector_name}.yaml'
    )
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"未找到检测器配置: {config_path}")

    # 读取 resolution
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    resolution = cfg.get('resolution', 256)

    return DeepfakeInference(
        detector_config_path=config_path,
        weights_path=weights_path,
        resolution=resolution,
        use_face_detect=True,
    )


if __name__ == '__main__':
    # 简单自测
    print("[Self Test] 初始化 ResNet34 检测器（无权重）...")
    infer = load_default_model(detector_name="resnet34")

    # 创建一张随机图片做测试
    dummy_img = Image.new('RGB', (512, 512), color=(128, 128, 128))
    result = infer.predict(dummy_img)
    print(f"[Self Test] 结果: {result}")
