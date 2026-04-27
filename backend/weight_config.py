"""
权重与检测器映射配置
自动扫描 models/ 目录，建立 权重文件名 -> 检测器名称 的映射
"""
import os
import glob

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

# 文件名前缀 / 关键字 -> 检测器名称
WEIGHT_DETECTOR_MAP = {
    'cnnaug': 'resnet34',
    'resnet34': 'resnet34',
    'capsule': 'capsule_net',
    'core': 'core',
    'effnb4': 'efficientnetb4',
    'efficientnet': 'efficientnetb4',
    'xception': 'xception',
    'recce': 'recce',
    'ucf': 'ucf',
    'meso4': 'meso4',
    'meso4Inception': 'meso4Inception',
    'f3net': 'f3net',
    'spsl': 'spsl',
    'srm': 'srm',
    'fwa': 'fwa',
    'ffd': 'ffd',
    'facexray': 'facexray',
}


def discover_weights():
    """
    扫描 models/ 目录，返回可用的 (detector_name, weight_path) 列表
    """
    results = []
    if not os.path.isdir(MODELS_DIR):
        return results

    for pth_path in glob.glob(os.path.join(MODELS_DIR, '*.pth')):
        fname = os.path.basename(pth_path).lower()
        matched_detector = None
        for keyword, detector in WEIGHT_DETECTOR_MAP.items():
            if keyword.lower() in fname:
                matched_detector = detector
                break
        if matched_detector:
            results.append((matched_detector, pth_path))
    return results


def get_default_weight():
    """
    返回默认使用的 (detector_name, weight_path)，优先 resnet34
    """
    discovered = discover_weights()
    if not discovered:
        return None, None

    # 优先返回 resnet34/cnnaug
    for det, path in discovered:
        if det == 'resnet34':
            return det, path

    # 否则返回第一个发现的
    return discovered[0]


if __name__ == '__main__':
    print("Discovered weights:")
    for det, path in discover_weights():
        print(f"  {det:20s} -> {path}")
    det, path = get_default_weight()
    print(f"\nDefault: {det} -> {path}")
