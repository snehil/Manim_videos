from manimlib import *


class YellowCircle(Scene):
    def construct(self):
        # Create a yellow circle
        circle = Circle()
        circle.set_fill(YELLOW, opacity=1.0)
        circle.set_stroke(YELLOW, width=4)

        # Add title
        title = Text("Yellow Circle Test", font_size=48)
        title.to_edge(UP)

        # Animate
        self.play(Write(title))
        self.wait(0.5)
        self.play(ShowCreation(circle))
        self.wait(1)
        self.play(circle.animate.scale(1.5))
        self.wait(0.5)
        self.play(circle.animate.scale(1/1.5))
        self.wait(1)
