# DeepfakeBench Web Demo - Research Plan

## 项目概述
基于 https://github.com/SCLBD/DeepfakeBench 构建网页端 Deepfake 识别 Demo。

## 调研方向

### 1. 模型加载与推理方式
- DeepfakeBench 支持多种检测模型（如 UCF, RECCE, SBI, CORE 等）
- 需要确认官方是否提供预训练权重下载方式
- 需要确认推理入口（命令行脚本 / API）

### 2. 项目依赖与环境
- Python 版本要求
- PyTorch 版本
- 关键依赖库（opencv-python, torchvision 等）
- CUDA 要求

### 3. 推理输入输出格式
- 输入：单张图片 or 视频帧？
- 输出：概率值 / 二分类结果？
- 预处理流程（尺寸、归一化等）

### 4. Web Demo 架构建议
- 后端：Flask / FastAPI 封装推理接口
- 前端：Vue3 / React / 纯 HTML 上传组件
- 部署：本地运行 / Docker
