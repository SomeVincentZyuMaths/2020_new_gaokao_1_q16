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

class Scene5(ThreeDScene):
    def construct(self):
        # =========================================================================
        # 0. 读取 24 个精准分镜音频时间戳元数据
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

        # 初始相机：开场原距全景 (zoom=1.0, 保持与原版完全一致)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES, zoom=1.0, frame_center=np.array([0.0, 0.0, 0.0]))

        # =========================================================================
        # 2. 常驻 HUD 标题与动态字幕控制器
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
        self.play(FadeIn(title_group), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.035)

        # Cue 1: 题目前言 (3.86s)
        play_cue(1, highlight=True)

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

        v0_labels = VGroup(
            make_billboard_label("A", A, np.array([-0.3, -0.3, 0]), col=GRAY_A),
            make_billboard_label("B", B, np.array([0, -0.35, 0]), col=YELLOW_B),
            make_billboard_label("C", C, np.array([0.3, -0.3, 0]), col=YELLOW_B),
            make_billboard_label("D", D, np.array([0, 0.35, 0]), col=GRAY_A),
            make_billboard_label("A₁", A1, np.array([-0.3, 0.3, 0]), col=GRAY_A),
            make_billboard_label("B₁", B1, np.array([0, -0.35, 0]), col=YELLOW_B),
            make_billboard_label("C₁", C1, np.array([0.3, -0.3, 0]), col=YELLOW_B),
            make_billboard_label("D₁(球心)", D1, np.array([0, 0.35, 0]), col=GOLD_A)
        )

        # Cue 2: 直四棱柱与底角60度 (6.48s)
        self.add_fixed_orientation_mobjects(*v0_labels)
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
            full_circle_mobj.animate.set_stroke(opacity=0.25, width=1.0),
            Flash(O_prime, color=GOLD, flash_radius=0.45),
            highlight=True,
            anim_duration=3.2
        )
        self.play(FadeOut(full_circle_mobj), FadeOut(sphere), run_time=1.0)
        self.remove(full_circle_mobj, sphere)
        del full_circle_mobj, sphere
        gc.collect()

        self.stop_ambient_camera_rotation()

        # =========================================================================
        # 4. 第二乐章 · 顶面俯视与线面垂直证明 (Cues 7 ~ 16)
        # 电影级运镜①：从全景平滑升起俯冲推近至 zoom=1.45，焦点锁定顶面
        # =========================================================================
        # Cue 7: 视角切换拉升 + 镜头推近 (2.66s)
        self.play(FadeOut(v0_labels), FadeOut(diag_bd), run_time=0.6)
        self.remove_fixed_orientation_mobjects(*v0_labels)
        self.remove(v0_labels, diag_bd)
        gc.collect()

        v1_labels = VGroup(
            make_billboard_label("D₁(球心)", D1, np.array([0.2, 0.4, 0]), font_size=16, col=GOLD_A),
            make_billboard_label("B₁", B1, np.array([-0.4, -0.3, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("C₁", C1, np.array([0.4, -0.3, 0]), font_size=15, col=YELLOW_B),
            make_billboard_label("A₁", A1, np.array([-0.4, 0.3, 0]), font_size=15, col=GRAY_A),
            make_billboard_label("O'(垂足·圆心)", O_prime, np.array([0.0, -0.42, 0]), font_size=15, col=RED_A)
        )
        self.add_fixed_orientation_mobjects(*v1_labels)
        play_cue(
            7,
            camera_target=dict(
                phi=3 * DEGREES,
                theta=-45 * DEGREES,
                zoom=1.45
            ),
            anim_duration=2.0
        )

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
        self.add_fixed_orientation_mobjects(lbl_h_val)
        play_cue(9, Create(line_d1_op), Create(dot_op), anim_duration=3.0)

        # Cue 10: 垂足O'也是圆心 (4.08s)
        play_cue(10, Flash(O_prime, color=RED, flash_radius=0.4), anim_duration=1.5)

        # Cue 11: 证明准备 (3.96s)
        play_cue(11, anim_duration=1.0)

        # Cue 12: 细节2·直角折角符号 + 判定1 (5.59s)
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

        # Cue 13: 侧棱垂直顶面 (9.24s)
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

        # Cue 14: 两相交线得出垂直结论 (13.15s)
        play_cue(14, highlight=True, anim_duration=2.5)

        # Cue 15: 垂距概念明确 (5.90s)
        play_cue(15, line_d1_op.animate.set_color(GOLD).set_stroke(width=0.035), anim_duration=2.2)

        # Cue 16: 勾股算出高 d = √3 + 弹出步骤① (8.28s)
        lbl_c1_len = make_billboard_label("半棱长 = 1", (O_prime + C1) / 2, np.array([0, -0.32, 0]), font_size=14, col=YELLOW_D)
        self.add_fixed_orientation_mobjects(lbl_c1_len)
        card_step1 = create_step_card(active_steps=[1])
        self.add_fixed_in_frame_mobjects(card_step1)
        play_cue(16, FadeIn(lbl_c1_len), highlight=True, anim_duration=2.5)

        self.play(FadeOut(lbl_c1_len), FadeOut(elbow_group), run_time=0.6)
        self.remove_fixed_in_frame_mobjects(card_step1, proof_panel)
        self.remove_fixed_orientation_mobjects(lbl_c1_len)
        self.remove(card_step1, proof_panel, lbl_c1_len, elbow_group)
        del card_step1, proof_panel
        gc.collect()

        # =========================================================================
        # 5. 第三乐章 · 侧面勾股定理求截面圆半径 (Cues 17 ~ 19)
        # 维持特写：zoom=1.40，焦点在侧面直角三角形区域
        # =========================================================================
        # Cue 17: 运镜切向侧面 + 细节3·大球隐现穿透淡出 (2.90s)
        self.play(FadeOut(v1_labels), run_time=0.4)
        self.remove_fixed_orientation_mobjects(*v1_labels)
        self.remove(v1_labels)
        gc.collect()

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
        self.play(FadeOut(sphere_replay), run_time=0.6)
        self.remove(sphere_replay)
        del sphere_replay
        gc.collect()

        # Cue 18: 垂距与球半径构成直角三角形 (5.47s)
        pt_M = O_prime + r_circle * v_vec
        line_R_hypot = Line3D(D1, pt_M, color=TEAL_A, thickness=0.02)
        line_r_leg = Line3D(O_prime, pt_M, color=YELLOW_A, thickness=0.022)
        lbl_R_val = make_billboard_label("R = √5", (D1 + pt_M) / 2, np.array([0.2, 0.2, 0.1]), font_size=15, col=TEAL_A)
        lbl_r_val = make_billboard_label("截面半径 r", (O_prime + pt_M) / 2, np.array([0.3, 0, 0]), font_size=15, col=YELLOW_B)
        self.add_fixed_orientation_mobjects(lbl_R_val, lbl_r_val)
        play_cue(18, Create(line_R_hypot), Create(line_r_leg), anim_duration=2.5)

        # Cue 19: 勾股算出 r = √2 + 弹出步骤② (13.90s)
        card_step2 = create_step_card(active_steps=[2])
        self.add_fixed_in_frame_mobjects(card_step2)
        play_cue(
            19,
            Flash(O_prime, color=YELLOW, flash_radius=0.4),
            highlight=True,
            anim_duration=3.0
        )
        self.play(FadeOut(lbl_R_val), FadeOut(lbl_r_val), FadeOut(line_R_hypot), FadeOut(line_r_leg), run_time=0.6)
        self.remove_fixed_in_frame_mobjects(card_step2)
        self.remove_fixed_orientation_mobjects(lbl_R_val, lbl_r_val)
        self.remove(card_step2, lbl_R_val, lbl_r_val, line_R_hypot, line_r_leg)
        del card_step2
        gc.collect()

        # =========================================================================
        # 6. 第四乐章 · 正方形降维秒杀与弧长终解 (Cues 20 ~ 24)
        # 电影级运镜②：深推近放大至 zoom=1.95，正方形铺满屏幕 70%！
        # =========================================================================
        # Cue 20: 正视正方形，彻底降维 (5.18s)
        self.play(FadeOut(other_edges), FadeOut(line_d1_op), FadeOut(tri_b1c1d1), FadeOut(diag_b1d1_top), run_time=0.6)
        self.remove(other_edges, line_d1_op, tri_b1c1d1, diag_b1d1_top)
        gc.collect()

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
            camera_target=dict(
                phi=90 * DEGREES,
                theta=-90 * DEGREES,
                zoom=1.85
            ),
            anim_duration=2.5
        )

        # Cue 21: 左右 45° 切角 (10.85s)
        line_op_e = Line3D(O_prime, E, color=YELLOW_C, thickness=0.018)
        line_op_f = Line3D(O_prime, F, color=YELLOW_C, thickness=0.018)
        lbl_45_l = make_billboard_label("45°", O_prime + u_vec * (-0.45) + v_vec * 0.15, font_size=14, col=GOLD_A)
        lbl_45_r = make_billboard_label("45°", O_prime + u_vec * 0.45 + v_vec * 0.15, font_size=14, col=GOLD_A)
        self.add_fixed_orientation_mobjects(lbl_45_l, lbl_45_r)
        play_cue(21, Create(line_op_e), Create(line_op_f), FadeIn(lbl_45_l), FadeIn(lbl_45_r), anim_duration=3.2)

        # Cue 22: 圆心角 90° = π/2 (10.42s)
        arc_90_pts = [O_prime + 0.35 * np.cos(th) * u_vec + 0.35 * np.sin(th) * v_vec for th in thetas_arc]
        arc_90_mobj = VMobject(color=GOLD_A, stroke_width=2.5)
        arc_90_mobj.set_points_smoothly(arc_90_pts)
        lbl_90_deg = make_billboard_label("90° (π/2)", O_prime + v_vec * 0.45, font_size=15, col=GOLD_B)
        self.add_fixed_orientation_mobjects(lbl_90_deg)
        play_cue(22, Create(arc_90_mobj), FadeIn(lbl_90_deg), highlight=True, anim_duration=2.8)

        # Cue 23: 弧长终解秒杀 (12.84s)
        play_cue(
            23,
            golden_arc.animate.set_stroke(width=8.0, color=GOLD),
            Flash(O_prime + v_vec * SQRT2, color=GOLD),
            highlight=True,
            anim_duration=3.5
        )

        # =========================================================================
        # 电影级运镜③：平滑拉远缩小回归 3D 黄金全景 (zoom 1.95 -> 1.15)
        # =========================================================================
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
        final_all_card = create_step_card(active_steps=[1, 2, 3, 4, 5])
        self.add_fixed_in_frame_mobjects(final_all_card)
        play_cue(
            24,
            FadeIn(other_edges_reborn),
            camera_target=dict(
                phi=68 * DEGREES,
                theta=-52 * DEGREES,
                zoom=1.15
            ),
            highlight=True,
            anim_duration=3.5
        )
        self.wait(2.0)
