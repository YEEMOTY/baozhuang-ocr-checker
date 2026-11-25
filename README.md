# 包装型号一致性校验系统

基于 PaddleOCR + PyQt5 + OpenCV 的**三路摄像头包装型号一致性检测**系统。生产场景下，三台摄像头同时识别包装上的型号，任意一路与其他两路不一致时触发声光报警并保存现场截图。

## 核心功能

| 模块 | 说明 |
|---|---|
| **镜头一 / 镜头二** | 海康 GigE 工业相机（硬触发拍照），各自独立 OCR，多帧投票确认标准答案 |
| **镜头三** | USB 摄像头，OCR 结果必须落在 {镜头一答案, 镜头二答案} 的集合里，否则判定为不一致 |
| **一致性校验** | 三路结果两两比对，任何偏差都触发报警 + 保存现场 |
| **声光报警** | pyserial 驱动串口报警器（默认 COM14 / COM16），不一致时闪光 + 响铃 5 秒后自动关闭 |
| **现场留证** | 报警瞬间保存画面截图到 `baojing/镜头一|二|三/` 目录，文件名带时间戳和识别结果 |

## 项目结构

```
shiyan/
├── 文字提取/
│   ├── jinzhai(全).py       ← ⭐ 主程序（生产版，三路摄像头 + 一致性校验 + 报警）
│   ├── 金寨窗口0.py          ← PyQt5 UI 界面补全文件（setupUi）
│   ├── 包装型号识别.py        ← 电脑摄像头单路 OCR + PyQt 界面（调试/演示用）
│   ├── 视频文字提取.py        ← 命令行版视频/摄像头 OCR
│   ├── 图片提取.py           ← 单张图片 OCR
│   ├── 正则判断.py           ← 包装型号正则筛选
│   └── ...
├── HKCamera_class.py          ← 海康 GigE 相机二次封装
├── MvCameraControl_class.py   ← 海康 MVS SDK 官方 ctypes 封装
├── CameraParams_header.py     ← SDK 参数结构体（官方 xml2py 生成，勿改）
├── CameraParams_const.py      ← SDK 常量（勿改）
├── MvErrorDefine_const.py     ← SDK 错误码（勿改）
├── PixelType_header.py        ← SDK 像素类型（勿改）
├── .gitignore
├── requirements.txt
└── README.md
```

## 快速开始

### 环境要求

- **操作系统**：Windows（海康 MVS SDK 仅支持 Windows）
- **Python**：3.8.x（paddlepaddle-gpu 2.6.2 + Python 3.9 有兼容性问题）
- **GPU**：NVIDIA 显卡 + CUDA 11.x（当前硬编码 `use_gpu=True`，无 GPU 需改代码降级 CPU）
- **海康 MVS SDK**：需用户自行安装（提供 `MvCameraControl.dll`），SDK 文件已在仓库中，运行时 DLL 需能被系统找到（MVS 安装后会自动加入 PATH）

### 安装依赖

```powershell
# 创建虚拟环境（Windows PowerShell）
python -m venv .venv
.venv\Scripts\Activate.ps1

# 安装核心依赖
pip install -r requirements.txt
```

### 运行主程序

```powershell
# 默认参数运行（两台海康相机 IP=192.168.20.20/60，USB 摄像头编号=1）
& ".venv\Scripts\python.exe" "文字提取\jinzhai(全).py"

# 自定义参数运行
& ".venv\Scripts\python.exe" "文字提取\jinzhai(全).py" ^
    --camera1_ip 192.168.20.20 ^
    --camera2_ip 192.168.20.60 ^
    --cap_numb3 0 ^
    --SERIAL_PORT1 COM5 ^
    --baojing_dir "D:\logs"
```

### 命令行参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--camera1_ip` | `192.168.20.20` | 海康 GigE 镜头一 IP |
| `--camera2_ip` | `192.168.20.60` | 海康 GigE 镜头二 IP |
| `--cap_numb3` | `1` | USB 镜头三摄像头编号（0=默认） |
| `--SERIAL_PORT1` | `COM14` | 镜头一报警器串口号 |
| `--SERIAL_PORT2` | `COM16` | 镜头二/三报警器串口号 |
| `--frame_delay` | `67` | QTimer 取帧间隔（毫秒） |
| `--baojing_dir` | `./baojing` | 报警截图保存根目录（自动创建 镜头一/二/三 子目录） |

### 启动调试版（仅电脑摄像头）

如果手头没有海康 GigE 相机，可运行单路摄像头版本：

```powershell
& ".venv\Scripts\python.exe" "文字提取\包装型号识别.py"
```

## 一致性校验逻辑

```
海康镜头一 ──┐
              ├── OCR + 多帧投票 ──→ {daan1, daan2} 合集 ──┐
海康镜头二 ──┘                                             ├── USB镜头三 OCR 结果
                                                          比对：text3 在合集中？
                                                              YES → 通过
                                                              NO  → 报警 + 保存现场 + 显示⚠
```

**镜头一/二的投票机制**：同一帧里 PaddleOCR 可能识别出多个候选型号，程序连续收集 N 帧候选做 Counter 投票，出现次数最多的作为标准答案 `daan1` / `daan2`。

**跳帧策略**：镜头一每 5 帧 OCR 一次，镜头二/三每 3 帧 OCR 一次（PaddleOCR GPU 推理仍有几百毫秒延迟，必须跳帧才能保证画面不丢帧）。

## 型号筛选规则

正则在 `jinzhai(全).py` 第 58-71 行（`process_string` 函数）：

- 必须同时包含字母和数字，长度 2~10 位：`(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d-]{2,10}$`
- 或者纯数字 4~7 位：`\d{4,7}$`

易错字符纠错在 `set_bing` 函数（第 73-78 行）：`0→O`、`s→5`、`I→1`、`L→1`、`B→8`、`p→P`。

## 已知限制

1. **海康 SDK 依赖**：`MvCameraControl_class.py` 需要加载 `MvCameraControl.dll`，必须安装海康 MVS 并将 DLL 路径加入系统 PATH
2. **无 GPU 时崩溃**：OCR 硬编码 `use_gpu=True`，无 CUDA 环境需手动改为 `False`（每帧推理约 1~2 秒，实时性不行）
3. **异常捕获过粗**：`_queryFrame` 和三个 OCR 方法里有裸 `except: pass`，生产环境建议细化异常
4. **USB 摄像头定期释放**：守护线程每 30 分钟 release + reopen 一次 camera3，这是应对 USB 摄像头长期运行偶发卡死的 workaround

## 许可证

本项目包含 PyQt5（GPLv3）和海康 MVS SDK（自有许可）的调用代码，分发时需注意各自的许可要求。
