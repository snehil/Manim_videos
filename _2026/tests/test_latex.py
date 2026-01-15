from manimlib import *


class TestLaTeX(Scene):
    """Quick test to verify LaTeX rendering works"""

    def construct(self):
        # Create title
        title = Text("LaTeX Rendering Test", font_size=48)
        title.to_edge(UP)

        # Create some LaTeX formulas
        formula1 = Tex(R"E = mc^2")
        formula1.scale(2)

        formula2 = Tex(R"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}")
        formula2.next_to(formula1, DOWN, buff=0.5)

        formula3 = Tex(R"\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}")
        formula3.next_to(formula2, DOWN, buff=0.5)

        # Animate
        self.play(Write(title))
        self.wait(0.5)

        self.play(Write(formula1))
        self.wait(0.5)

        self.play(Write(formula2))
        self.wait(0.5)

        self.play(Write(formula3))
        self.wait(1)
