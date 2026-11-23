from manim import *
import numpy as np
import manimpango

import os

# 注册霞鹜文楷字体 (优先读取项目内置 fonts/ 目录)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
font_candidates = [
    os.path.join(BASE_DIR, "fonts", "LXGWWenKai-Regular.ttf"),
    r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Regular.ttf"
]
for p in font_candidates:
    if os.path.exists(p):
        manimpango.register_font(p)
FONT_REGULAR = "LXGW WenKai"

class ProblemPoster(ThreeDScene):
    def construct(self):
        # =========================================================================
        # 1. 几何坐标与常量设定 (严格棱长均为 2)
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

        # 关键几何特征点
        O_prime = np.array([SQRT3 / 2, -0.5, 1.0])        # 顶棱 B1C1 中点 (垂足圆心)
        E = np.array([0.0, -1.0, 0.0])                    # 侧棱 BB1 中点 (截面小圆左交点)
        F = np.array([SQRT3, 0.0, 0.0])                   # 侧棱 CC1 中点 (截面小圆右交点)
        M_bottom = O_prime + np.array([0.0, 0.0, -SQRT2]) # 截面圆弧底点

        # 侧面正交局部基底
        u_vec = (C1 - B1) / np.linalg.norm(C1 - B1)
        v_vec = np.array([0.0, 0.0, -1.0])

        # 摄像机视角：居于右半区的绝对黄金分割正中心
        self.set_camera_orientation(
            phi=68 * DEGREES,
            theta=-48 * DEGREES,
            zoom=1.04,
            frame_center=np.array([-2.0, 0.0, 0.0])
        )

        # =========================================================================
        # 2. 3D 空间立体几何对象构建
        # =========================================================================
        EDGE_THICKNESS = 0.013
        edges = [
            (A, B), (B, C), (C, D), (D, A),
            (A1, B1), (B1, C1), (C1, D1), (D1, A1),
            (A, A1), (B, B1), (C, C1), (D, D1)
        ]
        prism_lines = VGroup(*[
            Line3D(p1, p2, color=BLUE_B, thickness=EDGE_THICKNESS)
            for p1, p2 in edges
        ])

        # 侧面正方形 BCC1B1 半透明面
        side_square = Polygon(
            B, C, C1, B1,
            fill_color=PURPLE_C,
            fill_opacity=0.35,
            stroke_color=PURPLE_B,
            stroke_width=2.2
        )

        # 等边三角形 B1C1D1 虚构辅助线与球心垂线
        line_b1d1 = Line3D(B1, D1, color=YELLOW_B, thickness=0.015)
        line_d1_op = Line3D(D1, O_prime, color=RED_A, thickness=0.024) # 垂线 d = √3

        # 截面圆弧与完整小圆
        thetas = np.linspace(45 * DEGREES, 135 * DEGREES, 60)
        arc_points = [
            O_prime + SQRT2 * np.cos(th) * u_vec + SQRT2 * np.sin(th) * v_vec
            for th in thetas
        ]
        intersection_arc = VMobject(color=YELLOW_A, stroke_width=6.8)
        intersection_arc.set_points_smoothly(arc_points)

        full_thetas = np.linspace(0, 360 * DEGREES, 90)
        full_pts = [
            O_prime + SQRT2 * np.cos(th) * u_vec + SQRT2 * np.sin(th) * v_vec
            for th in full_thetas
        ]
        full_slice_circle = VMobject(color=YELLOW_E, stroke_width=1.5)
        full_slice_circle.set_points_smoothly(full_pts)

        # 截面内圆心到端点连线 (展开 45° 等腰直角特征)
        rad_e = Line3D(O_prime, E, color=ORANGE, thickness=0.020)
        rad_f = Line3D(O_prime, F, color=ORANGE, thickness=0.020)

        # 侧面正方形两上角直角折角
        def make_ra(center_pt, dir1, dir2, sz=0.18, col=PURPLE_A):
            ra = VMobject(color=col, stroke_width=2.2)
            ra.set_points_as_corners([
                center_pt + dir1 * sz,
                center_pt + dir1 * sz + dir2 * sz,
                center_pt + dir2 * sz
            ])
            return ra

        ra_b1 = make_ra(B1, u_vec, v_vec)
        ra_c1 = make_ra(C1, -u_vec, v_vec)
        
        # 垂足 O' 处的直角折角 (在顶面内)
        dir_to_d1 = (D1 - O_prime) / np.linalg.norm(D1 - O_prime)
        dir_to_c1 = (C1 - O_prime) / np.linalg.norm(C1 - O_prime)
        ra_o_prime = VMobject(color=RED_A, stroke_width=2.6)
        ra_o_prime.set_points_as_corners([
            O_prime + dir_to_d1 * 0.22,
            O_prime + dir_to_d1 * 0.22 + dir_to_c1 * 0.22,
            O_prime + dir_to_c1 * 0.22
        ])

        # 3D 空间通用圆弧角生成函数 (标出 60° 顶角与两翼 45° 角)
        def make_3d_angle(p1, vertex, p2, radius=0.4, color=YELLOW, stroke_width=2.8, num_pts=30):
            v1 = (p1 - vertex) / np.linalg.norm(p1 - vertex)
            v2_raw = (p2 - vertex) / np.linalg.norm(p2 - vertex)
            dot_val = np.clip(np.dot(v1, v2_raw), -1.0, 1.0)
            total_angle = np.arccos(dot_val)
            v2_perp = v2_raw - dot_val * v1
            norm_perp = np.linalg.norm(v2_perp)
            if norm_perp < 1e-7:
                return VMobject()
            v2 = v2_perp / norm_perp
            th_arr = np.linspace(0, total_angle, num_pts)
            pts = [vertex + radius * (np.cos(th) * v1 + np.sin(th) * v2) for th in th_arr]
            arc = VMobject(color=color, stroke_width=stroke_width)
            arc.set_points_smoothly(pts)
            return arc

        arc_60 = make_3d_angle(B1, A1, D1, radius=0.42, color=YELLOW_B, stroke_width=2.8)
        arc_45_l = make_3d_angle(B1, O_prime, E, radius=0.36, color=ORANGE, stroke_width=2.4)
        arc_45_r = make_3d_angle(C1, O_prime, F, radius=0.36, color=ORANGE, stroke_width=2.4)

        # 实体点球
        def make_dot(pt, col, r=0.06):
            return Dot3D(point=pt, radius=r, color=col)

        dots = VGroup(
            make_dot(A, GRAY_B, 0.05),
            make_dot(B, BLUE_B, 0.06),
            make_dot(C, BLUE_B, 0.06),
            make_dot(D, GRAY_B, 0.05),
            make_dot(A1, GRAY_A, 0.06),
            make_dot(B1, GOLD_B, 0.065),
            make_dot(C1, GOLD_B, 0.065),
            make_dot(D1, GOLD_A, 0.08),    # 球心
            make_dot(O_prime, RED_A, 0.068), # 垂足
            make_dot(E, YELLOW, 0.06),
            make_dot(F, YELLOW, 0.06),
        )

        # Billboard 标签 (永远正对镜头)
        def make_billboard(txt, pt, offset, font_size=15, col=WHITE, weight=NORMAL):
            lbl = Text(txt, font=FONT_REGULAR, font_size=font_size, color=col, weight=weight)
            lbl.move_to(pt + offset)
            return lbl

        bisector_60 = ((B1 + D1) / 2 - A1) / np.linalg.norm((B1 + D1) / 2 - A1)

        labels = VGroup(
            make_billboard("A", A, np.array([-0.22, -0.15, -0.1]), col=GRAY_B),
            make_billboard("B", B, np.array([-0.25, -0.25, -0.1]), col=BLUE_B),
            make_billboard("C", C, np.array([0.22, -0.2, -0.1]), col=BLUE_B),
            make_billboard("D", D, np.array([0.15, 0.22, -0.1]), col=GRAY_B),
            make_billboard("A₁", A1, np.array([-0.25, -0.15, 0.15]), col=GRAY_A),
            make_billboard("60°", A1 + bisector_60 * 0.65, np.zeros(3), font_size=14, col=YELLOW_B),
            make_billboard("B₁", B1, np.array([-0.30, -0.25, 0.15]), col=GOLD_B),
            make_billboard("C₁", C1, np.array([0.30, -0.15, 0.15]), col=GOLD_B),
            make_billboard("D₁(球心)", D1, np.array([0.0, 0.35, 0.30]), font_size=16, col=GOLD_A, weight=BOLD),
            make_billboard("O'(垂足)", O_prime, np.array([0.15, -0.25, 0.32]), font_size=15, col=RED_A),
            make_billboard("E", E, np.array([-0.24, -0.15, 0.0]), font_size=14, col=YELLOW),
            make_billboard("F", F, np.array([0.24, -0.15, 0.0]), font_size=14, col=YELLOW),
            make_billboard("d = √3", (D1 + O_prime) / 2, np.array([0.42, 0.12, 0.12]), font_size=15, col=RED_B),
            make_billboard("交线长 L", (E + F) / 2 + np.array([0, 0, -0.45]), np.array([0.15, -0.2, -0.05]), font_size=15, col=YELLOW_A, weight=BOLD),
        )
        self.add_fixed_orientation_mobjects(*labels)

        # 半透明大球面 (降低透明度，突出内部几何骨架)
        sphere = Sphere(
            center=D1,
            radius=SQRT5,
            resolution=(32, 32)
        ).set_color(GOLD).set_opacity(0.075)

        # 添加所有三维物体
        self.add(
            prism_lines, side_square, sphere,
            line_b1d1, line_d1_op,
            full_slice_circle, intersection_arc,
            rad_e, rad_f,
            ra_b1, ra_c1, ra_o_prime,
            arc_60, arc_45_l, arc_45_r,
            dots, labels
        )

        # =========================================================================
        # 3. 左侧常驻题目海报与秒杀解析卡片 (2D HUD, 极致黑金文楷)
        # =========================================================================
        tag_title = Text("2020年新高考Ⅰ卷 · 第16题", font=FONT_REGULAR, font_size=21, weight=BOLD, color=GOLD_A)
        tag_badge = SurroundingRectangle(tag_title, buff=0.15, color=GOLD_B, fill_color=BLACK, fill_opacity=0.88, corner_radius=0.1)
        tag_badge.set_stroke(width=1.4)
        tag_group = VGroup(tag_badge, tag_title)

        # 题目原文本 (排版规整，分行适度)
        prob_header = Text("【原题呈现】", font=FONT_REGULAR, font_size=17, weight=BOLD, color=YELLOW_A)
        prob_text = Text(
            "直四棱柱 ABCD-A₁B₁C₁D₁ 的棱长均为 2，\n"
            "∠BAD = 60°。以 D₁ 为球心，√5 为半径的\n"
            "球面与侧面 BCC₁B₁ 的交线长为 ______。",
            font=FONT_REGULAR, font_size=15, line_spacing=1.35, color=WHITE
        )

        # 核心通解与三步秒杀
        sol_header = Text("【多视角通解模型】", font=FONT_REGULAR, font_size=17, weight=BOLD, color=GREEN_B)
        sol_steps = Text(
            "① 顶视图：△B₁C₁D₁ 为等边三角形(边长2)\n"
            "   球心 D₁ 到侧面垂足为中点 O'，垂距 d = √3\n"
            "② 截面圆：勾股定理求得截面小圆半径\n"
            "   r = √(R² - d²) = √(5 - 3) = √2\n"
            "③ 降维侧面：正方形内两翼均为等腰直角△\n"
            "   直角边 B₁O'=B₁E=1 ⇒ 夹角各 45°\n"
            "   圆心角 α = 180° - 45° - 45° = 90° (π/2)\n"
            "④ 交线长：L = α · r = (π/2) · √2 = (√2/2)π",
            font=FONT_REGULAR, font_size=13.5, line_spacing=1.28, color=GRAY_A
        )

        # 答案框
        ans_txt = Text("参考答案： (√2 / 2) π", font=FONT_REGULAR, font_size=18, weight=BOLD, color=GOLD)
        ans_bg = SurroundingRectangle(ans_txt, buff=0.14, color=GOLD, fill_color=DARK_BLUE, fill_opacity=0.7, corner_radius=0.1)
        ans_group = VGroup(ans_bg, ans_txt)

        # 整合为左侧浮窗卡片
        left_card_content = VGroup(
            tag_group,
            prob_header,
            prob_text,
            Line(LEFT * 2.8, RIGHT * 2.8, color=GRAY_C, stroke_width=0.8),
            sol_header,
            sol_steps,
            ans_group
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).to_corner(UL, buff=0.42).shift(DOWN * 0.1)

        card_bg = SurroundingRectangle(
            left_card_content,
            buff=0.22,
            color=GOLD_E,
            fill_color=BLACK,
            fill_opacity=0.86,
            corner_radius=0.15
        ).set_stroke(width=1.5)

        full_left_hud = VGroup(card_bg, left_card_content)
        self.add_fixed_in_frame_mobjects(full_left_hud)
