from manimlib import *


class SimpleTest(Scene):
    def construct(self):
        # Create a yellow circle
        circle = Circle()
        circle.set_fill(YELLOW, opacity=1.0)
        circle.set_stroke(YELLOW, width=4)

        # Just add it without animation to test basic functionality
        self.add(circle)
        print("✓ Scene constructed successfully!")
        print("✓ Yellow circle created and added to scene")
        print("✓ ManimGL installation is working!")
