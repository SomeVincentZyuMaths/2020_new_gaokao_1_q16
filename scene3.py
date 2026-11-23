from manim import *
import numpy as np
import manimpango
import gc

# 注册霞鹜文楷字体
manimpango.register_font(r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Regular.ttf")
manimpango.register_font(r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Medium.ttf")
FONT_REGULAR = "LXGW WenKai"

class MultiViewSphereIntersectionExtended(ThreeDScene):
    def construct(self):
        # =========================================================================
        # 0. 几何常量与三维空间坐标设定 (严格棱长均为 2)
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
        O_bottom = np.array([SQRT3 / 2, -0.5, -1.0])      # 底棱 BC 中点
        E = np.array([0.0, -1.0, 0.0])                    # 侧棱 BB1 中点 (截面小圆左交点)
        F = np.array([SQRT3, 0.0, 0.0])                   # 侧棱 CC1 中点 (截面小圆右交点)
        M_bottom = O_prime + np.array([0.0, 0.0, -SQRT2]) # 截面小圆最低点 (r = √2)

        # 几何参数
        R_sphere = SQRT5
        d_perp = SQRT3
        r_circle = SQRT2

        # 侧面正交局部基底 (u 沿 B1->C1 棱向, v 坚直向下)
        u_vec = (C1 - B1) / np.linalg.norm(C1 - B1)
        v_vec = np.array([0.0, 0.0, -1.0])

        # 初始相机：黄金 3D 视角
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES)

        # =========================================================================
        # 1. 常驻 HUD 标题与动态阶段提示栏 (霞鹜文楷)
        # =========================================================================
        title_group = VGroup(
            Text("2020年新高考I卷 · 第16题多视角极致透视", font=FONT_REGULAR, font_size=23, weight=BOLD, color=YELLOW),
            Text("直四棱柱棱长均为 2，∠BAD = 60°，球面半径 R = √5", font=FONT_REGULAR, font_size=16, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.35)
        self.add_fixed_in_frame_mobjects(title_group)
        self.play(FadeIn(title_group, shift=DOWN * 0.15), run_time=1.0)

        # 底部动态阶段提示条（带暗底徽标，对比度极高）
        def create_stage_badge(text_str, text_color):
            tag_txt = Text(text_str, font=FONT_REGULAR, font_size=17, color=text_color)
            bg_rect = SurroundingRectangle(tag_txt, buff=0.14, color=text_color, fill_color=BLACK, fill_opacity=0.78, corner_radius=0.1)
            bg_rect.set_stroke(width=1.2)
            return VGroup(bg_rect, tag_txt).to_edge(DOWN, buff=0.35)

        current_badge = create_stage_badge("【视角 0】3D 空间全局：八大顶点建构与截面圆弧初现", TEAL_A)
        self.add_fixed_in_frame_mobjects(current_badge)
        self.play(FadeIn(current_badge), run_time=0.8)

        def switch_badge(text_str, text_color):
            nonlocal current_badge
            new_badge = create_stage_badge(text_str, text_color)
            self.add_fixed_in_frame_mobjects(new_badge)
            self.play(
                FadeOut(current_badge, shift=DOWN * 0.1),
                FadeIn(new_badge, shift=UP * 0.1),
                run_time=0.5
            )
            self.remove_fixed_in_frame_mobjects(current_badge)
            current_badge = new_badge

        # =========================================================================
        # 2. 乐章零：3D 全局建模与八大顶点全标注 (视角 0)
        # =========================================================================
        self.begin_ambient_camera_rotation(rate=0.06)

        # 直四棱柱线框 (调细 thickness=0.013，精致透亮)
        EDGE_THICKNESS = 0.013
        # 侧面 BCC1B1 的四条边
        edge_B_C = Line3D(B, C, color=BLUE_B, thickness=EDGE_THICKNESS)
        edge_C_C1 = Line3D(C, C1, color=BLUE_C, thickness=EDGE_THICKNESS)
        edge_C1_B1 = Line3D(C1, B1, color=BLUE_B, thickness=EDGE_THICKNESS)
        edge_B1_B = Line3D(B1, B, color=BLUE_C, thickness=EDGE_THICKNESS)
        side_edges = VGroup(edge_B_C, edge_C_C1, edge_C1_B1, edge_B1_B)

        # 其余 8 条棱柱边（后续降维时可独立隐去）
        other_edges = VGroup(
            Line3D(A, B, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C, D, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(D, A, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A1, B1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C1, D1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(D1, A1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A, A1, color=BLUE_C, thickness=EDGE_THICKNESS),
            Line3D(D, D1, color=BLUE_C, thickness=EDGE_THICKNESS),
        )
        all_prism_edges = VGroup(side_edges, other_edges)

        # 侧面正方形 BCC1B1
        side_polygon = Polygon(
            B, C, C1, B1,
            fill_color=PURPLE_C,
            fill_opacity=0.30,
            stroke_color=PURPLE_A,
            stroke_width=1.8
        )

        # 顶点实体点球
        def make_dot(pt, col, r=0.055):
            return Dot3D(point=pt, radius=r, color=col)

        dot_A = make_dot(A, GRAY_B, 0.05)
        dot_B = make_dot(B, BLUE_C, 0.055)
        dot_C = make_dot(C, BLUE_C, 0.055)
        dot_D = make_dot(D, GRAY_B, 0.05)
        dot_A1 = make_dot(A1, GRAY_A, 0.06)
        dot_B1 = make_dot(B1, GOLD_B, 0.065)
        dot_C1 = make_dot(C1, GOLD_B, 0.065)
        dot_D1 = make_dot(D1, GOLD_A, 0.075)   # 球心
        dot_Op = make_dot(O_prime, RED_A, 0.065) # 垂足

        side_dots = VGroup(dot_B, dot_C, dot_B1, dot_C1, dot_Op)
        other_dots = VGroup(dot_A, dot_D, dot_A1, dot_D1)
        all_dots = VGroup(side_dots, other_dots)

        # Billboard 标签：永远 100% 正对镜头，绝无压扁
        def make_billboard_label(txt, pt, offset, font_size=16, col=WHITE, weight=NORMAL):
            lbl = Text(txt, font=FONT_REGULAR, font_size=font_size, color=col, weight=weight)
            lbl.move_to(pt + offset)
            return lbl

        # 3D 空间通用圆弧角生成函数 (避开 Manim 内置 Angle 强制 z=0 的 xy-plane 报错)
        def make_3d_angle(p1, vertex, p2, radius=0.4, color=YELLOW, stroke_width=3.0, num_pts=30):
            v1 = (p1 - vertex) / np.linalg.norm(p1 - vertex)
            v2_raw = (p2 - vertex) / np.linalg.norm(p2 - vertex)
            dot_val = np.clip(np.dot(v1, v2_raw), -1.0, 1.0)
            total_angle = np.arccos(dot_val)
            v2_perp = v2_raw - dot_val * v1
            norm_perp = np.linalg.norm(v2_perp)
            if norm_perp < 1e-7:
                return VMobject()
            v2 = v2_perp / norm_perp
            thetas = np.linspace(0, total_angle, num_pts)
            arc_pts = [vertex + radius * (np.cos(th) * v1 + np.sin(th) * v2) for th in thetas]
            arc_mob = VMobject(color=color, stroke_width=stroke_width)
            arc_mob.set_points_smoothly(arc_pts)
            return arc_mob

        lbl_A = make_billboard_label("A", A, np.array([-0.22, -0.15, -0.1]), col=GRAY_B)
        lbl_B = make_billboard_label("B", B, np.array([-0.22, -0.25, -0.1]), col=BLUE_B)
        lbl_C = make_billboard_label("C", C, np.array([0.22, -0.2, -0.1]), col=BLUE_B)
        lbl_D = make_billboard_label("D", D, np.array([0.15, 0.22, -0.1]), col=GRAY_B)
        lbl_A1 = make_billboard_label("A₁", A1, np.array([-0.25, -0.15, 0.15]), col=GRAY_A)
        lbl_B1 = make_billboard_label("B₁", B1, np.array([-0.25, -0.25, 0.15]), col=GOLD_B)
        lbl_C1 = make_billboard_label("C₁", C1, np.array([0.25, -0.15, 0.15]), col=GOLD_B)
        lbl_D1 = make_billboard_label("D₁(球心)", D1, np.array([0.2, 0.28, 0.2]), font_size=17, col=GOLD_A)
        lbl_Op_v0 = make_billboard_label("O'(垂足)", O_prime, np.array([0.22, -0.22, 0.2]), font_size=16, col=RED_A)

        v0_labels = VGroup(lbl_A, lbl_B, lbl_C, lbl_D, lbl_A1, lbl_B1, lbl_C1, lbl_D1, lbl_Op_v0)
        self.add_fixed_orientation_mobjects(*v0_labels)

        self.play(Create(all_prism_edges), FadeIn(all_dots), run_time=1.8)
        self.play(FadeIn(side_polygon), FadeIn(v0_labels), run_time=1.0)

        # 半透明大球体
        sphere = Sphere(
            center=D1,
            radius=R_sphere,
            resolution=(20, 20),
            fill_color=TEAL_C,
            fill_opacity=0.15,
            stroke_color=TEAL_A,
            stroke_width=0.35,
            stroke_opacity=0.25
        )

        # 截面圆弧计算
        thetas = np.linspace(45 * DEGREES, 135 * DEGREES, 50)
        arc_points = [
            O_prime + r_circle * np.cos(th) * u_vec + r_circle * np.sin(th) * v_vec
            for th in thetas
        ]
        intersection_arc = VMobject(color=YELLOW_A, stroke_width=6.0)
        intersection_arc.set_points_smoothly(arc_points)

        full_thetas = np.linspace(0, 360 * DEGREES, 90)
        full_pts = [
            O_prime + r_circle * np.cos(th) * u_vec + r_circle * np.sin(th) * v_vec
            for th in full_thetas
        ]
        full_slice_circle = VMobject(color=YELLOW_E, stroke_width=1.5)
        full_slice_circle.set_points_smoothly(full_pts)

        self.play(Create(sphere), run_time=1.8)
        self.play(
            Create(intersection_arc),
            Create(full_slice_circle),
            Flash(O_prime, color=YELLOW, flash_radius=0.4),
            run_time=1.4
        )
        self.wait(1.2)
        self.stop_ambient_camera_rotation()

        # =========================================================================
        # 3. 乐章一：【视角 1·顶面垂直俯视】圆弧角 60° 与垂足直角折角符号
        # =========================================================================
        switch_badge("【视角 1】顶面垂直俯视：侧棱重合为点，垂距 d = 等边三角形高 = √3", YELLOW_B)

        self.play(FadeOut(v0_labels), FadeOut(sphere), run_time=0.6)
        self.remove_fixed_orientation_mobjects(*v0_labels)
        self.remove(v0_labels, sphere)
        gc.collect()

        # 视角 1 俯视标签 (避开 edge，全部水平正对观众)
        lbl_v1_d1 = make_billboard_label("D₁(D) 球心", D1, np.array([0.25, 0.45, 0.0]), font_size=17, col=GOLD_A)
        lbl_v1_b1 = make_billboard_label("B₁(B)", B1, np.array([-0.45, -0.35, 0.0]), font_size=16, col=YELLOW_B)
        lbl_v1_c1 = make_billboard_label("C₁(C)", C1, np.array([0.45, -0.35, 0.0]), font_size=16, col=YELLOW_B)
        lbl_v1_a1 = make_billboard_label("A₁(A)", A1, np.array([-0.45, 0.35, 0.0]), font_size=16, col=GRAY_A)
        lbl_v1_op = make_billboard_label("O'(垂足)", O_prime, np.array([0.0, -0.45, 0.0]), font_size=16, col=RED_A)
        lbl_v1_edge_len = make_billboard_label("棱长 = 2", (B1 + C1) / 2, np.array([-0.55, -0.55, 0.0]), font_size=15, col=YELLOW_D)
        lbl_v1_height = make_billboard_label("高 d = √3", (D1 + O_prime) / 2, np.array([0.45, 0.15, 0.0]), font_size=16, col=RED_B)

        v1_labels = VGroup(lbl_v1_d1, lbl_v1_b1, lbl_v1_c1, lbl_v1_a1, lbl_v1_op, lbl_v1_edge_len, lbl_v1_height)
        self.add_fixed_orientation_mobjects(*v1_labels)

        # 镜头平滑拉升至正上方俯角
        self.move_camera(
            phi=3 * DEGREES,
            theta=-45 * DEGREES,
            zoom=1.35,
            frame_center=np.array([0, 0, 0]),
            run_time=2.2
        )

        # 等边三角形 △B1C1D1 与高线 D1O'
        TRI_THICKNESS = 0.022
        diag_b1d1 = Line3D(B1, D1, color=YELLOW, thickness=TRI_THICKNESS)
        side_b1c1 = Line3D(B1, C1, color=YELLOW, thickness=TRI_THICKNESS)
        side_c1d1 = Line3D(C1, D1, color=YELLOW, thickness=TRI_THICKNESS)
        equilateral_triangle = VGroup(diag_b1d1, side_b1c1, side_c1d1)
        perp_height_line = Line3D(D1, O_prime, color=RED_A, thickness=0.025)

        # 【新增几何符号 A1】：底面/顶面 60° 角度圆弧 (在角 A1 处)
        arc_60 = make_3d_angle(B1, A1, D1, radius=0.42, color=YELLOW_B, stroke_width=3.2)
        bisector_dir = ((B1 + D1) / 2 - A1) / np.linalg.norm((B1 + D1) / 2 - A1)
        lbl_60 = make_billboard_label("60°", A1 + bisector_dir * 0.65, np.zeros(3), font_size=15, col=YELLOW_B)

        # 【新增几何符号 A2】：高线垂足直角折角符号 (RightAngle at O')
        dir_to_d1 = (D1 - O_prime) / np.linalg.norm(D1 - O_prime)
        dir_to_c1 = (C1 - O_prime) / np.linalg.norm(C1 - O_prime)
        ra_sz = 0.22
        ra_o_prime = VMobject(color=RED_A, stroke_width=2.6)
        ra_o_prime.set_points_as_corners([
            O_prime + dir_to_d1 * ra_sz,
            O_prime + dir_to_d1 * ra_sz + dir_to_c1 * ra_sz,
            O_prime + dir_to_c1 * ra_sz
        ])

        v1_symbols = VGroup(arc_60, lbl_60, ra_o_prime)
        self.add_fixed_orientation_mobjects(lbl_60)

        self.play(Create(equilateral_triangle), run_time=1.0)
        self.play(Create(perp_height_line), FadeIn(v1_labels), run_time=1.0)
        self.play(Create(arc_60), FadeIn(lbl_60), Create(ra_o_prime), run_time=1.2)

        # 慢速呼吸微摆视差 (2° ~ 5°)
        self.move_camera(
            phi=5 * DEGREES,
            theta=-43 * DEGREES,
            run_time=3.8,
            rate_func=there_and_back
        )
        self.wait(0.8)

        # =========================================================================
        # 4. 乐章二：【视角 2·顺棱对齐切面】直角折角与直角勾股求 r = √2
        # =========================================================================
        switch_badge("【视角 2】顺棱切面视线：BC与B₁C₁重合成一线，勾股求截面半径 r = √2", GREEN_A)

        self.play(
            FadeOut(v1_labels),
            FadeOut(equilateral_triangle),
            FadeOut(v1_symbols),
            run_time=0.6
        )
        self.remove_fixed_orientation_mobjects(*v1_labels, lbl_60)
        self.remove(v1_labels, equilateral_triangle, v1_symbols)
        gc.collect()

        # 视线旋转对齐至棱 B1C1 方向
        self.move_camera(
            phi=89 * DEGREES,
            theta=-150 * DEGREES,
            zoom=1.5,
            frame_center=O_prime + np.array([0, 0, -0.4]),
            run_time=2.2
        )

        # 顺棱直角勾股边线
        TRI2_THICKNESS = 0.020
        vert_radius_line = Line3D(O_prime, M_bottom, color=ORANGE, thickness=TRI2_THICKNESS)
        hypotenuse_line = Line3D(D1, M_bottom, color=GOLD, thickness=TRI2_THICKNESS)
        dot_M = Dot3D(point=M_bottom, radius=0.065, color=ORANGE)

        # 【新增几何符号 B】：直角三角形直角折角符号 (RightAngle at O')
        dir_horiz = (D1 - O_prime) / np.linalg.norm(D1 - O_prime) # 水平指向 D1
        dir_vert = np.array([0.0, 0.0, -1.0])                   # 坚直向下指向 M
        ra_corner = VMobject(color=RED_A, stroke_width=2.5)
        ra_corner.set_points_as_corners([
            O_prime + dir_horiz * ra_sz,
            O_prime + dir_horiz * ra_sz + dir_vert * ra_sz,
            O_prime + dir_vert * ra_sz
        ])

        # 视角 2 billboard 标注
        lbl_v2_top = make_billboard_label("B₁(C₁, O')", O_prime, np.array([0.0, 0.0, 0.22]), font_size=16, col=YELLOW_B)
        lbl_v2_bot = make_billboard_label("B(C)", O_bottom, np.array([0.0, 0.0, -0.22]), font_size=16, col=BLUE_B)
        lbl_v2_d1 = make_billboard_label("D₁(A₁)", D1, np.array([-0.22, 0.0, 0.18]), font_size=16, col=GOLD_A)
        lbl_v2_m = make_billboard_label("M (圆弧底点)", M_bottom, np.array([0.0, 0.0, -0.24]), font_size=15, col=ORANGE)
        lbl_v2_d = make_billboard_label("d = √3", (D1 + O_prime) / 2, np.array([0.0, 0.0, 0.16]), font_size=16, col=RED_A)
        lbl_v2_r = make_billboard_label("r = √2", (O_prime + M_bottom) / 2, np.array([0.28, 0.0, 0.0]), font_size=16, col=ORANGE)
        lbl_v2_R = make_billboard_label("R = √5", (D1 + M_bottom) / 2, np.array([-0.25, 0.0, -0.1]), font_size=16, col=GOLD)

        v2_labels = VGroup(lbl_v2_top, lbl_v2_bot, lbl_v2_d1, lbl_v2_m, lbl_v2_d, lbl_v2_r, lbl_v2_R)
        self.add_fixed_orientation_mobjects(*v2_labels)

        self.play(
            Create(vert_radius_line),
            Create(hypotenuse_line),
            Create(ra_corner),
            FadeIn(dot_M),
            FadeIn(v2_labels),
            run_time=1.4
        )

        # 顺棱慢速视差微晃
        self.move_camera(
            phi=91 * DEGREES,
            theta=-148 * DEGREES,
            run_time=3.8,
            rate_func=there_and_back
        )
        self.wait(0.8)

        # =========================================================================
        # 5. 【核心新增】乐章三：降维剥离，纯享侧面正方形与圆弧深度推导
        # =========================================================================
        switch_badge("【降维专注】纯平面视角：剥离空间骨架，专注侧面正方形截面与弧长推演", GOLD_A)

        # 清除视角 2 的辅助对象
        self.play(
            FadeOut(hypotenuse_line),
            FadeOut(vert_radius_line),
            FadeOut(dot_M),
            FadeOut(ra_corner),
            FadeOut(v2_labels),
            FadeOut(perp_height_line),
            run_time=0.6
        )
        self.remove_fixed_orientation_mobjects(*v2_labels)
        self.remove(hypotenuse_line, vert_radius_line, dot_M, ra_corner, v2_labels, perp_height_line)
        gc.collect()

        # 【核心转折：剥离三维线框！】
        # 其它 8 条棱柱边与后方顶点隐去，只留下侧面正方形 BCC1B1 与金色截面圆弧！
        self.play(
            FadeOut(other_edges),
            FadeOut(other_dots),
            run_time=1.0
        )

        # 相机精准正面正对侧面正方形 (外法线 theta = -60°，构图居左，为右侧推导卡片留出黄金舞台)
        self.move_camera(
            phi=90 * DEGREES,
            theta=-60 * DEGREES,
            zoom=1.38,
            frame_center=O_prime + np.array([0, 0, -0.6]) - u_vec * 0.85,
            run_time=2.2
        )

        # 截面圆弧两端交点 E, F
        dot_E = make_dot(E, YELLOW, 0.065)
        dot_F = make_dot(F, YELLOW, 0.065)

        # 正面基础顶点标签 (纯几何，无遮挡)
        lbl_plane_b1 = make_billboard_label("B₁", B1, np.array([-0.22, 0.0, 0.16]), font_size=17, col=GOLD_B)
        lbl_plane_c1 = make_billboard_label("C₁", C1, np.array([0.22, 0.0, 0.16]), font_size=17, col=GOLD_B)
        lbl_plane_b = make_billboard_label("B", B, np.array([-0.22, 0.0, -0.18]), font_size=17, col=BLUE_B)
        lbl_plane_c = make_billboard_label("C", C, np.array([0.22, 0.0, -0.18]), font_size=17, col=BLUE_B)
        lbl_plane_op = make_billboard_label("O'(垂足圆心)", O_prime, np.array([0.0, 0.0, 0.24]), font_size=17, col=RED_A)
        lbl_plane_e = make_billboard_label("E", E, np.array([-0.22, 0.0, 0.0]), font_size=16, col=YELLOW)
        lbl_plane_f = make_billboard_label("F", F, np.array([0.22, 0.0, 0.0]), font_size=16, col=YELLOW)

        # 边长标注：正方形边长均为 2
        lbl_side_len = make_billboard_label("棱长 BC = BB₁ = 2", (B + C) / 2, np.array([0.0, 0.0, -0.22]), font_size=15, col=BLUE_A)

        plane_base_group = VGroup(
            lbl_plane_b1, lbl_plane_c1, lbl_plane_b, lbl_plane_c,
            lbl_plane_op, lbl_plane_e, lbl_plane_f, lbl_side_len
        )
        self.add_fixed_orientation_mobjects(*plane_base_group)

        # 正方形两上角直角折角 (角 B1 与 角 C1 处)
        def make_plane_ra(center_pt, dir1, dir2, sz=0.18, col=PURPLE_A):
            ra = VMobject(color=col, stroke_width=2.4)
            ra.set_points_as_corners([
                center_pt + dir1 * sz,
                center_pt + dir1 * sz + dir2 * sz,
                center_pt + dir2 * sz
            ])
            return ra

        ra_b1 = make_plane_ra(B1, u_vec, v_vec)
        ra_c1 = make_plane_ra(C1, -u_vec, v_vec)
        square_right_angles = VGroup(ra_b1, ra_c1)

        self.play(
            FadeIn(dot_E), FadeIn(dot_F),
            FadeIn(plane_base_group),
            Create(square_right_angles),
            run_time=1.4
        )
        self.wait(1.0)

        # --- 步骤 3.1：连线 O'E 与 O'F，展开两翼等腰直角三角形 ---
        rad_E = Line3D(O_prime, E, color=ORANGE, thickness=0.022)
        rad_F = Line3D(O_prime, F, color=ORANGE, thickness=0.022)

        # 标出半棱长 1
        lbl_len_b1_op = make_billboard_label("1", (B1 + O_prime) / 2, np.array([0.0, 0.0, 0.12]), font_size=15, col=YELLOW_D)
        lbl_len_op_c1 = make_billboard_label("1", (O_prime + C1) / 2, np.array([0.0, 0.0, 0.12]), font_size=15, col=YELLOW_D)
        lbl_len_b1_e = make_billboard_label("1", (B1 + E) / 2, np.array([-0.12, 0.0, 0.0]), font_size=15, col=YELLOW_D)
        lbl_len_c1_f = make_billboard_label("1", (C1 + F) / 2, np.array([0.12, 0.0, 0.0]), font_size=15, col=YELLOW_D)
        unit_lengths = VGroup(lbl_len_b1_op, lbl_len_op_c1, lbl_len_b1_e, lbl_len_c1_f)
        self.add_fixed_orientation_mobjects(*unit_lengths)

        # 两翼等腰直角三角形半透明淡彩高亮填充
        tri_left_fill = Polygon(
            B1, O_prime, E,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=0
        )
        tri_right_fill = Polygon(
            C1, O_prime, F,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=0
        )

        self.play(
            Create(rad_E), Create(rad_F),
            FadeIn(tri_left_fill), FadeIn(tri_right_fill),
            FadeIn(unit_lengths),
            run_time=1.5
        )

        # 【新增几何符号 C1 & C2】：在 O' 点标出两翼 45° 圆弧角
        arc_45_left = make_3d_angle(B1, O_prime, E, radius=0.38, color=ORANGE, stroke_width=2.8)
        arc_45_right = make_3d_angle(C1, O_prime, F, radius=0.38, color=ORANGE, stroke_width=2.8)

        dir_e_unit = (E - O_prime) / np.linalg.norm(E - O_prime)
        dir_f_unit = (F - O_prime) / np.linalg.norm(F - O_prime)

        lbl_45_left = make_billboard_label("45°", O_prime + 0.40 * dir_e_unit + np.array([-0.09, 0, 0.06]), np.zeros(3), font_size=15, col=ORANGE)
        lbl_45_right = make_billboard_label("45°", O_prime + 0.40 * dir_f_unit + np.array([0.09, 0, 0.06]), np.zeros(3), font_size=15, col=ORANGE)

        angles_45_labels = VGroup(lbl_45_left, lbl_45_right)
        self.add_fixed_orientation_mobjects(*angles_45_labels)

        # 右侧 HUD 深度推导演示卡片 (逐步渐入，极清排版)
        derivation_lines = [
            Text("【侧面截面深度解剖】", font=FONT_REGULAR, font_size=18, weight=BOLD, color=GOLD),
            Text("① 截面圆半径 r = √(R² - d²) = √2", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("② 直角边 B₁O' = B₁E = 1 ⇒ 两翼均为等腰直角△", font=FONT_REGULAR, font_size=15, color=ORANGE),
            Text("③ 夹角互补：圆心角 α = 180° - 45° - 45° = 90°", font=FONT_REGULAR, font_size=15, color=YELLOW_B),
            Text("④ 弧长公式：L = α · r = (π/2) · √2 = (√2/2)π", font=FONT_REGULAR, font_size=16, weight=BOLD, color=GREEN_B),
        ]
        hud_deriv_vgroup = VGroup(*derivation_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UR, buff=0.32).shift(DOWN * 0.85)
        hud_deriv_bg = SurroundingRectangle(hud_deriv_vgroup, color=GOLD_B, buff=0.22, fill_color=BLACK, fill_opacity=0.85, corner_radius=0.12)
        side_derivation_box = VGroup(hud_deriv_bg, hud_deriv_vgroup)
        self.add_fixed_in_frame_mobjects(side_derivation_box)

        self.play(
            Create(arc_45_left),
            Create(arc_45_right),
            FadeIn(angles_45_labels),
            FadeIn(side_derivation_box, shift=LEFT * 0.25),
            run_time=1.5
        )
        self.wait(1.5)

        # --- 步骤 3.2：平角互补，定格圆心角 α = 90° ---
        # 在圆心 O' 处生成标准的 90° 直角折角 (在截面内垂直)
        ra_center_90 = VMobject(color=YELLOW_A, stroke_width=2.8)
        ra_center_90.set_points_as_corners([
            O_prime + dir_e_unit * 0.22,
            O_prime + dir_e_unit * 0.22 + dir_f_unit * 0.22,
            O_prime + dir_f_unit * 0.22
        ])

        lbl_alpha_90 = make_billboard_label("α = 90°", O_prime + np.array([0.0, 0.0, -0.38]), np.zeros(3), font_size=16, col=YELLOW_A)
        self.add_fixed_orientation_mobjects(lbl_alpha_90)

        self.play(
            Create(ra_center_90),
            FadeIn(lbl_alpha_90),
            run_time=1.4
        )
        self.wait(1.5)

        # --- 步骤 3.3：金色圆弧高亮流光与弧长公式定格 ---
        arc_glow = intersection_arc.copy().set_color(YELLOW).set_stroke(width=10.0, opacity=0.85)

        self.play(
            ShowPassingFlash(arc_glow, time_width=0.6, run_time=2.2),
            Flash(O_prime, color=YELLOW_A, flash_radius=0.35),
        )
        self.wait(2.5)

        # =========================================================================
        # 6. 【核心新增】乐章四：升维缝合与时空复原
        # =========================================================================
        switch_badge("【升维复原】时空回归：空间问题降维击破，回归三维立体全景", TEAL_B)

        # 平面细部推导符号与右侧卡片淡出
        self.play(
            FadeOut(tri_left_fill), FadeOut(tri_right_fill),
            FadeOut(unit_lengths),
            FadeOut(square_right_angles),
            FadeOut(arc_45_left), FadeOut(arc_45_right),
            FadeOut(angles_45_labels),
            FadeOut(ra_center_90),
            FadeOut(lbl_alpha_90),
            FadeOut(plane_base_group),
            FadeOut(rad_E), FadeOut(rad_F),
            FadeOut(dot_E), FadeOut(dot_F),
            FadeOut(side_derivation_box, shift=RIGHT * 0.2),
            run_time=1.0
        )
        self.remove_fixed_orientation_mobjects(
            *plane_base_group, *unit_lengths, *angles_45_labels, lbl_alpha_90
        )
        self.remove_fixed_in_frame_mobjects(side_derivation_box)
        self.remove(arc_45_left, arc_45_right, ra_center_90)
        gc.collect()

        # 【核心升维动效：三维骨架从虚空中重新缝合！】
        self.play(
            Create(other_edges),
            FadeIn(other_dots),
            run_time=2.0
        )

        # 镜头平滑拉升仰角（90° -> 68°），重新展开三维立体宏观景深
        self.move_camera(
            phi=68 * DEGREES,
            theta=-52 * DEGREES,
            zoom=1.1,
            frame_center=np.array([0, 0, 0]),
            run_time=2.8
        )
        self.wait(1.0)

        # =========================================================================
        # 7. 乐章五：终极秒杀卡片与 3D 宏观自转收官
        # =========================================================================
        switch_badge("【终极秒杀】弧长公式 L = α · r = (π/2) · √2 = (√2/2)π", GREEN_B)

        # 终极秒杀黑金卡片 (霞鹜文楷排版)
        calc_card = VGroup(
            Text("【多视角通解模型三步秒杀】", font=FONT_REGULAR, font_size=18, weight=BOLD, color=GOLD),
            Text("Step 1 (顶视图): 球心垂距 d = 等边△高 = √3", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("Step 2 (侧切面): 截面圆半径 r = √(R² - d²) = √(5 - 3) = √2", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("Step 3 (降侧面): 剥离空间，正方形内边长 2，交点平分", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("Step 4 (圆心角): 两翼等腰直角各 45°，圆心角 α = 90° (π/2)", font=FONT_REGULAR, font_size=16, color=YELLOW_B),
            Text("Step 5 (交线长): L = α · r = (π/2) · √2 = (√2/2)π", font=FONT_REGULAR, font_size=18, weight=BOLD, color=GREEN_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UR, buff=0.35).shift(DOWN * 0.8)

        card_bg = SurroundingRectangle(calc_card, color=GOLD_B, buff=0.2, fill_color=BLACK, fill_opacity=0.82, corner_radius=0.12)
        calc_box = VGroup(card_bg, calc_card)
        self.add_fixed_in_frame_mobjects(calc_box)

        self.play(FadeIn(calc_box, shift=LEFT * 0.25), run_time=1.4)

        # 宏观 3D 黄金视角自转定格
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(3.5)
