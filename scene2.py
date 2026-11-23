from manim import *
import numpy as np
import manimpango
import gc

# 注册霞鹜文楷字体
manimpango.register_font(r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Regular.ttf")
manimpango.register_font(r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Medium.ttf")
FONT_REGULAR = "LXGW WenKai"

class MultiViewSphereIntersection(ThreeDScene):
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

        # 侧面正交局部基底
        u_vec = (C1 - B1) / np.linalg.norm(C1 - B1)       # 沿 B1->C1 棱向
        v_vec = np.array([0.0, 0.0, -1.0])                # 坚直向下

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

        # 底部动态阶段提示条（带精致半透明背景板，确保任何角度对比度鲜明）
        def create_stage_badge(text_str, text_color):
            tag_txt = Text(text_str, font=FONT_REGULAR, font_size=17, color=text_color)
            bg_rect = SurroundingRectangle(tag_txt, buff=0.14, color=text_color, fill_color=BLACK, fill_opacity=0.75, corner_radius=0.1)
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

        # 直四棱柱线框 (调细 thickness=0.013，精致透亮，彻底告别粗笨感)
        EDGE_THICKNESS = 0.013
        prism_edges = VGroup(
            Line3D(A, B, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(B, C, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C, D, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(D, A, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A1, B1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(B1, C1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(C1, D1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(D1, A1, color=BLUE_B, thickness=EDGE_THICKNESS),
            Line3D(A, A1, color=BLUE_C, thickness=EDGE_THICKNESS),
            Line3D(B, B1, color=BLUE_C, thickness=EDGE_THICKNESS),
            Line3D(C, C1, color=BLUE_C, thickness=EDGE_THICKNESS),
            Line3D(D, D1, color=BLUE_C, thickness=EDGE_THICKNESS),
        )

        # 侧面正方形 BCC1B1
        side_polygon = Polygon(
            B, C, C1, B1,
            fill_color=PURPLE_C,
            fill_opacity=0.30,
            stroke_color=PURPLE_A,
            stroke_width=1.8
        )

        # 顶点实体点球 (调细半径，高雅通透)
        def make_dot(pt, col, r=0.055):
            return Dot3D(point=pt, radius=r, color=col)

        dots_group = VGroup(
            make_dot(A, GRAY_B, 0.05),
            make_dot(B, BLUE_C, 0.05),
            make_dot(C, BLUE_C, 0.05),
            make_dot(D, GRAY_B, 0.05),
            make_dot(A1, GRAY_A, 0.06),
            make_dot(B1, GOLD_B, 0.065),
            make_dot(C1, GOLD_B, 0.065),
            make_dot(D1, GOLD_A, 0.075), # 球心
            make_dot(O_prime, RED_A, 0.065), # 垂足
        )

        # 【核心修正 1】：视角 0 顶点标签使用 add_fixed_orientation_mobjects！
        # 无论相机怎么旋转，所有字母永远 100% 正对镜头 (Billboard)，绝不压扁或侧对镜头！
        def make_billboard_label(txt, pt, offset, font_size=16, col=WHITE):
            lbl = Text(txt, font=FONT_REGULAR, font_size=font_size, color=col)
            lbl.move_to(pt + offset)
            return lbl

        lbl_A = make_billboard_label("A", A, np.array([-0.22, -0.15, -0.1]), col=GRAY_B)
        lbl_B = make_billboard_label("B", B, np.array([-0.22, -0.25, -0.1]), col=BLUE_B)
        lbl_C = make_billboard_label("C", C, np.array([0.22, -0.2, -0.1]), col=BLUE_B)
        lbl_D = make_billboard_label("D", D, np.array([0.15, 0.22, -0.1]), col=GRAY_B)
        lbl_A1 = make_billboard_label("A₁", A1, np.array([-0.25, -0.15, 0.15]), col=GRAY_A)
        lbl_B1 = make_billboard_label("B₁", B1, np.array([-0.25, -0.25, 0.15]), col=GOLD_B)
        lbl_C1 = make_billboard_label("C₁", C1, np.array([0.25, -0.15, 0.15]), col=GOLD_B)
        lbl_D1 = make_billboard_label("D₁(球心)", D1, np.array([0.2, 0.28, 0.2]), font_size=17, col=GOLD_A)
        lbl_Op = make_billboard_label("O'(垂足)", O_prime, np.array([0.22, -0.22, 0.2]), font_size=16, col=RED_A)

        v0_labels = VGroup(lbl_A, lbl_B, lbl_C, lbl_D, lbl_A1, lbl_B1, lbl_C1, lbl_D1, lbl_Op)
        self.add_fixed_orientation_mobjects(*v0_labels)

        self.play(Create(prism_edges), FadeIn(dots_group), run_time=1.8)
        self.play(FadeIn(side_polygon), FadeIn(v0_labels), run_time=1.0)

        # 轻量化半透明大球 (20x20 分辨率)
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
        # 3. 乐章一：【视角 1·顶面垂直俯视】不压棱、正对视线的清晰重合标注
        # =========================================================================
        switch_badge("【视角 1】顶面垂直俯视：侧棱重合为点，垂距 d = 等边三角形高 = √3", YELLOW_B)

        # 清除视角 0 标签与球体
        self.play(FadeOut(v0_labels), FadeOut(sphere), run_time=0.6)
        self.remove_fixed_orientation_mobjects(*v0_labels)
        self.remove(v0_labels, sphere)
        gc.collect()

        # 【核心修正 2】：视角 1 标签精确避开所有 edge（绝不压线），且全部正对视线
        # 相机在俯视 (theta = -45°)，使用 add_fixed_orientation_mobjects 确保文字永远水平端正！
        lbl_v1_d1 = make_billboard_label("D₁(D) 球心", D1, np.array([0.25, 0.45, 0.0]), font_size=17, col=GOLD_A)
        lbl_v1_b1 = make_billboard_label("B₁(B)", B1, np.array([-0.45, -0.35, 0.0]), font_size=16, col=YELLOW_B)
        lbl_v1_c1 = make_billboard_label("C₁(C)", C1, np.array([0.45, -0.35, 0.0]), font_size=16, col=YELLOW_B)
        lbl_v1_a1 = make_billboard_label("A₁(A)", A1, np.array([-0.45, 0.35, 0.0]), font_size=16, col=GRAY_A)
        # 垂足点 O' 标签往下方拉开，绝不压在棱 B1C1 上
        lbl_v1_op = make_billboard_label("O'(垂足)", O_prime, np.array([0.0, -0.45, 0.0]), font_size=16, col=RED_A)
        # 棱长与高线文字摆在开阔空白区
        lbl_v1_edge_len = make_billboard_label("棱长 = 2", (B1 + C1) / 2, np.array([-0.55, -0.55, 0.0]), font_size=15, col=YELLOW_D)
        lbl_v1_height = make_billboard_label("高 d = √3", (D1 + O_prime) / 2, np.array([0.45, 0.15, 0.0]), font_size=16, col=RED_B)

        v1_labels = VGroup(lbl_v1_d1, lbl_v1_b1, lbl_v1_c1, lbl_v1_a1, lbl_v1_op, lbl_v1_edge_len, lbl_v1_height)
        self.add_fixed_orientation_mobjects(*v1_labels)

        # 镜头平滑拉升至正上方俯角 (留 3° 微俯角呈现空间层次)
        self.move_camera(
            phi=3 * DEGREES,
            theta=-45 * DEGREES,
            zoom=1.35,
            frame_center=np.array([0, 0, 0]),
            run_time=2.2
        )

        # 高亮顶面等边三角形 △B1C1D1 与高线 D1O' (线条适度纤细细腻 thickness=0.022)
        TRI_THICKNESS = 0.022
        diag_b1d1 = Line3D(B1, D1, color=YELLOW, thickness=TRI_THICKNESS)
        side_b1c1 = Line3D(B1, C1, color=YELLOW, thickness=TRI_THICKNESS)
        side_c1d1 = Line3D(C1, D1, color=YELLOW, thickness=TRI_THICKNESS)
        equilateral_triangle = VGroup(diag_b1d1, side_b1c1, side_c1d1)
        perp_height_line = Line3D(D1, O_prime, color=RED_A, thickness=0.025)

        self.play(Create(equilateral_triangle), run_time=1.0)
        self.play(Create(perp_height_line), FadeIn(v1_labels), run_time=1.0)

        # 慢速呼吸微摆视差 (2° ~ 5°)
        self.move_camera(
            phi=5 * DEGREES,
            theta=-43 * DEGREES,
            run_time=4.0,
            rate_func=there_and_back
        )
        self.wait(0.8)

        # =========================================================================
        # 4. 乐章二：【视角 2·顺棱对齐切面】线条纤细通透，标准直角三角形
        # =========================================================================
        switch_badge("【视角 2】顺棱切面视线：BC与B₁C₁重合成一线，勾股求截面半径 r = √2", GREEN_A)

        self.play(
            FadeOut(v1_labels),
            FadeOut(equilateral_triangle),
            run_time=0.6
        )
        self.remove_fixed_orientation_mobjects(*v1_labels)
        self.remove(v1_labels, equilateral_triangle)
        gc.collect()

        # 视线旋转对齐至棱 B1C1 方向 (phi=89°, theta=-150°)
        self.move_camera(
            phi=89 * DEGREES,
            theta=-150 * DEGREES,
            zoom=1.5,
            frame_center=O_prime + np.array([0, 0, -0.4]),
            run_time=2.2
        )

        # 【核心修正 3】：将视角 2 的直角三角形各边从粗管道大幅调细！
        # 水平边：D1 -> O' (thickness=0.020)
        # 坚直边：O' -> M_bottom (thickness=0.020)
        # 斜边：D1 -> M_bottom (thickness=0.020)
        TRI2_THICKNESS = 0.020
        vert_radius_line = Line3D(O_prime, M_bottom, color=ORANGE, thickness=TRI2_THICKNESS)
        hypotenuse_line = Line3D(D1, M_bottom, color=GOLD, thickness=TRI2_THICKNESS)
        dot_M = Dot3D(point=M_bottom, radius=0.065, color=ORANGE)

        # 视角 2 标签全部采用正对镜头的 billboard 标注，绝不压线，层次分明
        lbl_v2_top = make_billboard_label("B₁(C₁, O')", O_prime, np.array([0.0, 0.0, 0.22]), font_size=16, col=YELLOW_B)
        lbl_v2_bot = make_billboard_label("B(C)", O_bottom, np.array([0.0, 0.0, -0.22]), font_size=16, col=BLUE_B)
        lbl_v2_d1 = make_billboard_label("D₁(A₁)", D1, np.array([-0.22, 0.0, 0.18]), font_size=16, col=GOLD_A)
        lbl_v2_m = make_billboard_label("M (圆弧底点)", M_bottom, np.array([0.0, 0.0, -0.24]), font_size=15, col=ORANGE)

        # 直角三角形边长标注 (放置在三角形外部或正旁，避开线段本体)
        lbl_v2_d = make_billboard_label("d = √3", (D1 + O_prime) / 2, np.array([0.0, 0.0, 0.16]), font_size=16, col=RED_A)
        lbl_v2_r = make_billboard_label("r = √2", (O_prime + M_bottom) / 2, np.array([0.28, 0.0, 0.0]), font_size=16, col=ORANGE)
        lbl_v2_R = make_billboard_label("R = √5", (D1 + M_bottom) / 2, np.array([-0.25, 0.0, -0.1]), font_size=16, col=GOLD)

        v2_labels = VGroup(lbl_v2_top, lbl_v2_bot, lbl_v2_d1, lbl_v2_m, lbl_v2_d, lbl_v2_r, lbl_v2_R)
        self.add_fixed_orientation_mobjects(*v2_labels)

        self.play(
            Create(vert_radius_line),
            Create(hypotenuse_line),
            FadeIn(dot_M),
            FadeIn(v2_labels),
            run_time=1.4
        )

        # 顺棱慢速视差微晃 (89° ~ 91°)
        self.move_camera(
            phi=91 * DEGREES,
            theta=-148 * DEGREES,
            run_time=4.0,
            rate_func=there_and_back
        )
        self.wait(0.8)

        # =========================================================================
        # 5. 乐章三：【视角 3·正对侧面 89°~91°微摆】正面全点位与圆心角 90°
        # =========================================================================
        switch_badge("【视角 3】正对侧面：89°~91°微摆视差呼吸，等腰直角定格圆心角 90°", GOLD_A)

        self.play(
            FadeOut(hypotenuse_line),
            FadeOut(vert_radius_line),
            FadeOut(dot_M),
            FadeOut(v2_labels),
            run_time=0.6
        )
        self.remove_fixed_orientation_mobjects(*v2_labels)
        self.remove(hypotenuse_line, vert_radius_line, dot_M, v2_labels)
        gc.collect()

        # 精确转至正对侧面正方形 BCC1B1 (外法线朝向 theta = -60°)
        self.move_camera(
            phi=89 * DEGREES,
            theta=-60 * DEGREES,
            zoom=1.45,
            frame_center=O_prime + np.array([0, 0, -0.6]),
            run_time=2.2
        )

        # 截面圆弧交点 E (BB1 中点), F (CC1 中点)
        dot_E = Dot3D(point=E, radius=0.065, color=YELLOW)
        dot_F = Dot3D(point=F, radius=0.065, color=YELLOW)
        rad_E = Line3D(O_prime, E, color=ORANGE, thickness=0.022)
        rad_F = Line3D(O_prime, F, color=ORANGE, thickness=0.022)

        # 视角 3 正面标签 (统一 billboard，清晰可读且不遮挡图形)
        lbl_v3_b1 = make_billboard_label("B₁", B1, np.array([-0.22, 0.0, 0.16]), font_size=17, col=GOLD_B)
        lbl_v3_c1 = make_billboard_label("C₁", C1, np.array([0.22, 0.0, 0.16]), font_size=17, col=GOLD_B)
        lbl_v3_b = make_billboard_label("B", B, np.array([-0.22, 0.0, -0.18]), font_size=17, col=BLUE_B)
        lbl_v3_c = make_billboard_label("C", C, np.array([0.22, 0.0, -0.18]), font_size=17, col=BLUE_B)
        lbl_v3_op = make_billboard_label("O'(垂足圆心)", O_prime, np.array([0.0, 0.0, 0.24]), font_size=17, col=RED_A)
        lbl_v3_e = make_billboard_label("E(中点)", E, np.array([-0.3, 0.0, 0.0]), font_size=15, col=YELLOW)
        lbl_v3_f = make_billboard_label("F(中点)", F, np.array([0.3, 0.0, 0.0]), font_size=15, col=YELLOW)

        # 45° 角度与圆心角标注
        lbl_v3_a1 = make_billboard_label("45°", O_prime + 0.35 * (E - O_prime) / np.linalg.norm(E - O_prime) + np.array([-0.12, 0, 0.08]), np.zeros(3), font_size=15, col=ORANGE)
        lbl_v3_a2 = make_billboard_label("45°", O_prime + 0.35 * (F - O_prime) / np.linalg.norm(F - O_prime) + np.array([0.12, 0, 0.08]), np.zeros(3), font_size=15, col=ORANGE)
        lbl_v3_center_ang = make_billboard_label("圆心角 α = 90°", O_prime + np.array([0.0, 0.0, -0.4]), np.zeros(3), font_size=17, col=YELLOW_A)

        v3_labels = VGroup(
            lbl_v3_b1, lbl_v3_c1, lbl_v3_b, lbl_v3_c,
            lbl_v3_op, lbl_v3_e, lbl_v3_f,
            lbl_v3_a1, lbl_v3_a2, lbl_v3_center_ang
        )
        self.add_fixed_orientation_mobjects(*v3_labels)

        self.play(
            Create(rad_E),
            Create(rad_F),
            FadeIn(dot_E),
            FadeIn(dot_F),
            FadeIn(v3_labels),
            run_time=1.4
        )

        # 核心交互：89° ~ 91° 缓动呼吸微摆 5.5 秒
        self.move_camera(
            phi=91 * DEGREES,
            theta=-59 * DEGREES,
            run_time=5.5,
            rate_func=there_and_back
        )
        self.wait(0.8)

        # =========================================================================
        # 6. 乐章四：终极秒杀卡片与 3D 宏观回旋
        # =========================================================================
        switch_badge("【终极秒杀】弧长公式 L = α · r = (π/2) · √2 = (√2/2)π", GREEN_B)

        # 优雅淡出侧面正交的细部角度标签与连线，回归纯净几何
        self.play(
            FadeOut(v3_labels),
            FadeOut(rad_E),
            FadeOut(rad_F),
            FadeOut(dot_E),
            FadeOut(dot_F),
            run_time=0.6
        )
        self.remove_fixed_orientation_mobjects(*v3_labels)
        self.remove(v3_labels, rad_E, rad_F, dot_E, dot_F)
        gc.collect()

        # 终极秒杀黑金卡片 (霞鹜文楷排版，精致高贵)
        calc_card = VGroup(
            Text("【多视角通解模型三步秒杀】", font=FONT_REGULAR, font_size=18, weight=BOLD, color=GOLD),
            Text("Step 1 (顶视图): 球心垂距 d = 等边△高 = √3", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("Step 2 (侧切面): 截面圆半径 r = √(R² - d²) = √(5 - 3) = √2", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("Step 3 (侧正方): 等腰直角交中点，两翼各 45°", font=FONT_REGULAR, font_size=15, color=WHITE),
            Text("Step 4 (圆心角): 侧面圆心角 α = 180° - 45° - 45° = 90° (π/2)", font=FONT_REGULAR, font_size=16, color=YELLOW_B),
            Text("Step 5 (交线长): L = α · r = (π/2) · √2 = (√2/2)π", font=FONT_REGULAR, font_size=18, weight=BOLD, color=GREEN_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UR, buff=0.35).shift(DOWN * 0.8)

        card_bg = SurroundingRectangle(calc_card, color=GOLD_B, buff=0.2, fill_color=BLACK, fill_opacity=0.82, corner_radius=0.12)
        calc_box = VGroup(card_bg, calc_card)
        self.add_fixed_in_frame_mobjects(calc_box)

        self.play(FadeIn(calc_box, shift=LEFT * 0.25), run_time=1.4)

        # 镜头拉回宏观 3D 黄金视角，带环境光自转
        self.move_camera(
            phi=68 * DEGREES,
            theta=-52 * DEGREES,
            zoom=1.1,
            frame_center=np.array([0, 0, 0]),
            run_time=2.8
        )
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(3.0)
