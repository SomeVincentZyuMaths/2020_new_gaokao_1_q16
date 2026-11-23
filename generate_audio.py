import os
import subprocess
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+10%"  # 稍微加速 +10%，让口播节奏更加紧凑、生动、不拖沓

# 按语义断句划分的 27 个分镜节奏点 (Cues)，台词与字幕 100% 同文对齐
CUES = [
    # 乐章一 · 题意破题
    {
        "id": 1,
        "chapter": 1,
        "text": "这是2020新高考全国一卷第十六题。",
        "subtitle": "这是 2020 新高考全国 I 卷第 16 题。"
    },
    {
        "id": 2,
        "chapter": 1,
        "text": "如图所示，直四棱柱所有的棱长都是2，底面菱形当中，一个角是60度。",
        "subtitle": "如图所示，直四棱柱所有的棱长都是 2，\n底面菱形当中，一个角是 60°。"
    },
    {
        "id": 3,
        "chapter": 1,
        "text": "也就是说，底面是两个等边三角形拼起来的对称图形。",
        "subtitle": "也就是说，底面是两个等边三角形拼起来的对称图形。"
    },
    {
        "id": 4,
        "chapter": 1,
        "text": "现在有一个以 D1 为球心、根号5为半径的球。",
        "subtitle": "现在有一个以 D₁ 为球心、√5 为半径的球。"
    },
    {
        "id": 5,
        "chapter": 1,
        "text": "题目问你：这个球与侧面 BCC1B1 的交线弧长是多少？",
        "subtitle": "题目问你：这个球与侧面 BCC₁B₁ 的交线弧长是多少？"
    },
    {
        "id": 6,
        "chapter": 1,
        "text": "很显然，题目问的是这个正方形侧面内部截出的弧长，而不是整个截面大圆的周长哈，这里一定要先审清楚！",
        "subtitle": "题目问的是正方形侧面内部截出的弧长，\n而不是整个截面大圆的周长，一定要先审清！"
    },

    # 乐章二 · 顶面俯视与线面垂直证明 (O' 念为 欧一撇)
    {
        "id": 7,
        "chapter": 2,
        "text": "好，我们先专注来看顶面。",
        "subtitle": "好，我们先专注来看顶面。"
    },
    {
        "id": 8,
        "chapter": 2,
        "text": "正如我刚刚所说，连接 B1D1 可以得到两个等边三角形。",
        "subtitle": "正如我刚刚所说，连接 B₁D₁ 可以得到两个等边三角形。"
    },
    {
        "id": 9,
        "chapter": 2,
        "text": "所以很显然，球心 D1 到侧面 BCC1B1 的垂面距离，就是这个等边三角形 B1C1D1 的高！",
        "subtitle": "球心 D₁ 到侧面 BCC₁B₁ 的垂面距离，\n正是等边三角形 B₁C₁D₁ 的高！"
    },
    {
        "id": 10,
        "chapter": 2,
        "text": "垂足我们标记为欧一撇，也就是后续截面圆的圆心。",
        "subtitle": "垂足我们标记为 O'，也就是后续截面圆的圆心。"
    },
    {
        "id": 11,
        "chapter": 2,
        "text": "要严格证明 D1 欧一撇 垂直于侧面也很简单：",
        "subtitle": "要严格证明 D₁O' 垂直于侧面也很简单："
    },
    {
        "id": 12,
        "chapter": 2,
        "text": "首先，在等边三角形中，高线 D1 欧一撇 垂直于底边 B1C1；",
        "subtitle": "首先，在等边三角形中，高线 D₁O' 垂直于底边 B₁C₁；"
    },
    {
        "id": 13,
        "chapter": 2,
        "text": "其次，因为这是直四棱柱，竖直的棱 BB1 垂直于顶面，所以 BB1 这条棱自然垂直于顶面内的直线 D1 欧一撇。",
        "subtitle": "其次，因为直四棱柱竖直棱 BB₁ 垂直顶面，\n所以 BB₁ 自然垂直于顶面内的直线 D₁O'。"
    },
    {
        "id": 14,
        "chapter": 2,
        "text": "根据线面垂直判定定理：D1 欧一撇 垂直于 B1C1，且 D1 欧一撇 垂直于 BB1，两条相交直线都在侧面上，所以线段 D1 欧一撇 垂直于整个侧面 BCC1B1！",
        "subtitle": "D₁O' 垂直于 B₁C₁ 且垂直于 BB₁，\n两条相交线在侧面上，故 D₁O' 垂直于整个侧面！"
    },
    {
        "id": 15,
        "chapter": 2,
        "text": "因此，线段 D1 欧一撇 的长度，正是球心 D1 距离侧面的垂面距离 d。",
        "subtitle": "因此，线段 D₁O' 的长度，正是球心 D₁ 距离侧面的垂面距离 d。"
    },
    {
        "id": 16,
        "chapter": 2,
        "text": "等边三角形边长 C1D1 是 2，所以中点一半 C1 欧一撇 就是 1，勾股定理立刻算出高 d 等于根号3！",
        "subtitle": "等边三角形边长为 2，半边 C₁O' 为 1，\n勾股定理立刻算出高 d = √3！"
    },

    # 乐章三 · 侧面透视与直角勾股 (实装草图右图 B1和C1重合视角)
    {
        "id": 17,
        "chapter": 3,
        "text": "接下来我们把视角切到侧面，让以 D1 为球心的大球穿透侧面。",
        "subtitle": "接下来我们把视角切到侧面，\n让以 D₁ 为球心的大球穿透侧面。"
    },
    {
        "id": 18,
        "chapter": 3,
        "text": "看！我们沿着棱 B1C1 的方向平视过去，侧面压成了一条垂线！球心 D1 到侧面的垂距 d，就是水平这条高线根号3；球半径 R 是斜边根号5！",
        "subtitle": "沿 B₁C₁ 平视侧面压成垂线！\n水平垂距 d = √3，斜边球半径 R = √5！"
    },
    {
        "id": 19,
        "chapter": 3,
        "text": "这构成了一个极其标准的直角三角形！根据球截面的勾股定理，竖直方向的截面圆半径小 r，就等于根号下大 R 方减去 d 方，也就是根号下 5 减 3，立刻算出截面圆半径 r 等于根号2！",
        "subtitle": "标准直角三角形勾股秒杀：\n截面圆半径 r = √(R² - d²) = √(5 - 3) = √2！"
    },

    # 乐章四 · 正方形降维秒杀与弧长终解
    {
        "id": 20,
        "chapter": 4,
        "text": "好，最后我们彻底降维，正视这个边长为 2 的正方形侧面。",
        "subtitle": "好，最后我们彻底降维，正视这个边长为 2 的正方形侧面。"
    },
    {
        "id": 21,
        "chapter": 4,
        "text": "欧一撇是中点，两边截出的两个小角都是边长为 1 的等腰直角三角形，左右各切掉了 45 度角！",
        "subtitle": "O' 为中点，两边截出的都是边长为 1 的等腰直角三角形，\n左右各切掉了 45° 切角！"
    },
    {
        "id": 22,
        "chapter": 4,
        "text": "整个图形是左右严格对称的，所以中间交线弧所对应的圆心角，正好就是 180 度减去两个 45 度，也就是直角 90 度，对应二分之派！",
        "subtitle": "图形左右严格对称，中间弧所对圆心角，\n正好是 180° - 45° - 45° = 90°，对应 π/2！"
    },
    {
        "id": 23,
        "chapter": 4,
        "text": "根据弧长公式：弧长等于圆心角乘以截面圆半径，二分之派乘以根号 2，最终答案就是——二分之根号二 派！",
        "subtitle": "弧长公式：l = θ · r = (π/2) · √2，\n最终答案就是——(√2/2)π！"
    },

    # 乐章五 · 终章 3D 全景回归与五步极速秒杀复盘
    {
        "id": 24,
        "chapter": 5,
        "text": "最后我们回归三维立体空间，来完整回顾这道高考压轴题的极速五步法！",
        "subtitle": "回归三维立体空间，完整回顾极速五步法！"
    },
    {
        "id": 25,
        "chapter": 5,
        "text": "第一步，顶面等边三角形算出垂面距离 d 等于根号3；第二步，侧视投影直角三角形勾股算出截面半径 r 等于根号2；",
        "subtitle": "① 顶面等边三角形算垂距 d = √3；\n② 侧面直角三角形勾股算截面半径 r = √2；"
    },
    {
        "id": 26,
        "chapter": 5,
        "text": "第三步，正方形两边各切 45 度；第四步，得出截面圆心角 90 度；第五步，弧长公式一锤定音！",
        "subtitle": "③ 左右各切 45°；④ 圆心角 θ = 90° = π/2；\n⑤ 弧长 l = θ · r = (√2/2)π 一锤定音！"
    },
    {
        "id": 27,
        "chapter": 5,
        "text": "掌握空间几何的降维透视思想，复杂高考难题也能三分钟极速搞定！",
        "subtitle": "掌握空间几何降维透视思想，复杂高考难题轻松搞定！"
    }
]

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(res.stdout.strip())

