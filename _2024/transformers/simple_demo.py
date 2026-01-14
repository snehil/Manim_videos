from manim_imports_ext import *


class SimpleTransformerDemo(InteractiveScene):
    """A simple demo scene without LaTeX dependencies"""

    def construct(self):
        # Create title
        title = Text("Transformer Architecture Demo", font_size=48)
        title.to_edge(UP)
        title.set_color(BLUE)

        # Create some boxes to represent components
        encoder = Rectangle(width=3, height=4, fill_opacity=0.3, fill_color=BLUE)
        encoder.shift(LEFT * 3.5)
        encoder_label = Text("Encoder", font_size=32)
        encoder_label.next_to(encoder, DOWN)

        decoder = Rectangle(width=3, height=4, fill_opacity=0.3, fill_color=GREEN)
        decoder.shift(RIGHT * 3.5)
        decoder_label = Text("Decoder", font_size=32)
        decoder_label.next_to(decoder, DOWN)

        # Arrow between them
        arrow = Arrow(encoder.get_right(), decoder.get_left(), buff=0.3)
        arrow.set_color(YELLOW)

        # Attention mechanism visualization
        attention_circles = VGroup(*[
            Circle(radius=0.3, fill_opacity=0.5, fill_color=RED)
            .shift(UP * (1.5 - i) + LEFT * 3.5)
            for i in range(4)
        ])

        # Animate
        self.play(Write(title))
        self.wait(0.5)

        self.play(
            ShowCreation(encoder),
            ShowCreation(decoder)
        )
        self.wait(0.3)

        self.play(
            Write(encoder_label),
            Write(decoder_label)
        )
        self.wait(0.5)

        self.play(GrowArrow(arrow))
        self.wait(0.5)

        self.play(LaggedStart(*[
            FadeIn(circle, scale=0.5)
            for circle in attention_circles
        ], lag_ratio=0.2))
        self.wait(1)

        # Pulse animation
        self.play(LaggedStart(*[
            circle.animate.scale(1.3).set_color(YELLOW)
            for circle in attention_circles
        ], lag_ratio=0.1))
        self.play(LaggedStart(*[
            circle.animate.scale(1/1.3).set_color(RED)
            for circle in attention_circles
        ], lag_ratio=0.1))
        self.wait(1)
