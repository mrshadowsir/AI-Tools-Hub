# 🆓 Open-Source AI Hub

## 🌐 Browser AI Lab

The repository contains a browser-based AI Lab. No Python package, paid API key, or account is required for the browser app itself.

### Start the server

**Windows PowerShell**
```powershell
.start.ps1
```

**Windows CMD**
```bat
start.bat
```

**Linux / macOS**
```bash
bash start.sh
```

**Termux (Android)**
```bash
bash start-termux.sh
```

**Any terminal with Python 3**
```bash
python serve.py
```

The server prints the browser address and a LAN address. Open the displayed URL in your browser.

### How it works

The server only serves the web files. Supported ONNX models are loaded by Transformers.js and inference happens in the browser. The first model load downloads model files into the browser cache.

### Browser model limitation

Only browser-compatible ONNX models are directly runnable in the web app. The full open-source model directory contains many more models that may require a different runtime.

## 📚 Directory

- [Open-Source AI Model Index](./OPEN_SOURCE_AI_MODELS.md)
- [Open-Source AI Software & Runtimes](./OPEN_SOURCE_AI_TOOLS.md)
