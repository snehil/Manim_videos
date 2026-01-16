from manimlib import *
import numpy as np


# ============================================================================
# TRANSFORMER EXPLAINER - Julia Turc Style
# ============================================================================
# Clean, minimal, focused on intuition over formalism.
# Designed for voiceover - animations sync to narration beats.
# ============================================================================


# Clean color palette
BG_COLOR = "#1a1a2e"
TEXT_COLOR = "#eaeaea"
ACCENT_BLUE = "#4facfe"
ACCENT_PURPLE = "#a855f7"
ACCENT_GOLD = "#fbbf24"
ACCENT_CORAL = "#f472b6"
ACCENT_TEAL = "#2dd4bf"
DIM_COLOR = "#4a4a6a"


class TransformerJuliaStyle(Scene):
    """
    Clean, intuitive transformer explainer.
    Designed to accompany voiceover narration.
    """

    def construct(self):
        self.camera.background_color = BG_COLOR

        # Scene 1: Hook (~10 sec)
        self.hook()

        # Scene 2: The Core Idea (~20 sec)
        self.core_idea()

        # Scene 3: How Attention Works (~25 sec)
        self.attention_example()

        # Scene 4: The Mechanism - Q, K, V (~25 sec)
        self.qkv_mechanism()

        # Scene 5: Multi-Head (~20 sec)
        self.multi_head()

        # Scene 6: Full Picture (~20 sec)
        self.full_picture()

    # ========================================================================
    # SCENE 1: HOOK
    # ========================================================================
    def hook(self):
        """Opening hook - words in, response out."""

        # User message appearing
        user_text = Text("What is the meaning of life?", font_size=32)
        user_text.set_color(TEXT_COLOR)

        # Typing effect
        self.play(Write(user_text), run_time=2.0)
        self.wait(0.5)

        # Transform to processing indicator
        dots = Text("...", font_size=48, color=ACCENT_BLUE)
        dots.next_to(user_text, DOWN, buff=0.5)

        self.play(FadeIn(dots), run_time=0.3)
        self.wait(0.5)

        # Response appears
        response = Text("The meaning of life is a profound question...", font_size=28)
        response.set_color(ACCENT_TEAL)
        response.next_to(dots, DOWN, buff=0.5)

        self.play(
            FadeOut(dots),
            Write(response),
            run_time=1.5
        )
        self.wait(1.0)

        # Transition - "The secret?"
        secret_text = Text("The secret?", font_size=40, color=ACCENT_GOLD)

        self.play(
            FadeOut(user_text),
            FadeOut(response),
            run_time=0.5
        )
        self.play(Write(secret_text), run_time=0.8)
        self.wait(0.5)

        # Reveal: Transformer
        title = Text("The Transformer", font_size=56, weight=BOLD)
        title.set_color_by_gradient(ACCENT_BLUE, ACCENT_PURPLE)

        self.play(
            ReplacementTransform(secret_text, title),
            run_time=1.0
        )
        self.wait(1.5)

        self.play(FadeOut(title), run_time=0.5)

    # ========================================================================
    # SCENE 2: THE CORE IDEA
    # ========================================================================
    def core_idea(self):
        """Every word looks at every other word."""

        # Title
        idea_text = Text("The Core Idea", font_size=36, color=ACCENT_BLUE)
        idea_text.to_edge(UP, buff=0.5)
        self.play(FadeIn(idea_text), run_time=0.5)

        # Show words in a sequence
        words = ["The", "cat", "sat", "on", "the", "mat"]
        word_mobjects = VGroup()

        for word in words:
            w = Text(word, font_size=36, color=TEXT_COLOR)
            word_mobjects.add(w)

        word_mobjects.arrange(RIGHT, buff=0.6)

        self.play(
            LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in word_mobjects], lag_ratio=0.15),
            run_time=1.5
        )
        self.wait(1.0)

        # Old way: sequential arrows (dim)
        old_label = Text("Old way: sequential", font_size=20, color=DIM_COLOR)
        old_label.next_to(word_mobjects, DOWN, buff=1.0)

        seq_arrows = VGroup()
        for i in range(len(word_mobjects) - 1):
            arrow = Arrow(
                word_mobjects[i].get_right(),
                word_mobjects[i + 1].get_left(),
                buff=0.1,
                stroke_width=2,
                color=DIM_COLOR
            )
            seq_arrows.add(arrow)

        self.play(
            FadeIn(old_label),
            LaggedStart(*[GrowArrow(a) for a in seq_arrows], lag_ratio=0.1),
            run_time=1.0
        )
        self.wait(1.0)

        # New way: every word connects to every word
        self.play(
            FadeOut(seq_arrows),
            FadeOut(old_label),
            run_time=0.5
        )

        new_label = Text("Transformer: every word sees every word", font_size=24, color=ACCENT_GOLD)
        new_label.next_to(word_mobjects, DOWN, buff=1.5)

        # Create connection lines (all-to-all)
        connections = VGroup()
        center_word = word_mobjects[2]  # "sat"

        for i, w in enumerate(word_mobjects):
            if i != 2:
                line = Line(
                    center_word.get_center(),
                    w.get_center(),
                    stroke_width=2,
                    stroke_color=ACCENT_BLUE,
                    stroke_opacity=0.6
                )
                connections.add(line)

        # Highlight center word
        highlight = SurroundingRectangle(center_word, color=ACCENT_GOLD, buff=0.1)

        self.play(
            ShowCreation(highlight),
            word_mobjects[2].animate.set_color(ACCENT_GOLD),
            run_time=0.5
        )
        self.play(
            LaggedStart(*[ShowCreation(c) for c in connections], lag_ratio=0.1),
            FadeIn(new_label),
            run_time=1.5
        )
        self.wait(1.5)

        # Key word: ATTENTION
        attention_word = Text("ATTENTION", font_size=48, weight=BOLD, color=ACCENT_PURPLE)
        attention_word.next_to(new_label, DOWN, buff=0.5)

        self.play(Write(attention_word), run_time=1.0)
        self.wait(1.5)

        # Clear
        self.play(
            FadeOut(VGroup(idea_text, word_mobjects, highlight, connections, new_label, attention_word)),
            run_time=0.6
        )

    # ========================================================================
    # SCENE 3: ATTENTION EXAMPLE
    # ========================================================================
    def attention_example(self):
        """Concrete example: which words matter for 'sat'?"""

        # Words
        words = ["The", "cat", "sat", "on", "the", "mat"]
        word_mobjects = VGroup()

        for word in words:
            w = Text(word, font_size=40, color=TEXT_COLOR)
            word_mobjects.add(w)

        word_mobjects.arrange(RIGHT, buff=0.5)
        word_mobjects.shift(UP * 1.5)

        self.play(FadeIn(word_mobjects), run_time=0.8)

        # Highlight 'sat'
        sat_word = word_mobjects[2]
        sat_highlight = SurroundingRectangle(sat_word, color=ACCENT_GOLD, buff=0.1, stroke_width=3)

        question = Text("Processing 'sat' — which words matter?", font_size=24, color=TEXT_COLOR)
        question.next_to(word_mobjects, UP, buff=0.5)

        self.play(
            ShowCreation(sat_highlight),
            sat_word.animate.set_color(ACCENT_GOLD),
            FadeIn(question),
            run_time=1.0
        )
        self.wait(1.5)

        # Show attention weights
        weights = [0.05, 0.5, 0.1, 0.1, 0.05, 0.2]  # cat and mat get high attention
        weight_bars = VGroup()
        weight_labels = VGroup()

        for i, (w, weight) in enumerate(zip(word_mobjects, weights)):
            # Bar
            bar = Rectangle(
                width=0.4,
                height=weight * 3,
                fill_color=ACCENT_BLUE,
                fill_opacity=0.7 + weight * 0.3,
                stroke_width=0
            )
            bar.next_to(w, DOWN, buff=0.3)
            bar.align_to(w, DOWN).shift(DOWN * 0.3)
            weight_bars.add(bar)

            # Label
            label = Text(f"{weight:.0%}", font_size=16, color=TEXT_COLOR)
            label.next_to(bar, DOWN, buff=0.1)
            weight_labels.add(label)

        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in weight_bars], lag_ratio=0.1),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[FadeIn(l) for l in weight_labels], lag_ratio=0.05),
            run_time=0.5
        )
        self.wait(1.0)

        # Highlight high-attention words
        cat_glow = SurroundingRectangle(word_mobjects[1], color=ACCENT_BLUE, buff=0.1)
        mat_glow = SurroundingRectangle(word_mobjects[5], color=ACCENT_TEAL, buff=0.1)

        explanation_cat = Text("'cat' — who's sitting", font_size=20, color=ACCENT_BLUE)
        explanation_mat = Text("'mat' — where", font_size=20, color=ACCENT_TEAL)
        explanation_cat.next_to(weight_bars, DOWN, buff=0.8).shift(LEFT * 2)
        explanation_mat.next_to(explanation_cat, RIGHT, buff=1.5)

        self.play(
            ShowCreation(cat_glow),
            ShowCreation(mat_glow),
            word_mobjects[1].animate.set_color(ACCENT_BLUE),
            word_mobjects[5].animate.set_color(ACCENT_TEAL),
            run_time=0.8
        )
        self.play(
            Write(explanation_cat),
            Write(explanation_mat),
            run_time=1.0
        )
        self.wait(2.0)

        # Clear
        self.play(
            FadeOut(VGroup(
                word_mobjects, sat_highlight, question, weight_bars,
                weight_labels, cat_glow, mat_glow, explanation_cat, explanation_mat
            )),
            run_time=0.6
        )

    # ========================================================================
    # SCENE 4: Q, K, V MECHANISM
    # ========================================================================
    def qkv_mechanism(self):
        """Explain Query, Key, Value."""

        # Single word
        word = Text("sat", font_size=48, color=ACCENT_GOLD)
        word.shift(UP * 2)

        self.play(FadeIn(word), run_time=0.5)
        self.wait(0.5)

        # Three vectors emerge
        q_box = self.create_vector_box("Q", ACCENT_CORAL, "What am I\nlooking for?")
        k_box = self.create_vector_box("K", ACCENT_TEAL, "What do I\ncontain?")
        v_box = self.create_vector_box("V", ACCENT_PURPLE, "What info\ndo I share?")

        q_box.shift(LEFT * 3.5)
        k_box.shift(ORIGIN)
        v_box.shift(RIGHT * 3.5)

        boxes = VGroup(q_box, k_box, v_box)
        boxes.shift(DOWN * 0.5)

        # Arrows from word to boxes
        arrows = VGroup()
        for box in boxes:
            arrow = Arrow(
                word.get_bottom(),
                box[0].get_top(),
                buff=0.2,
                stroke_width=2,
                color=TEXT_COLOR
            )
            arrows.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2),
            run_time=1.0
        )
        self.play(
            LaggedStart(*[FadeIn(b, shift=DOWN * 0.2) for b in boxes], lag_ratio=0.3),
            run_time=1.5
        )
        self.wait(2.0)

        # Show comparison: Q matches with K
        self.play(
            FadeOut(VGroup(word, arrows)),
            boxes.animate.shift(UP * 1.5),
            run_time=0.6
        )

        # Show the process
        process_title = Text("The Attention Process", font_size=28, color=TEXT_COLOR)
        process_title.to_edge(UP, buff=0.4)
        self.play(FadeIn(process_title), run_time=0.5)

        # Step 1: Compare Q and K
        step1 = Text("1. Compare Query with all Keys", font_size=22, color=ACCENT_CORAL)
        step1.next_to(boxes, DOWN, buff=0.8)

        compare_arrow = CurvedArrow(
            q_box.get_right() + RIGHT * 0.1,
            k_box.get_left() + LEFT * 0.1,
            angle=-TAU / 6,
            color=ACCENT_GOLD
        )

        self.play(Write(step1), ShowCreation(compare_arrow), run_time=1.0)
        self.wait(1.0)

        # Step 2: Softmax
        step2 = Text("2. Convert to probabilities (softmax)", font_size=22, color=ACCENT_TEAL)
        step2.next_to(step1, DOWN, buff=0.3)

        self.play(Write(step2), run_time=0.8)
        self.wait(1.0)

        # Step 3: Weighted sum of V
        step3 = Text("3. Weighted sum of Values", font_size=22, color=ACCENT_PURPLE)
        step3.next_to(step2, DOWN, buff=0.3)

        self.play(Write(step3), run_time=0.8)
        self.wait(1.5)

        # Clear
        self.play(
            FadeOut(VGroup(boxes, process_title, step1, step2, step3, compare_arrow)),
            run_time=0.6
        )

    # ========================================================================
    # SCENE 5: MULTI-HEAD
    # ========================================================================
    def multi_head(self):
        """Multiple attention heads in parallel."""

        title = Text("Multi-Head Attention", font_size=36, color=ACCENT_PURPLE)
        title.to_edge(UP, buff=0.5)
        self.play(FadeIn(title), run_time=0.5)

        # Single head
        single_head = self.create_attention_head_simple(ACCENT_BLUE)
        single_head.shift(UP * 0.5)

        single_label = Text("One perspective", font_size=20, color=DIM_COLOR)
        single_label.next_to(single_head, DOWN, buff=0.3)

        self.play(FadeIn(single_head), FadeIn(single_label), run_time=0.8)
        self.wait(1.0)

        # Expand to multiple heads
        self.play(FadeOut(single_label), run_time=0.3)

        head_colors = [ACCENT_CORAL, ACCENT_GOLD, ACCENT_TEAL, ACCENT_BLUE, ACCENT_PURPLE, "#a78bfa", "#f472b6", "#34d399"]
        head_labels = ["grammar", "meaning", "position", "entities", "syntax", "coreference", "sentiment", "logic"]

        heads = VGroup()
        labels = VGroup()

        for i, (color, label_text) in enumerate(zip(head_colors, head_labels)):
            head = self.create_attention_head_simple(color)
            heads.add(head)

            label = Text(label_text, font_size=12, color=color)
            labels.add(label)

        heads.arrange(RIGHT, buff=0.3)
        heads.shift(UP * 0.5)

        for head, label in zip(heads, labels):
            label.next_to(head, DOWN, buff=0.15)

        self.play(
            ReplacementTransform(single_head, heads[3]),
            run_time=0.5
        )
        self.play(
            LaggedStart(*[FadeIn(h, scale=0.8) for i, h in enumerate(heads) if i != 3], lag_ratio=0.1),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.05),
            run_time=0.8
        )
        self.wait(1.5)

        # Show them merging
        merge_text = Text("Combined → richer understanding", font_size=24, color=ACCENT_GOLD)
        merge_text.next_to(labels, DOWN, buff=0.8)

        # Merge lines to center
        merge_point = merge_text.get_top() + UP * 0.3
        merge_lines = VGroup()
        for head in heads:
            line = Line(
                head.get_bottom(),
                merge_point,
                stroke_width=1.5,
                stroke_color=ACCENT_GOLD,
                stroke_opacity=0.5
            )
            merge_lines.add(line)

        self.play(
            LaggedStart(*[ShowCreation(l) for l in merge_lines], lag_ratio=0.05),
            run_time=1.0
        )
        self.play(Write(merge_text), run_time=0.8)
        self.wait(1.5)

        # Clear
        self.play(
            FadeOut(VGroup(title, heads, labels, merge_lines, merge_text)),
            run_time=0.6
        )

    # ========================================================================
    # SCENE 6: FULL PICTURE
    # ========================================================================
    def full_picture(self):
        """The complete transformer architecture."""

        title = Text("The Full Transformer", font_size=36, color=ACCENT_BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(FadeIn(title), run_time=0.5)

        # Build block by block
        # Attention layer
        attn_block = self.create_layer_block("Multi-Head\nAttention", ACCENT_PURPLE)
        attn_block.shift(DOWN * 0.5)

        self.play(FadeIn(attn_block, shift=UP * 0.2), run_time=0.8)
        self.wait(0.5)

        # FFN layer
        ffn_block = self.create_layer_block("Feed\nForward", ACCENT_TEAL)
        ffn_block.next_to(attn_block, UP, buff=0.3)

        connect1 = Arrow(
            attn_block.get_top(),
            ffn_block.get_bottom(),
            buff=0.1,
            stroke_width=2,
            color=TEXT_COLOR
        )

        self.play(
            GrowArrow(connect1),
            FadeIn(ffn_block, shift=UP * 0.2),
            run_time=0.8
        )
        self.wait(0.5)

        # Stack indicator
        stack_label = Text("× N layers", font_size=20, color=DIM_COLOR)
        stack_label.next_to(ffn_block, RIGHT, buff=0.5)

        brace = Brace(VGroup(attn_block, ffn_block), RIGHT, color=DIM_COLOR)

        self.play(
            GrowFromCenter(brace),
            FadeIn(stack_label),
            run_time=0.6
        )
        self.wait(1.0)

        # Input and output
        input_label = Text("Input tokens", font_size=18, color=TEXT_COLOR)
        input_label.next_to(attn_block, DOWN, buff=0.5)

        output_label = Text("Output", font_size=18, color=TEXT_COLOR)
        output_label.next_to(ffn_block, UP, buff=0.5)

        input_arrow = Arrow(input_label.get_top(), attn_block.get_bottom(), buff=0.1, color=TEXT_COLOR, stroke_width=2)
        output_arrow = Arrow(ffn_block.get_top(), output_label.get_bottom(), buff=0.1, color=TEXT_COLOR, stroke_width=2)

        self.play(
            FadeIn(input_label),
            FadeIn(output_label),
            GrowArrow(input_arrow),
            GrowArrow(output_arrow),
            run_time=0.8
        )
        self.wait(1.5)

        # Final message
        self.play(
            VGroup(attn_block, ffn_block, connect1, brace, stack_label, input_label, output_label, input_arrow, output_arrow).animate.scale(0.7).shift(UP * 0.5),
            run_time=0.8
        )

        final_text = Text("Attention Is All You Need", font_size=40, weight=BOLD)
        final_text.set_color_by_gradient(ACCENT_BLUE, ACCENT_PURPLE)
        final_text.to_edge(DOWN, buff=1.0)

        self.play(Write(final_text), run_time=1.5)
        self.wait(2.0)

        # Fade out
        self.play(
            FadeOut(VGroup(title, attn_block, ffn_block, connect1, brace, stack_label, input_label, output_label, input_arrow, output_arrow, final_text)),
            run_time=1.5
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def create_vector_box(self, letter, color, description):
        """Create a labeled vector box with description."""
        box = RoundedRectangle(
            width=1.8,
            height=1.2,
            corner_radius=0.15,
            fill_color=color,
            fill_opacity=0.2,
            stroke_color=color,
            stroke_width=2
        )

        letter_text = Text(letter, font_size=36, weight=BOLD, color=color)
        letter_text.move_to(box.get_center())

        desc = Text(description, font_size=14, color=TEXT_COLOR)
        desc.next_to(box, DOWN, buff=0.2)

        return VGroup(box, letter_text, desc)

    def create_attention_head_simple(self, color):
        """Create a simple attention head visualization."""
        circle = Circle(
            radius=0.35,
            fill_color=color,
            fill_opacity=0.3,
            stroke_color=color,
            stroke_width=2
        )

        # Simple internal pattern
        lines = VGroup()
        for i in range(3):
            line = Line(LEFT * 0.15, RIGHT * 0.15, stroke_width=1.5, stroke_color=color)
            line.shift(UP * (i - 1) * 0.12)
            lines.add(line)

        return VGroup(circle, lines)

    def create_layer_block(self, text, color):
        """Create a transformer layer block."""
        box = RoundedRectangle(
            width=2.5,
            height=1.0,
            corner_radius=0.15,
            fill_color=color,
            fill_opacity=0.2,
            stroke_color=color,
            stroke_width=2
        )

        label = Text(text, font_size=16, color=TEXT_COLOR)
        label.move_to(box.get_center())

        return VGroup(box, label)
