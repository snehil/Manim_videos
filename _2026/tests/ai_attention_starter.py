from manim_imports_ext import *


class AttentionBasics(InteractiveScene):
    """
    A starter scene demonstrating self-attention in transformers.
    Run with: manimgl ai_attention_starter.py AttentionBasics -p
    """

    def construct(self):
        # Setup sentence
        sentence = "The cat sat on the mat"
        words = sentence.split()

        # Create word mobjects
        word_mobs = VGroup(*[Text(word, font_size=48) for word in words])
        word_mobs.arrange(RIGHT, buff=0.5)
        word_mobs.move_to(2 * UP)

        self.play(LaggedStartMap(FadeIn, word_mobs, shift=0.5 * UP, lag_ratio=0.1))
        self.wait()

        # Add rectangles around each word
        word_rects = VGroup(*[
            SurroundingRectangle(word, buff=0.1)
            .set_stroke(GREY, 2)
            .set_fill(GREY, 0.2)
            for word in word_mobs
        ])

        self.play(LaggedStartMap(FadeIn, word_rects, lag_ratio=0.1))
        self.wait()

        # Show attention from "cat" to other words
        # Attention weights (made up for illustration)
        cat_idx = 1
        attention_weights = [0.1, 0.0, 0.6, 0.05, 0.05, 0.2]  # cat attends to "sat" and "mat"

        # Create attention arrows with varying thickness
        attention_arrows = VGroup()
        for i, weight in enumerate(attention_weights):
            if i == cat_idx or weight < 0.05:
                continue
            arrow = Arrow(
                word_mobs[cat_idx].get_bottom(),
                word_mobs[i].get_bottom(),
                path_arc=-120 * DEGREES if i > cat_idx else 120 * DEGREES,
                stroke_width=weight * 8,
                stroke_color=interpolate_color(BLUE_E, BLUE_A, weight),
                buff=0.1
            )
            attention_arrows.add(arrow)

        # Highlight the query word
        query_rect = word_rects[cat_idx].copy()
        query_rect.set_stroke(YELLOW, 3)
        query_label = Text("Query", font_size=24, color=YELLOW)
        query_label.next_to(query_rect, UP, buff=0.1)

        self.play(
            ShowCreation(query_rect),
            FadeIn(query_label, shift=0.2 * UP)
        )
        self.wait()

        self.play(LaggedStartMap(ShowCreation, attention_arrows, lag_ratio=0.2))
        self.wait()

        # Show attention matrix
        self.play(
            FadeOut(attention_arrows),
            FadeOut(query_rect),
            FadeOut(query_label)
        )

        # Create attention matrix visualization
        n = len(words)
        # Generate random-ish attention pattern (row-normalized)
        np.random.seed(42)
        attention_matrix = np.random.rand(n, n)
        attention_matrix = attention_matrix / attention_matrix.sum(axis=1, keepdims=True)

        # Create matrix of squares
        cell_size = 0.5
        matrix_group = VGroup()
        for i in range(n):
            row = VGroup()
            for j in range(n):
                cell = Square(cell_size)
                cell.set_stroke(WHITE, 0.5)
                weight = attention_matrix[i, j]
                cell.set_fill(BLUE, opacity=weight)
                row.add(cell)
            row.arrange(RIGHT, buff=0)
            matrix_group.add(row)
        matrix_group.arrange(DOWN, buff=0)
        matrix_group.move_to(DOWN)

        # Add labels
        row_labels = VGroup(*[
            Text(word, font_size=20).next_to(matrix_group[i], LEFT, buff=0.2)
            for i, word in enumerate(words)
        ])
        col_labels = VGroup(*[
            Text(word, font_size=20).rotate(45 * DEGREES).next_to(matrix_group[0][j], UP, buff=0.2)
            for j, word in enumerate(words)
        ])

        matrix_title = Text("Attention Matrix", font_size=36)
        matrix_title.next_to(matrix_group, UP, buff=1.0)

        self.play(
            FadeIn(matrix_title),
            LaggedStartMap(FadeIn, matrix_group, lag_ratio=0.02),
            LaggedStartMap(FadeIn, row_labels, lag_ratio=0.05),
            LaggedStartMap(FadeIn, col_labels, lag_ratio=0.05),
        )
        self.wait()

        # Highlight a row to show how one word attends to others
        highlight_idx = 1  # "cat"
        row_highlight = SurroundingRectangle(matrix_group[highlight_idx], buff=0.05)
        row_highlight.set_stroke(YELLOW, 3)

        explanation = Text(
            f'"{words[highlight_idx]}" attends to all other words',
            font_size=28
        )
        explanation.next_to(matrix_group, DOWN, buff=0.5)

        self.play(
            ShowCreation(row_highlight),
            FadeIn(explanation, shift=0.2 * DOWN)
        )
        self.wait(2)


