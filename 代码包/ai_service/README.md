# AI Service — 智能垃圾分类识别与商业分析

## 目录结构
```
ai_service/
├── recognition/          # 垃圾图像识别服务 (YOLOv11 + ONNX Runtime)
│   ├── app.py            # Flask 应用入口 (port 8081)
│   ├── inference.py      # ONNX 推理引擎
│   ├── preprocess.py     # 图片下载、校验、预处理
│   ├── postprocess.py    # 品类映射、投放指引
│   ├── config.yaml       # 模型/推理/安全配置
│   └── classes.txt       # 38类垃圾中文名称
├── llm/                  # 大语言模型分析服务 (port 8083)
│   ├── app.py            # Flask 应用入口
│   ├── generator.py      # LLM报告生成
│   ├── preprocessor.py   # 数据聚合预处理
│   ├── formatter.py      # Markdown报告格式化
│   └── prompts/          # 提示词模板
│       ├── governance.py # 治理分析
│       └── business.py   # 商业分析
├── training/             # 模型训练工具
│   ├── train.py          # 增量训练入口
│   ├── validate.py       # 数据集校验
│   └── export_onnx.py    # PyTorch → ONNX 导出
└── requirements.txt
```

## 启动
```bash
# 识别服务
cd ai_service && python -m ai_service.recognition.app

# LLM分析服务
cd ai_service && python -m ai_service.llm.app
```

Docker:
```bash
docker build -t ai-service .
docker run -p 8081:8081 -p 8083:8083 ai-service
```
