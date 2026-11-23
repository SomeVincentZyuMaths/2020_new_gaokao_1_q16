from manim import *
import numpy as np
import manimpango
import json
import os
import gc

# 注册霞鹜文楷字体
manimpango.register_font(r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Regular.ttf")
manimpango.register_font(r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Medium.ttf")
FONT_REGULAR = "LXGW WenKai"

# 彻底关闭分段缓存哈希，根除 deepcopy 与 hashing 引起的内存累积与 MemoryError
config.disable_caching = True

class Scene6(ThreeDScene):
    def construct(self):
        # =========================================================================
        # 0. 读取 27 个精准分镜音频时间戳元数据
        # =========================================================================
        cues_path = os.path.join(os.path.dirname(__file__), "audio", "cues.json")
        with open(cues_path, "r", encoding="utf-8") as f:
            cues_data = json.load(f)
        cues = cues_data["cues"]

        # =========================================================================
        # 1. 几何核心坐标系统 (棱长均为 2)
        # =========================================================================
        SQRT3 = np.sqrt(3)
        SQRT2 = np.sqrt(2)
        SQRT5 = np.sqrt(5)

        # 底面菱形顶点 (z = -1)
        A = np.array([-SQRT3, 0.0, -1.0])
        B = np.array([0.0, -1.0, -1.0])
        C = np.array([SQRT3, 0.0, -1.0])
        D = np.array([0.0, 1.0, -1.0])

        # 顶面菱形顶点 (z = +1)
        A1 = np.array([-SQRT3, 0.0, 1.0])
        B1 = np.array([0.0, -1.0, 1.0])
        C1 = np.array([SQRT3, 0.0, 1.0])
        D1 = np.array([0.0, 1.0, 1.0])

        # 关键几何点
        O_prime = np.array([SQRT3 / 2, -0.5, 1.0])        # B1C1 中点 (垂足兼截面圆心)
        O_bottom = np.array([SQRT3 / 2, -0.5, -1.0])      # BC 中点
        E = np.array([0.0, -1.0, 0.0])                    # BB1 中点 (圆截侧棱交点)
        F = np.array([SQRT3, 0.0, 0.0])                   # CC1 中点 (圆截侧棱交点)

        R_sphere = SQRT5
        d_perp = SQRT3
        r_circle = SQRT2

        u_vec = (C1 - B1) / np.linalg.norm(C1 - B1)
        v_vec = np.array([0.0, 0.0, -1.0])

        # 初始相机：开场原距全景 (zoom=1.0)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES, zoom=1.0)

        # =========================================================================
        # 2. 常驻 HUD 标题与动态分镜节拍器
        # =========================================================================
        title_group = VGroup(
            Text("2020年新高考I卷 · 第16题 · 立体几何极速解密", font=FONT_REGULAR, font_size=21, weight=BOLD, color=YELLOW_B),
            Text("直四棱柱棱长为 2，底角 60°，以 D₁ 为球心，R = √5", font=FONT_REGULAR, font_size=15, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UL, buff=0.35)
        self.add_fixed_in_frame_mobjects(title_group)

        # 核心分镜节拍器：严格按音频时长精确走满时间（毫秒级对齐晓晓配音）
        def play_cue(cue_id, *anims, highlight=False, anim_duration=None, camera_target=None):
            cue = cues[cue_id - 1]
            total_dur = cue["duration"]

            if anims or camera_target:
                if anim_duration is not None:
                    act_time = min(total_dur * 0.85, anim_duration)
                else:
                    act_time = min(total_dur * 0.65, 2.2)
                
                if camera_target:
                    self.move_camera(added_anims=list(anims), run_time=act_time, **camera_target)
                else:
                    self.play(*anims, run_time=act_time)
                
                left_wait = max(0.05, total_dur - act_time)
                self.wait(left_wait)
            else:
                self.wait(max(0.1, total_dur))

        # 右上角五步秒杀卡片系统
        def create_step_card(active_steps=[]):
            steps_data = [
                ("① 垂面距离", "d = D₁O' = √3"),
                ("② 截面半径", "r = √(R²-d²) = √2"),
                ("③ 左右切角", "等腰直角 △ ⇒ 45°"),
                ("④ 核心圆心角", "θ = 180°-2×45° = 90° = π/2"),
                ("⑤ 弧长终解", "l = θ·r = (√2/2)π")
            ]
            lines = []
            for idx, (title, formula) in enumerate(steps_data, 1):
                is_active = idx in active_steps
                col_t = GOLD_A if is_active else GRAY_B
                col_f = YELLOW if is_active else GRAY_C
                prefix = "▶ " if is_active else "  "
                t_obj = Text(f"{prefix}{title}: ", font=FONT_REGULAR, font_size=13, color=col_t, weight=BOLD if is_active else NORMAL)
                f_obj = Text(formula, font=FONT_REGULAR, font_size=13, color=col_f)
                lines.append(VGroup(t_obj, f_obj).arrange(RIGHT, buff=0.08))

            card_content = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            card_title = Text("五步极速推导", font=FONT_REGULAR, font_size=14, color=GOLD_B, weight=BOLD)
            full_box_content = VGroup(card_title, Line(LEFT, RIGHT, color=GOLD_E, stroke_width=0.8).set_width(card_content.width), card_content).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            bg = SurroundingRectangle(full_box_content, buff=0.14, color=GOLD_C if active_steps else GRAY_D, fill_color=BLACK, fill_opacity=0.85, corner_radius=0.12)
            bg.set_stroke(width=1.2)
            return VGroup(bg, full_box_content).to_corner(UR, buff=0.35)

        def make_billboard_label(text, point, offset=np.array([0, 0, 0]), font_size=16, col=WHITE):
            t = Text(text, font=FONT_REGULAR, font_size=font_size, color=col)
            t.move_to(point + offset)
            return t

        # =========================================================================
        # 3. 第一乐章 · 题意破题与空间构想 (Cues 1 ~ 6) 保持宏观全景 zoom=1.0
        # =========================================================================
        self.begin_ambient_camera_rotation(rate=0.035)

        # Cue 1: 题目前言 (3.86s) - 开场标题平滑淡入，严格毫秒对齐音频起始点
        play_cue(1, FadeIn(title_group), highlight=True, anim_duration=1.2)

        # 直四棱柱线框建模
        EDGE_THICKNESS = 0.013
        edge_B_C = Line3D(B, C, color=BLUE_B, thickness=EDGE_THICKNESS)
        edge_C_C1 = Line3D(C, C1, color=BLUE_C, thickness=EDGE_THICKNESS)
        edge_C1_B1 = Line3D(C1, B1, color=BLUE_B, thickness=EDGE_THICKNESS)
        edge_B1_B = Line3D(B1, B, color=BLUE_C, thickness=EDGE_THICKNESS)
        side_edges = VGroup(edge_B_C, edge_C_C1, edge_C1_B1, edge_B1_B)

        other_edges = VGroup(
            Line3D(A, B, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A, D, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C, D, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A1, B1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A1, D1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C1, D1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A, A1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(D, D1, color=BLUE_B, thickness=EDGE_THICKNESS)
        )
        all_prism_edges = VGroup(side_edges, other_edges)

        lbl_A = make_billboard_label("A", A, np.array([-0.3, -0.3, 0]), col=GRAY_A)
        lbl_B = make_billboard_label("B", B, np.array([0, -0.35, 0]), col=YELLOW_B)
        lbl_C = make_billboard_label("C", C, np.array([0.3, -0.3, 0]), col=YELLOW_B)
        lbl_D = make_billboard_label("D", D, np.array([0, 0.35, 0]), col=GRAY_A)
        lbl_A1 = make_billboard_label("A₁", A1, np.array([-0.3, 0.3, 0]), col=GRAY_A)
        lbl_B1 = make_billboard_label("B₁", B1, np.array([0, -0.35, 0]), col=YELLOW_B)
        lbl_C1 = make_billboard_label("C₁", C1, np.array([0.3, -0.3, 0]), col=YELLOW_B)
        lbl_D1 = make_billboard_label("D₁(球心)", D1, np.array([0, 0.35, 0]), col=GOLD_A)
        v0_labels_list = [lbl_A, lbl_B, lbl_C, lbl_D, lbl_A1, lbl_B1, lbl_C1, lbl_D1]

        # Cue 2: 直四棱柱与底角60度 (6.48s)
        self.add_fixed_orientation_mobjects(*v0_labels_list)
        play_cue(2, Create(all_prism_edges), anim_duration=3.0)

        # Cue 3: 两个等边三角形拼合 (4.80s)
        diag_bd = Line3D(B, D, color=GOLD_B, thickness=0.018)
        diag_b1d1_top = Line3D(B1, D1, color=GOLD_B, thickness=0.018)
        play_cue(3, Create(diag_bd), Create(diag_b1d1_top), anim_duration=2.2)

        # Cue 4: 球心与大球构造 (3.98s)
        sphere = Sphere(
            center=D1, radius=R_sphere, resolution=(16, 16),
            fill_color=TEAL_C, fill_opacity=0.14, stroke_color=TEAL_A, stroke_width=0.3, stroke_opacity=0.2
        )
        play_cue(4, Create(sphere), anim_duration=2.0)

        # Cue 5: 截面圆弧初现 (5.54s)
        full_thetas = np.linspace(0, 360 * DEGREES, 72)
        full_pts = [O_prime + r_circle * np.cos(th) * u_vec + r_circle * np.sin(th) * v_vec for th in full_thetas]
        full_circle_mobj = VMobject(color=YELLOW_C, stroke_width=1.8)
        full_circle_mobj.set_points_smoothly(full_pts)

        thetas_arc = np.linspace(45 * DEGREES, 135 * DEGREES, 40)
        arc_pts = [O_prime + r_circle * np.cos(th) * u_vec + r_circle * np.sin(th) * v_vec for th in thetas_arc]
        golden_arc = VMobject(color=GOLD_A, stroke_width=5.5)
        golden_arc.set_points_smoothly(arc_pts)
        play_cue(5, Create(full_circle_mobj), anim_duration=2.5)

        # Cue 6: 细节1·正方形内弧长强调，消散外部圆 (9.14s)
        play_cue(
            6,
            Create(golden_arc),
            full_circle_mobj.animate.set_stroke(opacity=0.0, width=0.1),
            sphere.animate.set_opacity(0.0),
            Flash(O_prime, color=GOLD, flash_radius=0.45),
            highlight=True,
            anim_duration=3.2
        )
        self.remove(full_circle_mobj, sphere)
        del full_circle_mobj, sphere
        gc.collect()

        self.stop_ambient_camera_rotation()

        # =========================================================================
        # 4. 第二乐章 · 顶面俯视与线面垂直证明 (Cues 7 ~ 16)
        # 电影级运镜①：从全景平滑升起俯冲推近至 zoom=1.45，焦点锁定顶面
        # 核心投影合并：底面 A,B,C,D 动画融合至顶面 B₁(B), C₁(C), D₁(D)·球心，彻底避免重叠与双球心！
        # =========================================================================
        # Cue 7: 视角切换拉升 + 镜头推近 + 投影标记合并动画 (2.66s)
        lbl_B1_proj = make_billboard_label("B₁(B)", B1, np.array([-0.45, -0.28, 0]), font_size=15, col=YELLOW_B)
        lbl_C1_proj = make_billboard_label("C₁(C)", C1, np.array([0.45, -0.28, 0]), font_size=15, col=YELLOW_B)
        lbl_A1_proj = make_billboard_label("A₁(A)", A1, np.array([-0.45, 0.28, 0]), font_size=15, col=GRAY_A)
        lbl_D1_proj = make_billboard_label("D₁(D) · 球心", D1, np.array([0.25, 0.42, 0]), font_size=15, col=GOLD_A)
        v1_proj_labels = [lbl_A1_proj, lbl_B1_proj, lbl_C1_proj, lbl_D1_proj]
        self.add_fixed_orientation_mobjects(*v1_proj_labels)

        play_cue(
            7,
            FadeOut(diag_bd),
            ReplacementTransform(lbl_B1, lbl_B1_proj),
            FadeOut(lbl_B),
            ReplacementTransform(lbl_C1, lbl_C1_proj),
            FadeOut(lbl_C),
            ReplacementTransform(lbl_A1, lbl_A1_proj),
            FadeOut(lbl_A),
            ReplacementTransform(lbl_D1, lbl_D1_proj),
            FadeOut(lbl_D),
            camera_target=dict(
                phi=3 * DEGREES,
                theta=-45 * DEGREES,
                zoom=1.45
            ),
            highlight=True,
            anim_duration=2.2
        )
        self.remove_fixed_orientation_mobjects(*v0_labels_list)
        self.remove(diag_bd, *v0_labels_list)

        # Cue 8: 等边三角形连线 (5.02s)
        tri_b1c1d1 = VGroup(
            Line3D(B1, C1, color=YELLOW, thickness=0.02),
            Line3D(C1, D1, color=YELLOW, thickness=0.02),
            Line3D(D1, B1, color=YELLOW, thickness=0.02)
        )
        play_cue(8, Create(tri_b1c1d1), anim_duration=2.5)

        # Cue 9: 垂面距离即高线 (8.23s)
        line_d1_op = Line3D(D1, O_prime, color=RED_A, thickness=0.024)
        dot_op = Dot3D(O_prime, radius=0.06, color=RED)
        lbl_h_val = make_billboard_label("高线 d = √3", (D1 + O_prime) / 2, np.array([0.42, 0.12, 0]), font_size=15, col=RED_B)
        lbl_op_foot = make_billboard_label("O'(垂足·圆心)", O_prime, np.array([0.0, -0.42, 0]), font_size=15, col=RED_A)
        self.add_fixed_orientation_mobjects(lbl_h_val, lbl_op_foot)
        play_cue(9, Create(line_d1_op), Create(dot_op), FadeIn(lbl_op_foot), anim_duration=3.0)

        # Cue 10: 垂足O'也是圆心 (4.66s，念为“欧一撇”)
        play_cue(10, Flash(O_prime, color=RED, flash_radius=0.4), anim_duration=1.5)

        # Cue 11: 证明准备 (4.44s)
        play_cue(11, anim_duration=1.0)

        # Cue 12: 直角折角符号 + 判定1 (6.12s)
        elbow_size = 0.18
        v_c1_b1 = (B1 - C1) / np.linalg.norm(B1 - C1)
        v_op_d1 = (D1 - O_prime) / np.linalg.norm(D1 - O_prime)
        elbow_p1 = O_prime + elbow_size * v_c1_b1
        elbow_p2 = elbow_p1 + elbow_size * v_op_d1
        elbow_p3 = O_prime + elbow_size * v_op_d1
        elbow_top = Line(elbow_p1, elbow_p2, color=RED_C, stroke_width=2.5)
        elbow_top2 = Line(elbow_p2, elbow_p3, color=RED_C, stroke_width=2.5)
        elbow_group = VGroup(elbow_top, elbow_top2)
        play_cue(12, Create(elbow_group), anim_duration=2.0)

        # Cue 13: 竖直棱垂直顶面 (10.01s)
        proof_card = VGroup(
            Text("线面垂直严谨判定：", font=FONT_REGULAR, font_size=14, color=GOLD_A, weight=BOLD),
            Text("① D₁O' ⊥ B₁C₁ (等边三角形高线)", font=FONT_REGULAR, font_size=13, color=WHITE),
            Text("② BB₁ ⊥ 顶面 ⇒ BB₁ ⊥ D₁O'", font=FONT_REGULAR, font_size=13, color=WHITE),
            Text("③ B₁C₁ ∩ BB₁ = B₁", font=FONT_REGULAR, font_size=13, color=GRAY_B),
            Text("∴ D₁O' ⊥ 侧面 BCC₁B₁！", font=FONT_REGULAR, font_size=14, color=YELLOW, weight=BOLD)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        bg_proof = SurroundingRectangle(proof_card, buff=0.12, color=BLUE_D, fill_color=BLACK, fill_opacity=0.82, corner_radius=0.1)
        proof_panel = VGroup(bg_proof, proof_card).to_corner(DL, buff=0.35)
        self.add_fixed_in_frame_mobjects(proof_panel)
        play_cue(13, anim_duration=2.5)

        # Cue 14: 两相交线得出垂直结论 (14.52s)
        play_cue(14, highlight=True, anim_duration=2.5)

        # Cue 15: 垂距概念明确 (6.55s)
        play_cue(15, line_d1_op.animate.set_color(GOLD).set_stroke(width=0.035), anim_duration=2.2)

        # Cue 16: 勾股算出高 d = √3 + 弹出步骤① (8.98s)
        lbl_c1_len = make_billboard_label("半棱长 = 1", (O_prime + C1) / 2, np.array([0, -0.32, 0]), font_size=14, col=YELLOW_D)
        self.add_fixed_orientation_mobjects(lbl_c1_len)
        card_step1 = create_step_card(active_steps=[1])
        self.add_fixed_in_frame_mobjects(card_step1)
        play_cue(16, FadeIn(lbl_c1_len), highlight=True, anim_duration=2.5)

        # 彻底清理第二乐章的所有专属标签与对象，杜绝红点dot残留
        self.remove_fixed_in_frame_mobjects(card_step1, proof_panel)
        self.remove_fixed_orientation_mobjects(lbl_c1_len, lbl_h_val, lbl_op_foot, *v1_proj_labels)
        self.remove(card_step1, proof_panel, lbl_c1_len, lbl_h_val, lbl_op_foot, elbow_group, dot_op, tri_b1c1d1, *v1_proj_labels)
        del card_step1, proof_panel
        gc.collect()

        # =========================================================================
        # 5. 第三乐章 · 侧面透视与手绘草图右图“棱重合直角勾股” (Cues 17 ~ 19)
        # 视线平行于 B1C1 (phi=90°, theta=-150°)，B1与C1重合，呈现纯平面直角三角形
        # =========================================================================
        # Cue 17: 运镜切向侧面 + 大球隐现穿透 (5.81s)
        sphere_replay = Sphere(
            center=D1, radius=R_sphere, resolution=(16, 16),
            fill_color=TEAL_C, fill_opacity=0.18, stroke_color=TEAL_A, stroke_width=0.4, stroke_opacity=0.25
        )
        play_cue(
            17,
            FadeIn(sphere_replay),
            camera_target=dict(
                phi=74 * DEGREES,
                theta=-78 * DEGREES,
                zoom=1.40
            ),
            anim_duration=2.2
        )
        self.remove(sphere_replay)
        del sphere_replay
        gc.collect()

        # Cue 18: 核心神级运镜！视线沿 B1C1 平视过去 (phi=90°, theta=-150°)
        # 此时 B1 与 C1 完美重合，侧面压成垂线，呈现草图右图纯直角三角形！(13.13s)
        pt_M = O_prime + r_circle * v_vec  # 截面圆弧交点 (位于 O' 正下方 r=√2 处)
        line_R_hypot = Line3D(D1, pt_M, color=TEAL_A, thickness=0.024)
        line_r_leg = Line3D(O_prime, pt_M, color=YELLOW_A, thickness=0.024)

        # 直角折角符号 (在草图右图直角顶点 O' 处)
        elbow_sz = 0.16
        eb_p1 = O_prime + elbow_sz * np.array([0, 0, -1])
        eb_p2 = eb_p1 + elbow_sz * v_op_d1
        eb_p3 = O_prime + elbow_sz * v_op_d1
        elbow_rt = VGroup(
            Line(eb_p1, eb_p2, color=RED_C, stroke_width=2.5),
            Line(eb_p2, eb_p3, color=RED_C, stroke_width=2.5)
        )

        v2_side_labels = VGroup(
            make_billboard_label("D₁(球心)", D1, np.array([-0.35, 0.25, 0]), font_size=15, col=GOLD_A),
            make_billboard_label("C₁(B₁)", O_prime, np.array([0.45, 0.25, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("C(B)", O_bottom, np.array([0.45, -0.25, 0]), font_size=14, col=GRAY_A),
            make_billboard_label("d = √3", (D1 + O_prime) / 2, np.array([0, 0.28, 0]), font_size=15, col=RED_B),
            make_billboard_label("R = √5", (D1 + pt_M) / 2, np.array([-0.3, -0.2, 0]), font_size=15, col=TEAL_A),
            make_billboard_label("r = √2", (O_prime + pt_M) / 2, np.array([0.35, 0, 0]), font_size=15, col=YELLOW_A)
        )
        self.add_fixed_orientation_mobjects(*v2_side_labels)

        play_cue(
            18,
            Create(line_R_hypot),
            Create(line_r_leg),
            Create(elbow_rt),
            camera_target=dict(
                phi=90 * DEGREES,
                theta=-150 * DEGREES,
                zoom=1.65
            ),
            anim_duration=3.5
        )

        # Cue 19: 直角三角形勾股秒杀 r = √2 + 弹出步骤② (15.34s)
        card_step2 = create_step_card(active_steps=[2])
        self.add_fixed_in_frame_mobjects(card_step2)
        play_cue(
            19,
            Flash(pt_M, color=YELLOW, flash_radius=0.4),
            line_r_leg.animate.set_color(GOLD).set_stroke(width=0.035),
            highlight=True,
            anim_duration=3.5
        )
        self.remove_fixed_in_frame_mobjects(card_step2)
        self.remove_fixed_orientation_mobjects(*v2_side_labels)
        self.remove(card_step2, line_R_hypot, line_r_leg, elbow_rt, *v2_side_labels, other_edges, line_d1_op, tri_b1c1d1, diag_b1d1_top)
        del card_step2
        gc.collect()

        # =========================================================================
        # 6. 第四乐章 · 正方形降维秒杀与弧长终解 (Cues 20 ~ 23)
        # 电影级运镜②：正视正方形，深推放大至 zoom=1.85，占屏幕 70%！
        # =========================================================================
        # Cue 20: 正视正方形，彻底降维 (5.18s)
        v3_labels = VGroup(
            make_billboard_label("B₁", B1, np.array([-0.3, 0.22, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("C₁", C1, np.array([0.3, 0.22, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("B", B, np.array([-0.3, -0.22, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("C", C, np.array([0.3, -0.22, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("O'(圆心)", O_prime, np.array([0, 0.25, 0]), font_size=15, col=RED_A)
        )
        self.add_fixed_orientation_mobjects(*v3_labels)
        play_cue(
            20,
            FadeIn(v3_labels),
            camera_target=dict(
                phi=90 * DEGREES,
                theta=-90 * DEGREES,
                zoom=1.85
            ),
            highlight=True,
            anim_duration=2.5
        )

        # Cue 21: 左右 45° 切角 (8.16s)
        line_op_e = Line3D(O_prime, E, color=YELLOW_C, thickness=0.018)
        line_op_f = Line3D(O_prime, F, color=YELLOW_C, thickness=0.018)
        lbl_45_l = make_billboard_label("45°", O_prime + u_vec * (-0.45) + v_vec * 0.15, font_size=14, col=GOLD_A)
        lbl_45_r = make_billboard_label("45°", O_prime + u_vec * 0.45 + v_vec * 0.15, font_size=14, col=GOLD_A)
        self.add_fixed_orientation_mobjects(lbl_45_l, lbl_45_r)
        play_cue(21, Create(line_op_e), Create(line_op_f), anim_duration=3.0)

        # Cue 22: 圆心角 90° = π/2 (11.62s)
        arc_90_pts = [O_prime + 0.35 * np.cos(th) * u_vec + 0.35 * np.sin(th) * v_vec for th in thetas_arc]
        arc_90_mobj = VMobject(color=GOLD_A, stroke_width=2.5)
        arc_90_mobj.set_points_smoothly(arc_90_pts)
        lbl_90_deg = make_billboard_label("90° (π/2)", O_prime + v_vec * 0.45, font_size=15, col=GOLD_B)
        self.add_fixed_orientation_mobjects(lbl_90_deg)
        play_cue(22, Create(arc_90_mobj), highlight=True, anim_duration=2.8)

        # Cue 23: 弧长终解秒杀 (9.77s)
        play_cue(
            23,
            golden_arc.animate.set_stroke(width=8.0, color=GOLD),
            Flash(O_prime + v_vec * SQRT2, color=GOLD),
            highlight=True,
            anim_duration=3.0
        )

        # =========================================================================
        # 7. 第五乐章 · 终章 3D 全景回归与五步极速秒杀复盘 (Cues 24 ~ 27)
        # =========================================================================
        # Cue 24: 回归 3D 黄金全景 (6.29s) - 平滑隐退正方形2D平面辅助标记，还原本体
        other_edges_reborn = VGroup(
            Line3D(A, B, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A, D, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C, D, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A1, B1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A1, D1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C1, D1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A, A1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(D, D1, color=BLUE_B, thickness=EDGE_THICKNESS)
        )
        # 终章震撼全景构建：半透明大球体重现 + 全套 8 顶点高清标注 + 高线 D1O'
        sphere_final = Sphere(
            center=D1, radius=R_sphere, resolution=(18, 18),
            fill_color=TEAL_C, fill_opacity=0.16, stroke_color=TEAL_A, stroke_width=0.35, stroke_opacity=0.25
        )
        line_final_d1_op = Line3D(D1, O_prime, color=RED_A, thickness=0.022)

        lbl_final_A = make_billboard_label("A", A, np.array([-0.3, -0.3, 0]), col=GRAY_A)
        lbl_final_B = make_billboard_label("B", B, np.array([0, -0.35, 0]), col=YELLOW_B)
        lbl_final_C = make_billboard_label("C", C, np.array([0.3, -0.3, 0]), col=YELLOW_B)
        lbl_final_D = make_billboard_label("D", D, np.array([0, 0.35, 0]), col=GRAY_A)
        lbl_final_A1 = make_billboard_label("A₁", A1, np.array([-0.3, 0.3, 0]), col=GRAY_A)
        lbl_final_B1 = make_billboard_label("B₁", B1, np.array([0, -0.35, 0]), col=YELLOW_B)
        lbl_final_C1 = make_billboard_label("C₁", C1, np.array([0.3, -0.3, 0]), col=YELLOW_B)
        lbl_final_D1 = make_billboard_label("D₁(球心)", D1, np.array([0, 0.38, 0]), col=GOLD_A)
        lbl_final_Op = make_billboard_label("O'", O_prime, np.array([0, -0.35, 0]), col=RED_A)
        v_final_labels = [
            lbl_final_A, lbl_final_B, lbl_final_C, lbl_final_D,
            lbl_final_A1, lbl_final_B1, lbl_final_C1, lbl_final_D1,
            lbl_final_Op
        ]
        self.add_fixed_orientation_mobjects(*v_final_labels)

        # 终极 2D HUD 卡片：永远保持在 fixed_in_frame 中，绝对杜绝被 3D 相机旋转导致倾斜
        steps_data = [
            ("① 垂面距离", "d = D₁O' = √3"),
            ("② 截面半径", "r = √(R²-d²) = √2"),
            ("③ 左右切角", "等腰直角 △ ⇒ 45°"),
            ("④ 核心圆心角", "θ = 180°-2×45° = 90° = π/2"),
            ("⑤ 弧长终解", "l = θ·r = (√2/2)π")
        ]
        card_step_lines = []
        for idx, (title, formula) in enumerate(steps_data, 1):
            t_obj = Text(f"▶ {title}: ", font=FONT_REGULAR, font_size=13, color=GRAY_B)
            f_obj = Text(formula, font=FONT_REGULAR, font_size=13, color=GRAY_C)
            card_step_lines.append(VGroup(t_obj, f_obj).arrange(RIGHT, buff=0.08))

        card_content = VGroup(*card_step_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        card_title = Text("五步极速推导", font=FONT_REGULAR, font_size=14, color=GOLD_B, weight=BOLD)
        full_box_content = VGroup(card_title, Line(LEFT, RIGHT, color=GOLD_E, stroke_width=0.8).set_width(card_content.width), card_content).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        bg_hud = SurroundingRectangle(full_box_content, buff=0.14, color=GRAY_D, fill_color=BLACK, fill_opacity=0.88, corner_radius=0.12)
        bg_hud.set_stroke(width=1.2)
        card_hud = VGroup(bg_hud, full_box_content).to_corner(UR, buff=0.35)
        self.add_fixed_in_frame_mobjects(card_hud)

        # Cue 24: 回归 3D 黄金全景 (6.29s) - 模型更加放大 (zoom=1.55)，大球体与全套字母震撼展现
        play_cue(
            24,
            FadeIn(other_edges_reborn),
            FadeIn(sphere_final),
            FadeIn(line_final_d1_op),
            FadeIn(card_hud),
            *[FadeIn(lbl) for lbl in v_final_labels],
            FadeOut(line_op_e),
            FadeOut(line_op_f),
            FadeOut(lbl_45_l),
            FadeOut(lbl_45_r),
            FadeOut(arc_90_mobj),
            FadeOut(lbl_90_deg),
            FadeOut(v3_labels),
            camera_target=dict(
                phi=68 * DEGREES,
                theta=-52 * DEGREES,
                zoom=1.55
            ),
            highlight=True,
            anim_duration=3.5
        )
        self.remove_fixed_orientation_mobjects(lbl_45_l, lbl_45_r, lbl_90_deg, *v3_labels)
        self.remove(line_op_e, line_op_f, lbl_45_l, lbl_45_r, arc_90_mobj, lbl_90_deg, v3_labels)
        gc.collect()

        # Cue 25: 复盘第 1、2 步 (10.61s) - 原位平滑点亮第 1、2 步，高线高亮，卡片永远 100% 垂直正对屏幕！
        play_cue(
            25,
            bg_hud.animate.set_stroke(color=GOLD_C),
            card_step_lines[0][0].animate.set_color(GOLD_A),
            card_step_lines[0][1].animate.set_color(YELLOW),
            card_step_lines[1][0].animate.set_color(GOLD_A),
            card_step_lines[1][1].animate.set_color(YELLOW),
            line_final_d1_op.animate.set_color(GOLD).set_stroke(width=0.035),
            Flash(O_prime, color=RED, flash_radius=0.4),
            anim_duration=3.0
        )

        # Cue 26: 复盘第 3、4、5 步 (9.10s) - 原位平滑点亮第 3、4、5 步，金色截面圆弧璀璨加粗放光
        play_cue(
            26,
            card_step_lines[2][0].animate.set_color(GOLD_A),
            card_step_lines[2][1].animate.set_color(YELLOW),
            card_step_lines[3][0].animate.set_color(GOLD_A),
            card_step_lines[3][1].animate.set_color(YELLOW),
            card_step_lines[4][0].animate.set_color(GOLD_A),
            card_step_lines[4][1].animate.set_color(YELLOW),
            golden_arc.animate.set_stroke(width=9.0, color=YELLOW_A),
            highlight=True,
            anim_duration=3.0
        )

        # Cue 27: 降维思想总结，大球与棱柱缓缓全景自转，气势磅礴落幕 (6.10s)
        self.begin_ambient_camera_rotation(rate=0.035)
        play_cue(27, highlight=True, anim_duration=2.0)
        self.stop_ambient_camera_rotation()