class QueryKeyValue(InteractiveScene):
    """
    Visualize the Query, Key, Value mechanism.
    Run with: manimgl ai_attention_starter.py QueryKeyValue -p
    """

    def construct(self):
        # Title
        title = Text("Query, Key, Value", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Create a single word embedding
        word = Text("cat", font_size=36)
        word.move_to(3 * LEFT + UP)

        embedding_label = Text("Embedding", font_size=24)
        embedding = self.create_vector(8, color=GREY_B)
        embedding.next_to(word, DOWN, buff=0.5)
        embedding_label.next_to(embedding, DOWN, buff=0.1)

        self.play(
            FadeIn(word),
            FadeIn(embedding),
            FadeIn(embedding_label)
        )
        self.wait()

        # Show Q, K, V transformations
        q_vec = self.create_vector(6, color=RED)
        k_vec = self.create_vector(6, color=GREEN)
        v_vec = self.create_vector(6, color=BLUE)

        qkv_group = VGroup(q_vec, k_vec, v_vec)
        qkv_group.arrange(RIGHT, buff=1.5)
        qkv_group.move_to(2 * RIGHT)

        q_label = Text("Query", font_size=24, color=RED)
        k_label = Text("Key", font_size=24, color=GREEN)
        v_label = Text("Value", font_size=24, color=BLUE)

        q_label.next_to(q_vec, DOWN, buff=0.1)
        k_label.next_to(k_vec, DOWN, buff=0.1)
        v_label.next_to(v_vec, DOWN, buff=0.1)

        # Arrows from embedding to Q, K, V
        arrows = VGroup(*[
            Arrow(
                embedding.get_right(),
                vec.get_left(),
                buff=0.2,
                stroke_color=vec[0].get_fill_color()
            )
            for vec in [q_vec, k_vec, v_vec]
        ])

        # Matrix labels (using Text since LaTeX not installed)
        wq = Text("Wq", font_size=28, color=RED)
        wk = Text("Wk", font_size=28, color=GREEN)
        wv = Text("Wv", font_size=28, color=BLUE)

        for label, arrow in zip([wq, wk, wv], arrows):
            label.next_to(arrow, UP, buff=0.05)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2),
            LaggedStart(*[FadeIn(l) for l in [wq, wk, wv]], lag_ratio=0.2),
        )
        self.play(
            LaggedStart(
                *[FadeIn(v, shift=0.3 * RIGHT) for v in [q_vec, k_vec, v_vec]],
                lag_ratio=0.2
            ),
            LaggedStart(
                *[FadeIn(l) for l in [q_label, k_label, v_label]],
                lag_ratio=0.2
            ),
        )
        self.wait()

        # Explanation
        explanation = VGroup(
            Text("Query: What am I looking for?", font_size=24),
            Text("Key: What do I contain?", font_size=24),
            Text("Value: What information do I provide?", font_size=24),
        )
        explanation.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation.to_edge(DOWN, buff=0.5)
        explanation[0].set_color(RED)
        explanation[1].set_color(GREEN)
        explanation[2].set_color(BLUE)

        self.play(LaggedStartMap(FadeIn, explanation, shift=0.2 * UP, lag_ratio=0.3))
        self.wait(2)

    def create_vector(self, length, color=WHITE):
        """Create a simple vector visualization."""
        cells = VGroup(*[
            Square(0.3).set_stroke(WHITE, 1).set_fill(color, opacity=np.random.random())
            for _ in range(length)
        ])
        cells.arrange(DOWN, buff=0)
        bracket_l = Text("[", font_size=48).stretch(length * 0.4, 1).next_to(cells, LEFT, buff=0.05)
        bracket_r = Text("]", font_size=48).stretch(length * 0.4, 1).next_to(cells, RIGHT, buff=0.05)
        return VGroup(cells, bracket_l, bracket_r)


