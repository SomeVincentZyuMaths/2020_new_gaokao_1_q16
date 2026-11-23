from manim import *
import numpy as np

class SpherePrismIntersection(ThreeDScene):
    def construct(self):
        # =========================================================================
        # 0. 画布全局配置与相机初始化
        # =========================================================================
        # 初始透视仰角与方位角 (黄金 3D 观测角)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-52 * DEGREES)

        # 空间几何常量 (所有尺寸按棱长 2 严格等比换算)
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

        # 球心 D1 与垂足 O' (为 B1C1 的中点)
        sphere_center = D1
        R_sphere = SQRT5
        d_perp = SQRT3
        r_circle = SQRT2
        O_prime = np.array([SQRT3 / 2, -0.5, 1.0])

        # 侧面 BCC1B1 的局部坐标单位向量
        u_vec = (C1 - B1) / np.linalg.norm(C1 - B1)  # 沿着上边 B1->C1 (向右)
        v_vec = np.array([0.0, 0.0, -1.0])           # 沿着侧棱垂直向下

        # =========================================================================
        # 1. 乐章一：直四棱柱建模与题设展开
        # =========================================================================
        # 标题提示 (固定在画面左上方，不随 3D 相机旋转)
        title_group = VGroup(
            Text("2020年新高考I卷 · 第16题压轴透视", font_size=28, weight=BOLD, color=YELLOW),
            Text("直四棱柱棱长均为 2，∠BAD = 60°，求球截侧面交线长", font_size=18, color=GRAY_A)
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL, buff=0.4)
        self.add_fixed_in_frame_mobjects(title_group)
        self.play(FadeIn(title_group, shift=DOWN * 0.2), run_time=1.2)

        # 开启慢速环境自转增强立体感
        self.begin_ambient_camera_rotation(rate=0.08)

        # 构建直四棱柱线框
        bottom_edges = VGroup(
            Line3D(A, B, color=BLUE_B, thickness=0.025),
            Line3D(B, C, color=BLUE_B, thickness=0.025),
            Line3D(C, D, color=BLUE_B, thickness=0.025),
            Line3D(D, A, color=BLUE_B, thickness=0.025),
        )
        top_edges = VGroup(
            Line3D(A1, B1, color=BLUE_B, thickness=0.025),
            Line3D(B1, C1, color=BLUE_B, thickness=0.025),
            Line3D(C1, D1, color=BLUE_B, thickness=0.025),
            Line3D(D1, A1, color=BLUE_B, thickness=0.025),
        )
        side_edges = VGroup(
            Line3D(A, A1, color=BLUE_C, thickness=0.025),
            Line3D(B, B1, color=BLUE_C, thickness=0.025),
            Line3D(C, C1, color=BLUE_C, thickness=0.025),
            Line3D(D, D1, color=BLUE_C, thickness=0.025),
        )

        # 关键目标侧面 BCC1B1 (半透明水晶紫色微光)
        side_polygon = Polygon(
            B, C, C1, B1,
            fill_color=PURPLE_C,
            fill_opacity=0.35,
            stroke_color=PURPLE_A,
            stroke_width=2.5
        )

        self.play(
            Create(bottom_edges),
            Create(side_edges),
            Create(top_edges),
            run_time=2.2
        )
        self.play(FadeIn(side_polygon), run_time=1.2)

        # 标注球心 D1
        d1_dot = Dot3D(point=D1, radius=0.09, color=GOLD_A)
        d1_label = Text("D₁ (球心)", font_size=20, color=GOLD_B).next_to(d1_dot, UP + RIGHT, buff=0.15)
        self.add_fixed_in_frame_mobjects(d1_label)
        self.play(FadeIn(d1_dot), FadeIn(d1_label), run_time=1.0)
        self.wait(1.5)

        # =========================================================================
        # 2. 乐章二：球面膨胀与空间截线圆弧的诞生
        # =========================================================================
        # 半透明经纬球体
        sphere = Sphere(
            center=D1,
            radius=R_sphere,
            resolution=(32, 32),
            fill_color=TEAL_C,
            fill_opacity=0.22,
            stroke_color=TEAL_A,
            stroke_width=0.6,
            stroke_opacity=0.4
        )

        # 截面圆弧参数化 (从 theta = 45° 到 135°)
        num_arc_points = 60
        thetas = np.linspace(45 * DEGREES, 135 * DEGREES, num_arc_points)
        arc_points = [
            O_prime + r_circle * np.cos(th) * u_vec + r_circle * np.sin(th) * v_vec
            for th in thetas
        ]
        
        # 金色发光交线圆弧
        intersection_arc = VMobject(color=YELLOW_A, stroke_width=7.5)
        intersection_arc.set_points_smoothly(arc_points)

        # 截面圆其余虚线部分 (展示完整截面小圆)
        full_thetas = np.linspace(0, 360 * DEGREES, 120)
        full_circle_points = [
            O_prime + r_circle * np.cos(th) * u_vec + r_circle * np.sin(th) * v_vec
            for th in full_thetas
        ]
        full_slice_circle = VMobject(color=YELLOW_E, stroke_width=2.5)
        full_slice_circle.set_points_smoothly(full_circle_points)

        # 动画：球体自 D1 膨胀切入
        self.play(Create(sphere), run_time=2.5)
        self.play(
            Create(intersection_arc),
            Create(full_slice_circle),
            Flash(O_prime, color=YELLOW, flash_radius=0.5),
            run_time=2.0
        )
        self.wait(2.0)

        # =========================================================================
        # 3. 乐章三：运镜推入至侧面正交投影 (3D 无缝降维至 2D 平面)
        # =========================================================================
        self.stop_ambient_camera_rotation()

        # 弱化不需要的背景棱线与大球体，突出核心侧面与截面圆
        self.play(
            sphere.animate.set_opacity(0.06),
            bottom_edges.animate.set_opacity(0.2),
            side_edges.animate.set_opacity(0.2),
            top_edges.animate.set_opacity(0.2),
            run_time=1.2
        )

        # 计算侧面正对视角的法向量方向
        # 侧面法向为 (1, -SQRT3, 0)
        # 将相机精准旋转至法线方向：theta 设为法线反方向，phi 设为 90°
        # 此时屏幕正面正对侧面矩形 BCC1B1
        self.move_camera(
            phi=90 * DEGREES,
            theta=-120 * DEGREES,
            zoom=1.45,
            frame_center=O_prime + np.array([0, 0, -0.5]),
            run_time=2.8
        )
        self.wait(1.0)

        # 标出垂足中点 O'
        o_dot = Dot3D(point=O_prime, radius=0.08, color=RED_A)
        self.play(FadeIn(o_dot), FadeOut(d1_label), run_time=1.0)

        # 连线圆心到两端交点，展示等腰直角三角形
        p_left = arc_points[0]
        p_right = arc_points[-1]
        radius_l = Line3D(O_prime, p_left, color=ORANGE, thickness=0.035)
        radius_r = Line3D(O_prime, p_right, color=ORANGE, thickness=0.035)

        self.play(
            Create(radius_l), Create(radius_r),
            run_time=1.5
        )

        # =========================================================================
        # 4. 乐章四：几何定量推导与秒杀公式总结
        # =========================================================================
        # 屏幕右侧浮现 2D 公式推导卡片 (固定在画面上)
        calc_card = VGroup(
            Text("【核心量快速秒杀】", font_size=20, weight=BOLD, color=GOLD),
            Text("1. 球心垂距: d = 2 · sin(60°) = √3", font_size=18, color=WHITE),
            Text("2. 截面圆半径: r = √(R² - d²) = √(5 - 3) = √2", font_size=18, color=WHITE),
            Text("3. 侧棱交点中分: 两侧角均为 45°", font_size=18, color=WHITE),
            Text("4. 矩形内圆心角: α = 180° - 45° - 45° = 90° (π/2)", font_size=18, color=YELLOW_B),
            Text("5. 交线长: L = α · r = (π/2) · √2 = (√2/2)π", font_size=20, weight=BOLD, color=GREEN_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_corner(UR, buff=0.5)

        # 背景磨砂半透明框
        card_bg = SurroundingRectangle(calc_card, color=YELLOW_D, buff=0.2, fill_color=BLACK, fill_opacity=0.75, corner_radius=0.15)
        calc_box = VGroup(card_bg, calc_card)
        self.add_fixed_in_frame_mobjects(calc_box)

        self.play(FadeIn(calc_box, shift=LEFT * 0.3), run_time=2.0)
        self.wait(3.0)

        # 镜头微微倾斜拉远，全览定格
        self.move_camera(
            phi=72 * DEGREES,
            theta=-70 * DEGREES,
            zoom=1.1,
            frame_center=np.array([0, 0, 0]),
            run_time=2.5
        )
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(3.0)
