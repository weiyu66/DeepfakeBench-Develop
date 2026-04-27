# DeepfakeBench Web Demo - 开发计划

## 最终技术栈确认
- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Python FastAPI + Uvicorn
- **推理**: DeepfakeBench PyTorch 模型
- **人脸预处理**: facenet-pytorch (MTCNN)

---

## Todo 执行清单

### Phase 1: 环境准备与模型集成
- [ ] 克隆 DeepfakeBench 官方仓库到 `third_party/DeepfakeBench`
- [ ] 创建 Python 虚拟环境，安装项目依赖
- [ ] 下载/准备至少一个预训练模型权重（如 UCF、RECCE）
- [ ] 编写 `inference.py`：封装单张图片推理接口（人脸检测 → 预处理 → 模型推理 → 返回概率）

### Phase 2: 后端服务开发
- [ ] 初始化 FastAPI 项目结构（`backend/` 目录）
- [ ] 实现 `/predict` 接口：接收图片文件，调用 `inference.py` 推理，返回 JSON 结果
- [ ] 添加 CORS 配置，允许前端跨域访问
- [ ] 添加请求日志与基础错误处理
- [ ] 本地测试后端接口（curl / Postman）

### Phase 3: 前端界面开发
- [ ] 初始化 Vue 3 + Vite 项目（`frontend/` 目录）
- [ ] 安装 Element Plus 组件库
- [ ] 实现图片上传组件（支持拖拽、预览）
- [ ] 调用后端 `/predict` 接口，展示推理结果（真实/伪造概率条）
- [ ] 添加 loading 状态与错误提示
- [ ] 优化 UI 布局（居中卡片、简洁美观）

### Phase 4: 联调与优化
- [ ] 前后端联调，确保端到端流程通畅
- [ ] 测试多类型图片（真实人脸、伪造人脸、非人脸）
- [ ] 优化推理性能（GPU 加速、模型缓存）
- [ ] 编写项目 README，说明安装与运行方式

---

## 项目目录结构（预期）

```
v0/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── inference.py         # 推理封装
│   ├── config.yaml          # 模型配置
│   └── requirements.txt     # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   └── UploadPanel.vue
│   │   └── api.js           # 后端接口封装
│   ├── package.json
│   └── vite.config.js
├── third_party/
│   └── DeepfakeBench/       # 官方仓库（子模块或克隆）
├── models/                  # 预训练权重存放目录
└── docs/
    ├── research_plan.md
    ├── tech_stack_decision.md
    └── development_plan.md
```

---

## 关键接口定义

### POST /predict
- **Request**: `multipart/form-data`，字段 `file`
- **Response**:
```json
{
  "success": true,
  "data": {
    "is_fake": false,
    "confidence": 0.12,
    "message": "该图片被判定为真实人脸，伪造概率 12%"
  }
}
```

## 注意事项
1. **模型权重**：DeepfakeBench 官方可能不提供直接下载链接，需自行训练或寻找社区分享权重
2. **人脸检测**：上传图片可能不含人脸，需要做好异常处理并返回友好提示
3. **性能**：首次加载模型较慢，建议后端启动时预加载模型到内存/GPU
