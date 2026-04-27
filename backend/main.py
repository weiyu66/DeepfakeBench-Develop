"""
DeepfakeBench Web Demo - FastAPI 后端服务
"""
import os
import sys
import uuid
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

# 将当前目录加入路径，以便导入 inference
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inference import DeepfakeInference, load_default_model
import weight_config as dfb_config

# ================= 配置 =================
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 自动扫描 models/ 目录获取默认检测器与权重
DEFAULT_DETECTOR, DEFAULT_WEIGHTS = dfb_config.get_default_weight()
if DEFAULT_DETECTOR is None:
    # 回退到环境变量或默认值
    DEFAULT_DETECTOR = os.getenv("DFB_DETECTOR", "resnet34")
    DEFAULT_WEIGHTS = os.getenv("DFB_WEIGHTS", None)

# ================= 全局模型实例（启动时预加载） =================
inference_engine: Optional[DeepfakeInference] = None

# ================= FastAPI App =================
app = FastAPI(
    title="DeepfakeBench Web Demo",
    description="基于 DeepfakeBench 的网页端 Deepfake 识别服务",
    version="1.0.0",
)

# CORS：允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """
    服务启动时预加载模型到内存/GPU，避免首次请求时加载过慢。
    """
    global inference_engine
    print(f"[Startup] 正在加载检测器: {DEFAULT_DETECTOR} ...")
    try:
        inference_engine = load_default_model(
            detector_name=DEFAULT_DETECTOR,
            weights_path=DEFAULT_WEIGHTS,
        )
        print("[Startup] 模型加载完成！")
    except Exception as e:
        print(f"[Startup] 模型加载失败: {e}")
        # 这里不退出，让服务继续运行，但 predict 接口会返回错误
        raise e


@app.on_event("shutdown")
def shutdown_event():
    """
    清理上传的临时文件。
    """
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    print("[Shutdown] 清理完成")


@app.get("/")
def root():
    return {
        "message": "DeepfakeBench Web Demo API",
        "docs": "/docs",
        "predict_endpoint": "POST /predict",
    }


@app.get("/health")
def health():
    """健康检查接口"""
    return {
        "status": "ok",
        "model_loaded": inference_engine is not None,
        "detector": DEFAULT_DETECTOR,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    上传单张图片进行 Deepfake 检测。

    - **file**: 图片文件 (jpg, png, jpeg, webp)
    - **返回**: JSON 包含 is_fake, confidence, message
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="模型尚未加载完成，请稍后重试")

    # 1. 校验文件类型
    allowed_ext = {"jpg", "jpeg", "png", "webp", "bmp"}
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，请上传 {allowed_ext} 格式的图片",
        )

    # 2. 保存临时文件
    temp_name = f"{uuid.uuid4().hex}.{ext}"
    temp_path = UPLOAD_DIR / temp_name
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    finally:
        file.file.close()

    # 3. 读取图片并推理
    try:
        image = Image.open(temp_path).convert("RGB")
        result = inference_engine.predict(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推理失败: {str(e)}")
    finally:
        # 清理临时文件
        if temp_path.exists():
            temp_path.unlink()

    # 4. 返回结果
    if not result["success"]:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": result["message"]},
        )

    return {
        "success": True,
        "data": {
            "is_fake": result["is_fake"],
            "confidence": round(result["confidence"], 4),
            "message": result["message"],
            "has_face": result["has_face"],
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
