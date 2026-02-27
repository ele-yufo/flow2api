# Flow2API

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.119.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

**一个功能完整的 OpenAI 兼容 API 服务，为 Google Flow 提供统一的接口**

</div>

> 🔀 **Fork 说明**：本项目基于 [TheSmallHanCat/flow2api](https://github.com/TheSmallHanCat/flow2api) 二次开发，主要增强：
>
> - 🍌 **Nano Banana 2 集成** — 首发支持 Google 最新生图模型 (内部代号 `NARWHAL` / Gemini 3.1 Flash Image)，15 个模型变体覆盖所有尺寸和分辨率
> - 🎭 **Playwright 无头浏览器打码** — 将浏览器打码方案从 patchright 迁移至 Playwright，提升稳定性和兼容性
> - 🤖 **AI Coding Skill** — 内置 Agent 工具脚本 (`skills/`)，支持 Claude Code / Codex / Antigravity 等 AI 编程助手直接调用生成图片和视频

## ✨ 核心特性

- 🎨 **文生图** / **图生图** — 支持 Nano Banana 2、Gemini 2.5 Flash、Gemini 3.0 Pro、Imagen 4.0
- 🎬 **文生视频** / **图生视频** / **多图生视频** — 支持 Veo 2.0 / 2.1 / 3.1
- 🎞️ **首尾帧视频** — 1-2 张图作为首尾帧生成过渡视频
- 📐 **多尺寸** — 横屏 / 竖屏 / 方形 / 4:3 / 3:4
- 🔍 **高分辨率放大** — 图片支持 2K/4K 放大，视频支持 1080P/4K 放大
- 🔄 **AT/ST 自动刷新** — AT 过期自动刷新，ST 过期时自动通过浏览器更新
- 📊 **余额显示** — 实时查询和显示 VideoFX Credits
- 🚀 **负载均衡** — 多 Token 轮询和并发控制
- 🌐 **代理支持** — 支持 HTTP/SOCKS5 代理
- 📱 **Web 管理界面** — 直观的 Token 和配置管理
- 🤖 **AI Coding Skill** — 内置 AI Agent 工具脚本，开箱即用

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose（推荐）
- 或 Python 3.8+

- 由于 Flow 增加了额外的验证码，你可以自行选择使用浏览器打码或第三方打码：
注册 [YesCaptcha](https://yescaptcha.com/i/13Xd8K) 并获取 API key，将其填入系统配置页面 `YesCaptcha API密钥` 区域

- 自动更新 ST 浏览器拓展：[Flow2API-Token-Updater](https://github.com/TheSmallHanCat/Flow2API-Token-Updater)

### 方式一：Docker 部署（推荐）

#### 标准模式（不使用代理）

```bash
# 克隆项目
git clone https://github.com/ele-yufo/flow2api.git
cd flow2api

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### WARP 模式（使用代理）

```bash
# 使用 WARP 代理启动
docker-compose -f docker-compose.warp.yml up -d

# 查看日志
docker-compose -f docker-compose.warp.yml logs -f
```

### 方式二：本地部署

```bash
# 克隆项目
git clone https://github.com/ele-yufo/flow2api.git
cd flow2api

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

### 首次访问

服务启动后,访问管理后台: **http://localhost:8000**,首次登录后请立即修改密码!

- **用户名**: `admin`
- **密码**: `admin`

## 📋 支持的模型

### 图片生成

| 模型名称 | 内部模型 | 说明 | 尺寸 |
|---------|---------|------|------|
| `nano-banana-2-landscape` | NARWHAL | Nano Banana 2 (Gemini 3.1 Flash) | 横屏 |
| `nano-banana-2-portrait` | NARWHAL | Nano Banana 2 (Gemini 3.1 Flash) | 竖屏 |
| `nano-banana-2-square` | NARWHAL | Nano Banana 2 (Gemini 3.1 Flash) | 方形 |
| `nano-banana-2-four-three` | NARWHAL | Nano Banana 2 (Gemini 3.1 Flash) | 4:3 |
| `nano-banana-2-three-four` | NARWHAL | Nano Banana 2 (Gemini 3.1 Flash) | 3:4 |
| `gemini-2.5-flash-image-landscape` | GEM_PIX | Gemini 2.5 Flash | 横屏 |
| `gemini-2.5-flash-image-portrait` | GEM_PIX | Gemini 2.5 Flash | 竖屏 |
| `gemini-3.0-pro-image-landscape` | GEM_PIX_2 | Gemini 3.0 Pro | 横屏 |
| `gemini-3.0-pro-image-portrait` | GEM_PIX_2 | Gemini 3.0 Pro | 竖屏 |
| `gemini-3.0-pro-image-square` | GEM_PIX_2 | Gemini 3.0 Pro | 方形 |
| `gemini-3.0-pro-image-four-three` | GEM_PIX_2 | Gemini 3.0 Pro | 4:3 |
| `gemini-3.0-pro-image-three-four` | GEM_PIX_2 | Gemini 3.0 Pro | 3:4 |
| `imagen-4.0-generate-preview-landscape` | IMAGEN_3_5 | Imagen 4.0 | 横屏 |
| `imagen-4.0-generate-preview-portrait` | IMAGEN_3_5 | Imagen 4.0 | 竖屏 |

> 💡 所有图片模型均支持 **2K** 和 **4K** 放大版本，在模型名后加 `-2k` 或 `-4k` 即可，例如 `nano-banana-2-landscape-2k`

### 视频生成

#### 文生视频 (T2V)
⚠️ **不支持上传图片**

| 模型名称 | 说明 | 尺寸 |
|---------|------|------|
| `veo_3_1_t2v_fast_portrait` | Veo 3.1 Fast | 竖屏 |
| `veo_3_1_t2v_fast_landscape` | Veo 3.1 Fast | 横屏 |
| `veo_3_1_t2v_fast_portrait_ultra` | Veo 3.1 Ultra | 竖屏 |
| `veo_3_1_t2v_fast_ultra` | Veo 3.1 Ultra | 横屏 |
| `veo_3_1_t2v_portrait` | Veo 3.1 | 竖屏 |
| `veo_3_1_t2v_landscape` | Veo 3.1 | 横屏 |
| `veo_2_1_fast_d_15_t2v_portrait` | Veo 2.1 | 竖屏 |
| `veo_2_1_fast_d_15_t2v_landscape` | Veo 2.1 | 横屏 |
| `veo_2_0_t2v_portrait` | Veo 2.0 | 竖屏 |
| `veo_2_0_t2v_landscape` | Veo 2.0 | 横屏 |

#### 首尾帧模型 (I2V)
📸 **支持 1-2 张图片：1 张作为首帧，2 张作为首尾帧**

| 模型名称 | 说明 | 尺寸 |
|---------|------|------|
| `veo_3_1_i2v_s_fast_portrait_fl` | Veo 3.1 Fast | 竖屏 |
| `veo_3_1_i2v_s_fast_fl` | Veo 3.1 Fast | 横屏 |
| `veo_3_1_i2v_s_fast_portrait_ultra_fl` | Veo 3.1 Ultra | 竖屏 |
| `veo_3_1_i2v_s_fast_ultra_fl` | Veo 3.1 Ultra | 横屏 |
| `veo_2_1_fast_d_15_i2v_portrait` | Veo 2.1 | 竖屏 |
| `veo_2_1_fast_d_15_i2v_landscape` | Veo 2.1 | 横屏 |
| `veo_2_0_i2v_portrait` | Veo 2.0 | 竖屏 |
| `veo_2_0_i2v_landscape` | Veo 2.0 | 横屏 |

#### 多图生成 (R2V)
🖼️ **支持多张参考图片**

| 模型名称 | 说明 | 尺寸 |
|---------|------|------|
| `veo_3_1_r2v_fast_portrait` | Veo 3.1 Fast | 竖屏 |
| `veo_3_1_r2v_fast` | Veo 3.1 Fast | 横屏 |
| `veo_3_1_r2v_fast_portrait_ultra` | Veo 3.1 Ultra | 竖屏 |
| `veo_3_1_r2v_fast_ultra` | Veo 3.1 Ultra | 横屏 |

> 💡 T2V / I2V / R2V 视频模型均支持 **1080P** 和 **4K** 放大版本，在模型名后加 `-1080p` 或 `-4k` 即可

## 📡 API 使用示例

所有 API 均使用 OpenAI 兼容格式，需要使用 **流式** (`"stream": true`)。

### 文生图

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Authorization: Bearer han1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2-landscape",
    "messages": [
      {
        "role": "user",
        "content": "一只可爱的猫咪在花园里玩耍"
      }
    ],
    "stream": true
  }'
```

### 图生图

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Authorization: Bearer han1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2-landscape",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "将这张图片变成水彩画风格"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,<base64_encoded_image>"
            }
          }
        ]
      }
    ],
    "stream": true
  }'
```

### 文生视频

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Authorization: Bearer han1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "veo_3_1_t2v_fast_landscape",
    "messages": [
      {
        "role": "user",
        "content": "一只小猫在草地上追逐蝴蝶"
      }
    ],
    "stream": true
  }'
```

### 首尾帧生成视频

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Authorization: Bearer han1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "veo_3_1_i2v_s_fast_fl",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "从第一张图过渡到第二张图"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,<首帧base64>"
            }
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,<尾帧base64>"
            }
          }
        ]
      }
    ],
    "stream": true
  }'
```

## 🤖 AI Coding Skill

本项目内置了一个可供 AI Coding Agent（如 Claude Code、Codex、Antigravity 等）使用的 Skill，位于 `skills/` 目录。

通过将 Skill 软链接到你的 Agent 技能目录，Agent 可以直接调用 `generate_media.py` 脚本进行批量图片/视频生成，无需手工构造 API 请求。

### 安装方式

```bash
# 根据你使用的 Agent，选择对应的路径
ln -s $(pwd)/skills ~/.codex/skills/flow2api
ln -s $(pwd)/skills ~/.claude/skills/flow2api
ln -s $(pwd)/skills ~/.antigravity/skills/flow2api
```

### 快速使用

```bash
# 文生图
python3 skills/scripts/generate_media.py \
  --mode t2i --direction landscape \
  --prompt "A cinematic poster" --batch-size 2

# 图生视频
python3 skills/scripts/generate_media.py \
  --mode i2v --direction portrait \
  --prompt "Day to night transition" \
  --image /path/to/start.png --image /path/to/end.png
```

详细说明请参阅 [skills/SKILL.md](skills/SKILL.md)。

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [TheSmallHanCat](https://github.com/TheSmallHanCat/flow2api) 原项目
- [PearNoDec](https://github.com/PearNoDec) 提供的 YesCaptcha 打码方案
- [raomaiping](https://github.com/raomaiping) 提供的无头打码方案

感谢所有贡献者和使用者的支持！

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