class AttentionScoreComputation(InteractiveScene):
    """
    Show how attention scores are computed via dot products.
    Run with: manimgl ai_attention_starter.py AttentionScoreComputation -p
    """

    def construct(self):
        # Setup: Two words
        word1 = Text("cat", font_size=36, color=RED)
        word2 = Text("sat", font_size=36, color=GREEN)
        word1.move_to(3 * LEFT + 2 * UP)
        word2.move_to(3 * RIGHT + 2 * UP)

        # Query from word1, Key from word2
        q_label = Text("Query", font_size=24, color=RED)
        k_label = Text("Key", font_size=24, color=GREEN)

        q_vec = self.create_simple_vector([0.8, 0.3, 0.5, 0.1], RED)
        k_vec = self.create_simple_vector([0.6, 0.4, 0.7, 0.2], GREEN)

        q_vec.next_to(word1, DOWN, buff=0.5)
        k_vec.next_to(word2, DOWN, buff=0.5)
        q_label.next_to(q_vec, DOWN, buff=0.1)
        k_label.next_to(k_vec, DOWN, buff=0.1)

        self.play(
            FadeIn(word1), FadeIn(word2),
            FadeIn(q_vec), FadeIn(k_vec),
            FadeIn(q_label), FadeIn(k_label),
        )
        self.wait()

        # Show dot product computation (using Text since LaTeX not installed)
        dot_product_tex = Text("Q · K = ", font_size=36)
        dot_product_tex.move_to(DOWN)

        # Animated multiplication
        values_q = [0.8, 0.3, 0.5, 0.1]
        values_k = [0.6, 0.4, 0.7, 0.2]
        products = [q * k for q, k in zip(values_q, values_k)]
        result = sum(products)

        computation = Text(
            "0.8×0.6 + 0.3×0.4 + 0.5×0.7 + 0.1×0.2",
            font_size=24
        )
        computation.next_to(dot_product_tex, RIGHT)

        result_tex = Text(f"= {result:.2f}", font_size=36)
        result_tex.next_to(computation, RIGHT)

        self.play(Write(dot_product_tex))
        self.play(Write(computation))
        self.wait()
        self.play(Write(result_tex))
        self.wait()

        # Show this becomes attention weight after softmax
        softmax_note = Text(
            "→ Apply softmax across all keys to get attention weights",
            font_size=24
        )
        softmax_note.next_to(VGroup(dot_product_tex, computation, result_tex), DOWN, buff=0.5)

        self.play(FadeIn(softmax_note, shift=0.2 * DOWN))
        self.wait(2)

    def create_simple_vector(self, values, color):
        """Create a simple vertical vector with numeric values."""
        cells = VGroup()
        for val in values:
            cell = Square(0.4)
            cell.set_stroke(WHITE, 1)
            cell.set_fill(color, opacity=val)
            num = DecimalNumber(val, num_decimal_places=1, font_size=20)
            num.move_to(cell)
            cells.add(VGroup(cell, num))
        cells.arrange(DOWN, buff=0)
        return cells
