# 2020年新高考I卷 第16题 · 球截侧面圆弧交线长 Manim 3D 动画

> **原题题干**：直四棱柱 $ABCD-A_1B_1C_1D_1$ 的棱长均为 2，$\angle BAD=60^\circ$。以 $D_1$ 为球心，$\sqrt{5}$ 为半径的球面与侧面 $BCC_1B_1$ 的交线长为____。  
> **参考答案**：$\dfrac{\sqrt{2}}{2}\pi$

---

## 📁 目录文件结构

- `scene.py`：Manim 3D 第一代动画源码
- `scene2.py`：第二代多视角透视动画源码
- `scene3.py`：第三代高精细度 5 乐章极速推导动画源码
- `scene4.py`：**全新第四代 · 微软 Edge-TTS 晓晓原声口播协同与动态内嵌字幕成片动画源码**
- `tts.md`：校正后的口播讲解四乐章台词稿
- `generate_audio.py`：Edge-TTS 异步配音生成与音频对齐测量脚本
- `mix_audio.py`：视频与音频自动对齐混流脚本
- `audio/`：生成的各乐章高音质音频分轨及 `all.mp3`、`meta.json`
- `Scene4_final.mp4`：**已混流完毕的最终音视频带字幕完整成片**
- `media/videos/scene4/`：Manim 纯视频帧产物目录

---

## 🚀 渲染与成片导出指令 (基于 uv)

在当前子目录 `D:\TMP\manim\20261027manim立体几何高考捏\2020_new_gaokao_1_q16` 下执行：

```powershell
# 1. 重新生成/微调配音 (如果修改了台词)
..\.venv\Scripts\python.exe generate_audio.py

# 2. 渲染 Manim 动画
# 2.1 快速低清预览 (480p 15fps)
..\.venv\Scripts\manim.exe -ql scene4.py Scene4

# 2.2 720p 高清渲染 (720p 30fps)
..\.venv\Scripts\manim.exe -qm scene4.py Scene4

# 2.3 1080p 60fps 超清成片导出 (发 B站/小红书/抖音)
..\.venv\Scripts\manim.exe -qh scene4.py Scene4

# 3. 一键混流晓晓配音 (自动输出 Scene4_final.mp4)
..\.venv\Scripts\python.exe mix_audio.py
```

---

## 📦 仓库说明

`.gitignore` 排除了两类大体积目录，克隆后需要自行补齐才能重新渲染：

- `media/`：Manim 渲染中间产物，用上面的命令重新生成即可。
- `fonts/`：开源字体霞鹜文楷 LXGW WenKai（约 145 MB），从 <https://github.com/lxgw/LxgwWenKai/releases> 下载后放到 `fonts/` 目录。

根目录下的 `Scene*_final.mp4` 是已混流配音的最终成片，已随仓库一起提交。
