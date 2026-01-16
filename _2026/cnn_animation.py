from manimlib import *


class CNNExplainer(Scene):
    """15-second animation explaining how a CNN works"""

    def construct(self):
        # Title
        title = Text("How a CNN Works", font_size=42)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.5)

        # Create input image (simplified as a grid)
        input_label = Text("Input Image", font_size=24)
        input_grid = self.create_grid(5, 5, 0.4, BLUE_D)
        input_group = VGroup(input_grid, input_label)
        input_label.next_to(input_grid, DOWN, buff=0.2)
        input_group.move_to(LEFT * 5)

        self.play(FadeIn(input_group), run_time=0.5)

        # Create convolutional filter (kernel)
        filter_label = Text("Filter", font_size=20)
        conv_filter = self.create_grid(3, 3, 0.4, YELLOW)
        conv_filter.move_to(input_grid.get_center() + UP * 0.4 + LEFT * 0.4)
        filter_label.next_to(conv_filter, UP, buff=0.1)

        self.play(FadeIn(conv_filter), FadeIn(filter_label), run_time=0.4)

        # Animate filter sliding across input
        self.play(
            conv_filter.animate.shift(RIGHT * 0.8),
            filter_label.animate.shift(RIGHT * 0.8),
            run_time=0.3
        )
        self.play(
            conv_filter.animate.shift(RIGHT * 0.8),
            filter_label.animate.shift(RIGHT * 0.8),
            run_time=0.3
        )
        self.play(
            conv_filter.animate.shift(DOWN * 0.8 + LEFT * 1.6),
            filter_label.animate.shift(DOWN * 0.8 + LEFT * 1.6),
            run_time=0.3
        )

        # Feature map appears
        feature_label = Text("Feature Map", font_size=24)
        feature_grid = self.create_grid(3, 3, 0.4, GREEN)
        feature_group = VGroup(feature_grid, feature_label)
        feature_label.next_to(feature_grid, DOWN, buff=0.2)
        feature_group.move_to(LEFT * 1.5)

        # Arrow from input to feature map
        arrow1 = Arrow(
            input_grid.get_right() + RIGHT * 0.2,
            feature_grid.get_left() + LEFT * 0.2,
            buff=0.1,
            stroke_width=3
        )
        conv_text = Text("Convolution", font_size=18)
        conv_text.next_to(arrow1, UP, buff=0.1)

        self.play(
            FadeOut(conv_filter),
            FadeOut(filter_label),
            GrowArrow(arrow1),
            FadeIn(conv_text),
            run_time=0.4
        )
        self.play(FadeIn(feature_group), run_time=0.4)

        # Pooling layer
        pooling_label = Text("Pooled", font_size=24)
        pooled_grid = self.create_grid(2, 2, 0.5, ORANGE)
        pooled_group = VGroup(pooled_grid, pooling_label)
        pooling_label.next_to(pooled_grid, DOWN, buff=0.2)
        pooled_group.move_to(RIGHT * 1.5)

        arrow2 = Arrow(
            feature_grid.get_right() + RIGHT * 0.2,
            pooled_grid.get_left() + LEFT * 0.2,
            buff=0.1,
            stroke_width=3
        )
        pool_text = Text("Max Pool", font_size=18)
        pool_text.next_to(arrow2, UP, buff=0.1)

        self.play(GrowArrow(arrow2), FadeIn(pool_text), run_time=0.4)
        self.play(FadeIn(pooled_group), run_time=0.4)

        # Flatten indicator
        flatten_dots = VGroup(*[
            Dot(radius=0.08, color=ORANGE).shift(DOWN * i * 0.25)
            for i in range(4)
        ])
        flatten_dots.move_to(RIGHT * 3.5)
        flatten_label = Text("Flatten", font_size=18)
        flatten_label.next_to(flatten_dots, DOWN, buff=0.2)

        arrow3 = Arrow(
            pooled_grid.get_right() + RIGHT * 0.2,
            flatten_dots.get_left() + LEFT * 0.2,
            buff=0.1,
            stroke_width=3
        )

        self.play(GrowArrow(arrow3), run_time=0.3)
        self.play(FadeIn(flatten_dots), FadeIn(flatten_label), run_time=0.4)

        # Fully connected layer
        fc_layer = VGroup(*[
            Dot(radius=0.1, color=RED).shift(DOWN * i * 0.35)
            for i in range(3)
        ])
        fc_layer.move_to(RIGHT * 5)
        fc_label = Text("Output", font_size=20)
        fc_label.next_to(fc_layer, DOWN, buff=0.2)

        # Draw connections
        connections = VGroup()
        for flat_dot in flatten_dots:
            for fc_dot in fc_layer:
                line = Line(
                    flat_dot.get_center(),
                    fc_dot.get_center(),
                    stroke_width=1,
                    stroke_opacity=0.4,
                    color=WHITE
                )
                connections.add(line)

        arrow4 = Arrow(
            flatten_dots.get_right() + RIGHT * 0.15,
            fc_layer.get_left() + LEFT * 0.15,
            buff=0.05,
            stroke_width=3
        )
        fc_text = Text("Dense", font_size=18)
        fc_text.next_to(arrow4, UP, buff=0.1)

        self.play(
            GrowArrow(arrow4),
            FadeIn(fc_text),
            run_time=0.3
        )
        self.play(
            FadeIn(fc_layer),
            FadeIn(fc_label),
            ShowCreation(connections, lag_ratio=0.02),
            run_time=0.6
        )

        # Highlight output classification
        output_labels = VGroup(
            Text("Cat", font_size=16, color=GREEN),
            Text("Dog", font_size=16),
            Text("Bird", font_size=16),
        )
        for i, label in enumerate(output_labels):
            label.next_to(fc_layer[i], RIGHT, buff=0.15)

        self.play(FadeIn(output_labels, lag_ratio=0.2), run_time=0.8)

        # Highlight the "Cat" prediction
        highlight = SurroundingRectangle(
            VGroup(fc_layer[0], output_labels[0]),
            color=GREEN,
            buff=0.1
        )
        self.play(ShowCreation(highlight), run_time=0.6)
        self.wait(0.5)

        # Final summary text
        summary = Text(
            "CNN: Extract features → Reduce dimensions → Classify",
            font_size=22,
            color=YELLOW
        )
        summary.to_edge(DOWN, buff=0.4)
        self.play(Write(summary), run_time=1.5)

        self.wait(4)

    def create_grid(self, rows, cols, cell_size, color):
        """Create a grid of squares"""
        grid = VGroup()
        for i in range(rows):
            for j in range(cols):
                square = Square(side_length=cell_size)
                square.set_stroke(color, width=2)
                square.set_fill(color, opacity=0.3)
                square.shift(RIGHT * j * cell_size + DOWN * i * cell_size)
                grid.add(square)
        grid.move_to(ORIGIN)
        return grid