def main():
    print(f"🎙️ 开始为全部 27 个分镜节点逐句生成音频与精准对齐数据...")
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

    edge_tts_exe = r"D:\TMP\manim\20261027manim立体几何高考捏\.venv\Scripts\edge-tts.exe"
    
    total_timeline = []
    current_time = 0.0

    concat_list_file = os.path.join(AUDIO_DIR, "cues_concat.txt")
    with open(concat_list_file, "w", encoding="utf-8") as concat_f:
        for cue in CUES:
            cid = cue["id"]
            mp3_name = f"cue_{cid:02d}.mp3"
            mp3_path = os.path.join(AUDIO_DIR, mp3_name)
            
            # 由于更新了台词（欧一撇、侧视、复盘），重新生成单句音频
            print(f"🎙️ 正在生成 Cue {cid:02d} 音频...")
            cmd = [
                edge_tts_exe,
                "--text", cue["text"],
                "--voice", VOICE,
                "--rate", RATE,
                "--write-media", mp3_path
            ]
            subprocess.run(cmd, check=True)
            
            dur = get_audio_duration(mp3_path)
            start_t = current_time
            end_t = current_time + dur
            current_time = end_t
            
            cue_info = {
                "id": cid,
                "chapter": cue["chapter"],
                "text": cue["text"],
                "subtitle": cue["subtitle"],
                "file": mp3_name,
                "duration": round(dur, 3),
                "start_time": round(start_t, 3),
                "end_time": round(end_t, 3)
            }
            total_timeline.append(cue_info)
            print(f"  [Cue {cid:02d}] 时长: {dur:.3f}s | {cue['text'][:25]}...")
            
            escaped_path = mp3_path.replace("\\", "/")
            concat_f.write(f"file '{escaped_path}'\n")

    # 导出 cues.json
    cues_json_path = os.path.join(AUDIO_DIR, "cues.json")
    with open(cues_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration": round(current_time, 3),
            "voice": VOICE,
            "rate": RATE,
            "cues": total_timeline
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ cues.json 已更新: {cues_json_path} (总时长: {current_time:.3f}s)")

    # 使用 ffmpeg 无缝拼接为一条完整的 all.mp3
    all_mp3_path = os.path.join(AUDIO_DIR, "all.mp3")
    cmd_merge = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        all_mp3_path
    ]
    subprocess.run(cmd_merge, check=True)
    total_audio_dur = get_audio_duration(all_mp3_path)
    print(f"🎉 全篇无缝拼接音频 all.mp3 已生成: {all_mp3_path} (测量总时长: {total_audio_dur:.3f}s)")

if __name__ == "__main__":
    main()
