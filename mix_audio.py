import os
import sys
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
CUES_PATH = os.path.join(AUDIO_DIR, "cues.json")
AUDIO_PATH = os.path.join(AUDIO_DIR, "all.mp3")

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass(font_name, out_path, font_size=42):
    with open(CUES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    header = f"""[Script Info]
Title: Scene5 Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00141414,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1.5,2,40,40,42,1
Style: Highlight,{font_name},{font_size + 2},&H0000D7FF,&H000000FF,&H000A0A0A,&H80000000,-1,0,0,0,100,100,0,0,1,3.0,1.8,2,40,40,42,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    highlight_ids = {14, 16, 18, 19, 22, 23, 26}
    lines = [header]
    for c in data["cues"]:
        t_start = format_ass_time(c["start_time"])
        t_end = format_ass_time(c["end_time"])
        style = "Highlight" if c["id"] in highlight_ids else "Default"
        sub_text = c["subtitle"].replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{t_start},{t_end},{style},,0,0,0,,{sub_text}\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ 已成功生成字幕文件: {out_path} (字体: {font_name})")

def burn_subtitles_and_mux(video_path, ass_path, out_video_path, use_fonts_dir=True):
    rel_ass_path = os.path.relpath(ass_path, BASE_DIR).replace("\\", "/")
    
    if use_fonts_dir and os.path.exists(FONTS_DIR):
        rel_fonts_dir = os.path.relpath(FONTS_DIR, BASE_DIR).replace("\\", "/")
        vf_filter = f"ass={rel_ass_path}:fontsdir={rel_fonts_dir}"
    else:
        vf_filter = f"ass={rel_ass_path}"

    print(f"🎬 正在混流成片: {out_video_path}...")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", AUDIO_PATH,
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_video_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"🎉 混流成功！成片已生成: {out_video_path}")
    else:
        print(f"❌ 混流失败:\n{res.stderr}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        video_path = sys.argv[1]
    else:
        # 寻找最新的 1080p 视频 (Scene6 优先)
        video_candidates = [
            os.path.join(BASE_DIR, "media", "videos", "scene6", "1080p60", "Scene6.mp4"),
            os.path.join(BASE_DIR, "media", "videos", "scene6", "480p15", "Scene6.mp4"),
            os.path.join(BASE_DIR, "media", "videos", "scene5", "1080p60", "Scene5.mp4"),
        ]
        existing = [p for p in video_candidates if os.path.exists(p)]
        if not existing:
            print("❌ 未找到渲染好的视频")
            exit(1)
        existing.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        video_path = existing[0]

    print(f"🎯 检测到最新视频源: {video_path}")

    # 本次任务：只生成高清霞鹜文楷专属成片 Scene6_final.mp4
    ass_lxgw = os.path.join(AUDIO_DIR, "subtitles_lxgw.ass")
    generate_ass("LXGW WenKai", ass_lxgw, font_size=44)
    out_final = os.path.join(BASE_DIR, "Scene6_final.mp4")
    burn_subtitles_and_mux(video_path, ass_lxgw, out_final, use_fonts_dir=True)
