# DeepfakeBench Web Demo

基于 [DeepfakeBench](https://github.com/SCLBD/DeepfakeBench) 的网页端 Deepfake 识别系统。用户上传含有人脸的图片，后端进行人脸检测与 Deepfake 检测，返回伪造概率结果。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + `@element-plus/icons-vue` |
| 后端 | Python FastAPI + Uvicorn |
| 推理 | DeepfakeBench (PyTorch) + facenet-pytorch (MTCNN) |

## 项目结构

```
v0/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── inference.py         # 推理封装（人脸检测 + 模型推理）
│   ├── weight_config.py     # 权重自动扫描与检测器映射
│   ├── test_load_all.py     # 批量测试所有已下载检测器
│   ├── requirements.txt     # Python 依赖
│   └── uploads/             # 上传临时文件目录（运行时自动创建）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主页面
│   │   ├── api.js           # 后端接口封装
│   │   ├── components/
│   │   │   ├── UploadPanel.vue   # 图片上传组件
│   │   │   └── ResultCard.vue    # 结果展示组件
│   │   └── main.js
│   ├── vite.config.js       # Vite 配置（含代理）
│   ├── package.json
│   └── public/              # 静态资源（favicon、图标等）
├── scripts/
│   └── download_weights.py  # 自动下载官方预训练权重
├── third_party/
│   └── DeepfakeBench/       # 官方仓库（Git 子模块）
├── models/                  # 预训练权重存放目录（需自行准备或脚本下载）
├── docs/                    # 项目规划文档
└── .gitmodules              # Git 子模块配置
```

## 环境要求

- Python >= 3.8
- Node.js >= 18
- PyTorch >= 2.0（CUDA 可选，无 GPU 时自动回退 CPU）

## 快速开始

### 1. 克隆项目

本项目使用 Git 子模块管理 `third_party/DeepfakeBench`。

```bash
# 方式一：克隆时一并拉取子模块
git clone --recurse-submodules https://github.com/weiyu66/DeepfakeBench-Develop.git

# 方式二：如果已克隆，手动初始化子模块
git submodule update --init --recursive
```

### 2. 安装后端依赖

使用 conda 或系统 Python（>=3.8）：

```bash
# 示例使用已有 conda 环境
"D:\CondaEnvironment\yolo_v5\python.exe" -m pip install -r backend/requirements.txt

# 或创建新环境
python -m venv backend/venv
backend\venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

> 注意：部分依赖可能需要额外安装，如遇报错请根据提示补充（如 `simplejson`、`fvcore`、`loralib`、`opencv-python-headless` 等）。主要依赖包括 `torch`、`torchvision`、`facenet-pytorch`、`albumentations`、`timm`、`transformers`、`kornia` 等，详见 [`backend/requirements.txt`](backend/requirements.txt)。

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 准备模型权重（可选但推荐）

项目已内置权重自动扫描机制（[`backend/weight_config.py`](backend/weight_config.py)），会根据 `models/` 目录下的 `.pth` 文件名自动匹配对应检测器。当前支持的映射关系包括：

| 文件名关键字 | 检测器名称 |
|-------------|-----------|
| `cnnaug` / `resnet34` | `resnet34` |
| `capsule` | `capsule_net` |
| `core` | `core` |
| `effnb4` / `efficientnet` | `efficientnetb4` |
| `xception` | `xception` |
| `recce` | `recce` |
| `meso4` / `meso4Inception` | `meso4` / `meso4Inception` |
| `f3net` / `spsl` / `srm` / `fwa` / `ffd` / `facexray` / `ucf` | 对应同名检测器 |

> 系统启动时优先选择 `resnet34`，其次按扫描顺序加载第一个可用检测器。

**方式一：自动下载**
```bash
python scripts/download_weights.py
```
脚本会自动查询 [DeepfakeBench Releases](https://github.com/SCLBD/DeepfakeBench/releases) 并下载全部权重到 `models/` 目录。

**方式二：手动放置**
- 从官方 [Releases](https://github.com/SCLBD/DeepfakeBench/releases) 下载 `.pth` 权重文件
- 将文件放入 `models/` 目录
- 系统启动时会自动识别并加载（优先 `resnet34`，其次按扫描顺序）

> 无预训练权重时模型将以随机初始化运行，检测结果无意义。

### 5. 启动服务

#### 启动后端

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> 可通过环境变量强制指定检测器与权重：
> ```bash
> # Linux/macOS
> export DFB_DETECTOR=efficientnetb4
> export DFB_WEIGHTS=/absolute/path/to/effnb4_best.pth
> python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
>
> # Windows PowerShell
> $env:DFB_DETECTOR="efficientnetb4"
> $env:DFB_WEIGHTS="D:\\path\\to\\effnb4_best.pth"
> python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
> ```

#### 启动前端

```bash
cd frontend
npm run dev
```

### 6. 访问应用

打开浏览器访问 [http://localhost:5173](http://localhost:5173)

## API 说明

### 根接口
```
GET /
```
返回服务基本信息与接口导航。

### 健康检查
```
GET /health
```
返回模型加载状态及当前使用的检测器名称。

### 图片检测
```
POST /predict
Content-Type: multipart/form-data

file: <图片文件>
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "is_fake": false,
    "confidence": 0.12,
    "message": "该图片被判定为 **真实人脸**，伪造概率 12.0%",
    "has_face": true
  }
}
```

> `message` 中使用了 Markdown 加粗语法（如 `**真实人脸**` / `**伪造人脸**`），前端可直接渲染。

## 注意事项

1. **模型权重**：官方可能未提供所有检测器的直接下载链接，部分权重需自行训练获取。
2. **人脸检测**：上传图片中需包含清晰可见的人脸，否则将返回 "未检测到人脸" 提示。
3. **GPU 加速**：如系统有 CUDA，推理将自动使用 GPU；否则回退到 CPU（速度较慢）。
4. **按需加载检测器**：当前 `inference.py` 已做优化，按需加载 `resnet34`、`capsule_net`、`core`、`efficientnetb4` 等检测器，避免一次性导入全部 36 个检测器（部分检测器依赖未安装库如 `dlib`）。如需使用其他检测器，请在 `inference.py` 中按需添加 `_load_module_from_file` 调用。
5. **前端代理**：开发环境下，`vite.config.js` 已将 `/api` 前缀代理到后端 `http://127.0.0.1:8000`。如需自定义后端地址，可设置前端环境变量 `VITE_API_BASE_URL`。
6. **批量测试**：可使用 [`backend/test_load_all.py`](backend/test_load_all.py) 批量验证 `models/` 目录下所有已下载权重的加载情况。

## 常见问题

**Q: 模型加载时报 `No module named 'dlib'`？**
A: `inference.py` 已通过按需加载策略绕过此问题。如需使用依赖 `dlib` 的检测器，请执行 `pip install dlib`（Windows 上需先安装 CMake 和 Visual C++ Build Tools）。

**Q: 前端请求后端报跨域错误？**
A: `vite.config.js` 中已配置代理到 `http://127.0.0.1:8000`，开发环境下前端自动转发 API 请求。生产环境请配置反向代理，或在构建时通过环境变量 `VITE_API_BASE_URL` 指定后端地址。

## 相关脚本

| 脚本 | 说明 |
|------|------|
| `scripts/download_weights.py` | 查询并下载 DeepfakeBench 官方 Releases 中的预训练权重 |
| `backend/test_load_all.py` | 批量加载 `models/` 目录下所有检测器，验证权重可用性 |
| `backend/weight_config.py` | 独立运行可查看当前已识别的权重与默认检测器 |

## 致谢

- [DeepfakeBench](https://github.com/SCLBD/DeepfakeBench) - 统一的 Deepfake 检测基准平台
