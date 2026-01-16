from manimlib import *
import numpy as np


# ============================================================================
# PREMIUM TRANSFORMER EXPLAINER - 2 Minutes
# ============================================================================
# A visually stunning, diagram-heavy explanation of the Transformer
# architecture with beautiful 3D effects and premium animations.
# Target: High-end studio quality ($10,000+ production value)
# ============================================================================


# Premium color palette - sophisticated and cohesive
ACCENT_BLUE = "#4A90D9"
ACCENT_PURPLE = "#9B59B6"
ACCENT_GOLD = "#F4D03F"
ACCENT_TEAL = "#1ABC9C"
ACCENT_CORAL = "#E74C3C"
ACCENT_PINK = "#E91E63"
DEEP_BLUE = "#2C3E50"
SOFT_WHITE = "#ECF0F1"
GLOW_BLUE = "#00D4FF"
GLOW_PURPLE = "#A855F7"


class TransformerExplainer(Scene):
    """
    Premium 2-minute transformer explainer with stunning 3D visuals.
    Diagram-heavy, minimal text, maximum visual impact.
    """

    def construct(self):
        # Set dark background for premium feel
        self.camera.background_color = "#0D1117"

        # Segment 1: Cinematic Opening (~15 seconds)
        self.cinematic_intro()

        # Segment 2: Token Flow Visualization (~20 seconds)
        self.token_flow_3d()

        # Segment 3: Self-Attention Matrix (~30 seconds)
        self.attention_matrix_visualization()

        # Segment 4: Multi-Head Attention 3D (~25 seconds)
        self.multihead_3d()

        # Segment 5: Full Architecture Reveal (~25 seconds)
        self.architecture_reveal()

        # Segment 6: Cinematic Outro (~5 seconds)
        self.cinematic_outro()

    # ========================================================================
    # SEGMENT 1: CINEMATIC INTRO
    # ========================================================================
    def cinematic_intro(self):
        """Stunning opening with particle effects and 3D title."""

        # Create floating particles in background
        particles = self.create_particle_field(50)
        self.add(particles)

        # Animate particles floating
        self.play(
            particles.animate.shift(UP * 0.3),
            rate_func=linear,
            run_time=2.0
        )

        # Main title with glow effect
        title = Text("TRANSFORMER", font_size=72, weight=BOLD)
        title.set_color_by_gradient(GLOW_BLUE, GLOW_PURPLE)

        # Glow rectangle behind title
        glow = Rectangle(
            width=title.get_width() + 1,
            height=title.get_height() + 0.5,
            fill_opacity=0.1,
            fill_color=GLOW_BLUE,
            stroke_width=0
        )
        glow.move_to(title)

        # Subtitle
        subtitle = Text("The Architecture That Changed Everything", font_size=24)
        subtitle.set_color(SOFT_WHITE)
        subtitle.set_opacity(0.7)
        subtitle.next_to(title, DOWN, buff=0.4)

        # Animated entry
        self.play(
            FadeIn(glow, scale=1.5),
            Write(title, run_time=2.5),
        )
        self.play(
            FadeIn(subtitle, shift=UP * 0.2),
            run_time=1.2
        )
        self.wait(2.5)

        # Create neural network hint in background
        network_hint = self.create_network_background()
        network_hint.set_opacity(0.15)

        self.play(
            FadeIn(network_hint),
            particles.animate.set_opacity(0.3),
            run_time=1.5
        )
        self.wait(1.5)

        # Transition out
        self.play(
            FadeOut(VGroup(title, subtitle, glow)),
            network_hint.animate.set_opacity(0.05),
            run_time=1.2
        )

        self.network_bg = network_hint
        self.particles = particles

    # ========================================================================
    # SEGMENT 2: TOKEN FLOW 3D
    # ========================================================================
    def token_flow_3d(self):
        """Show tokens flowing through embedding with 3D depth."""

        # Input tokens as 3D-style cubes
        tokens_text = ["The", "cat", "sat", "on", "mat"]
        token_cubes = VGroup()

        for i, text in enumerate(tokens_text):
            cube = self.create_3d_token(text, i)
            token_cubes.add(cube)

        token_cubes.arrange(RIGHT, buff=0.6)
        token_cubes.shift(UP * 2)

        # Animate tokens appearing with depth effect
        self.play(
            LaggedStart(
                *[self.create_token_entrance(cube) for cube in token_cubes],
                lag_ratio=0.2
            ),
            run_time=2.5
        )
        self.wait(1.5)

        # Show embedding transformation
        embed_label = Text("EMBEDDING", font_size=20, weight=BOLD)
        embed_label.set_color(ACCENT_BLUE)
        embed_label.shift(UP * 0.5)

        # Create embedding vectors (vertical bars with gradient)
        embed_vectors = VGroup()
        for i, cube in enumerate(token_cubes):
            vec = self.create_embedding_bar(i)
            vec.next_to(cube, DOWN, buff=0.8)
            embed_vectors.add(vec)

        # Transformation arrows
        arrows = VGroup()
        for cube, vec in zip(token_cubes, embed_vectors):
            arrow = Arrow(
                cube.get_bottom(),
                vec.get_top(),
                buff=0.15,
                stroke_width=2,
                color=ACCENT_BLUE
            )
            arrow.set_opacity(0.6)
            arrows.add(arrow)

        self.play(
            FadeIn(embed_label),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15),
            run_time=1.8
        )
        self.play(
            LaggedStart(
                *[GrowFromEdge(v, UP) for v in embed_vectors],
                lag_ratio=0.15
            ),
            run_time=2.0
        )
        self.wait(1.5)

        # Add positional encoding wave
        pos_wave = self.create_positional_wave()
        pos_wave.shift(DOWN * 1.5)

        pos_label = Text("+ POSITION", font_size=18, color=ACCENT_GOLD)
        pos_label.next_to(pos_wave, LEFT, buff=0.3)

        self.play(
            ShowCreation(pos_wave),
            FadeIn(pos_label),
            run_time=1.5
        )
        self.wait(1.0)

        # Merge into final embeddings
        self.play(
            embed_vectors.animate.set_color_by_gradient(ACCENT_TEAL, ACCENT_BLUE),
            pos_wave.animate.set_opacity(0),
            FadeOut(pos_label),
            run_time=1.2
        )
        self.wait(0.8)

        # Store and transition
        self.play(
            FadeOut(VGroup(token_cubes, arrows, embed_label)),
            embed_vectors.animate.shift(UP * 2.5).scale(0.8),
            run_time=1.2
        )

        self.embed_vectors = embed_vectors

    # ========================================================================
    # SEGMENT 3: ATTENTION MATRIX VISUALIZATION
    # ========================================================================
    def attention_matrix_visualization(self):
        """Beautiful attention matrix with animated connections."""

        # Title
        attn_title = Text("SELF-ATTENTION", font_size=28, weight=BOLD)
        attn_title.set_color_by_gradient(ACCENT_GOLD, ACCENT_CORAL)
        attn_title.to_edge(UP, buff=0.5)

        self.play(
            Write(attn_title),
            self.embed_vectors.animate.to_edge(LEFT, buff=1.0).shift(DOWN * 0.5),
            run_time=1.2
        )
        self.wait(0.5)

        # Create attention matrix
        matrix_size = 5
        attention_matrix = self.create_attention_matrix(matrix_size)
        attention_matrix.scale(0.9)
        attention_matrix.shift(RIGHT * 1.5)

        # Q, K, V labels
        q_label = Text("Q", font_size=36, weight=BOLD, color=ACCENT_CORAL)
        k_label = Text("K", font_size=36, weight=BOLD, color=ACCENT_TEAL)
        v_label = Text("V", font_size=36, weight=BOLD, color=ACCENT_PURPLE)

        q_label.next_to(attention_matrix, LEFT, buff=0.8)
        k_label.next_to(attention_matrix, UP, buff=0.3)
        v_label.next_to(attention_matrix, RIGHT, buff=0.8)

        # Animate matrix appearing cell by cell
        self.play(
            LaggedStart(
                *[FadeIn(cell, scale=0.5) for row in attention_matrix for cell in row],
                lag_ratio=0.03
            ),
            run_time=2.5
        )
        self.wait(1.0)

        self.play(
            FadeIn(q_label, shift=RIGHT * 0.2),
            FadeIn(k_label, shift=DOWN * 0.2),
            FadeIn(v_label, shift=LEFT * 0.2),
            run_time=1.0
        )
        self.wait(1.0)

        # Highlight attention pattern - show "cat" attending
        highlight_row = 1  # "cat" row
        row_highlight = VGroup()
        for j, cell in enumerate(attention_matrix[highlight_row]):
            glow = cell.copy()
            glow.set_fill(ACCENT_GOLD, opacity=0.4)
            glow.set_stroke(ACCENT_GOLD, width=2)
            row_highlight.add(glow)

        self.play(
            FadeIn(row_highlight),
            run_time=0.8
        )
        self.wait(1.0)

        # Show attention flow with animated lines
        source_vec = self.embed_vectors[1]  # "cat"
        attention_lines = VGroup()
        weights = [0.1, 0.6, 0.15, 0.1, 0.05]

        for i, (target_vec, weight) in enumerate(zip(self.embed_vectors, weights)):
            line = Line(
                source_vec.get_right() + RIGHT * 0.1,
                target_vec.get_right() + RIGHT * 0.1 + RIGHT * 5,
                stroke_width=weight * 8,
                stroke_color=ACCENT_GOLD,
                stroke_opacity=weight + 0.2
            )
            line.set_path_arc(0.3 * (i - 1))
            attention_lines.add(line)

        self.play(
            LaggedStart(*[ShowCreation(line) for line in attention_lines], lag_ratio=0.15),
            run_time=2.0
        )
        self.wait(1.5)

        # Formula overlay (minimal, elegant)
        formula = Tex(
            R"\text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) \cdot V",
            font_size=32
        )
        formula.set_color(SOFT_WHITE)
        formula.to_edge(DOWN, buff=0.6)

        formula_bg = Rectangle(
            width=formula.get_width() + 0.6,
            height=formula.get_height() + 0.3,
            fill_color=DEEP_BLUE,
            fill_opacity=0.8,
            stroke_width=0
        )
        formula_bg.move_to(formula)

        self.play(
            FadeIn(formula_bg),
            Write(formula),
            run_time=1.5
        )
        self.wait(2.5)

        # Clear for next section
        self.play(
            FadeOut(VGroup(
                attn_title, attention_matrix, q_label, k_label, v_label,
                row_highlight, attention_lines, formula, formula_bg,
                self.embed_vectors
            )),
            run_time=1.0
        )

    # ========================================================================
    # SEGMENT 4: MULTI-HEAD 3D
    # ========================================================================
    def multihead_3d(self):
        """Stunning multi-head attention with 3D layered effect."""

        # Title
        mh_title = Text("MULTI-HEAD ATTENTION", font_size=28, weight=BOLD)
        mh_title.set_color_by_gradient(ACCENT_PURPLE, ACCENT_PINK)
        mh_title.to_edge(UP, buff=0.5)

        self.play(Write(mh_title), run_time=1.2)
        self.wait(0.5)

        # Create layered attention heads with 3D depth
        head_colors = [
            ACCENT_CORAL, ACCENT_GOLD, ACCENT_TEAL, ACCENT_BLUE,
            ACCENT_PURPLE, ACCENT_PINK, "#FF6B6B", "#4ECDC4"
        ]

        heads_group = VGroup()
        for i, color in enumerate(head_colors):
            head = self.create_attention_head(color, i)
            heads_group.add(head)

        # Arrange in 3D-like perspective (stacked with offset)
        for i, head in enumerate(heads_group):
            head.shift(RIGHT * (i * 0.15) + UP * (i * 0.08))

        heads_group.center()

        # Animate heads appearing with stagger
        self.play(
            LaggedStart(
                *[FadeIn(head, shift=LEFT * 0.3 + DOWN * 0.1, scale=0.9) for head in heads_group],
                lag_ratio=0.15
            ),
            run_time=2.5
        )
        self.wait(1.5)

        # Show heads "focusing" on different things
        focus_labels = VGroup(
            Text("syntax", font_size=14, color=head_colors[0]),
            Text("semantics", font_size=14, color=head_colors[2]),
            Text("position", font_size=14, color=head_colors[4]),
            Text("context", font_size=14, color=head_colors[6]),
        )

        for i, (label, head_idx) in enumerate(zip(focus_labels, [0, 2, 4, 6])):
            label.next_to(heads_group[head_idx], DOWN, buff=0.1)
            label.shift(LEFT * (i - 1.5) * 0.3)

        self.play(
            LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in focus_labels], lag_ratio=0.2),
            run_time=1.5
        )
        self.wait(1.5)

        # Concatenation animation
        concat_box = RoundedRectangle(
            width=3, height=0.8,
            corner_radius=0.15,
            fill_color=DEEP_BLUE,
            fill_opacity=0.8,
            stroke_color=SOFT_WHITE,
            stroke_width=1
        )
        concat_box.shift(DOWN * 2)
        concat_label = Text("CONCAT + LINEAR", font_size=16, weight=BOLD)
        concat_label.set_color(SOFT_WHITE)
        concat_label.move_to(concat_box)

        # Animate heads merging
        self.play(
            FadeOut(focus_labels),
            run_time=0.5
        )

        # Create merge lines
        merge_lines = VGroup()
        for head in heads_group:
            line = Line(
                head.get_bottom(),
                concat_box.get_top(),
                stroke_width=1.5,
                stroke_color=ACCENT_PURPLE,
                stroke_opacity=0.5
            )
            merge_lines.add(line)

        self.play(
            LaggedStart(*[ShowCreation(line) for line in merge_lines], lag_ratio=0.08),
            FadeIn(concat_box),
            FadeIn(concat_label),
            run_time=1.8
        )
        self.wait(1.0)

        # Output arrow
        output_arrow = Arrow(
            concat_box.get_bottom(),
            concat_box.get_bottom() + DOWN * 0.8,
            buff=0.1,
            stroke_width=3,
            color=ACCENT_TEAL
        )
        output_label = Text("OUTPUT", font_size=16, color=ACCENT_TEAL)
        output_label.next_to(output_arrow, DOWN, buff=0.1)

        self.play(
            GrowArrow(output_arrow),
            FadeIn(output_label),
            run_time=1.0
        )
        self.wait(1.5)

        # Clear
        self.play(
            FadeOut(VGroup(mh_title, heads_group, merge_lines, concat_box, concat_label, output_arrow, output_label)),
            run_time=1.0
        )

    # ========================================================================
    # SEGMENT 5: ARCHITECTURE REVEAL
    # ========================================================================
    def architecture_reveal(self):
        """Cinematic reveal of the full transformer architecture."""

        # Build architecture from bottom up
        arch_title = Text("THE COMPLETE ARCHITECTURE", font_size=24, weight=BOLD)
        arch_title.set_color_by_gradient(GLOW_BLUE, GLOW_PURPLE)
        arch_title.to_edge(UP, buff=0.4)

        self.play(Write(arch_title), run_time=1.2)
        self.wait(0.5)

        # Create elegant encoder-decoder diagram
        encoder = self.create_encoder_stack()
        decoder = self.create_decoder_stack()

        encoder.shift(LEFT * 2.5)
        decoder.shift(RIGHT * 2.5)

        # Labels
        enc_label = Text("ENCODER", font_size=20, weight=BOLD, color=ACCENT_BLUE)
        dec_label = Text("DECODER", font_size=20, weight=BOLD, color=ACCENT_TEAL)
        enc_label.next_to(encoder, UP, buff=0.3)
        dec_label.next_to(decoder, UP, buff=0.3)

        # Input/Output
        input_label = Text("Input", font_size=16, color=SOFT_WHITE)
        input_label.set_opacity(0.7)
        input_label.next_to(encoder, DOWN, buff=0.3)

        output_label = Text("Output", font_size=16, color=SOFT_WHITE)
        output_label.set_opacity(0.7)
        output_label.next_to(decoder, DOWN, buff=0.3)

        # Animate encoder appearing
        self.play(
            LaggedStart(
                *[FadeIn(block, shift=UP * 0.2, scale=0.9) for block in encoder],
                lag_ratio=0.2
            ),
            FadeIn(enc_label),
            FadeIn(input_label),
            run_time=2.0
        )
        self.wait(1.0)

        # Animate decoder appearing
        self.play(
            LaggedStart(
                *[FadeIn(block, shift=UP * 0.2, scale=0.9) for block in decoder],
                lag_ratio=0.2
            ),
            FadeIn(dec_label),
            FadeIn(output_label),
            run_time=2.0
        )
        self.wait(1.0)

        # Cross-attention connections
        cross_arrows = VGroup()
        for i in range(len(encoder)):
            arrow = Arrow(
                encoder[i].get_right(),
                decoder[i].get_left(),
                buff=0.2,
                stroke_width=2,
                color=ACCENT_GOLD,
                stroke_opacity=0.6
            )
            cross_arrows.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in cross_arrows], lag_ratio=0.25),
            run_time=1.8
        )
        self.wait(1.0)

        # Add flowing data particles
        data_flow = self.create_data_flow_particles(encoder, decoder)

        self.play(
            LaggedStart(*[ShowCreation(p) for p in data_flow], lag_ratio=0.08),
            run_time=2.5
        )
        self.wait(1.5)

        # Pulse effect on architecture
        self.play(
            encoder.animate.set_opacity(0.9),
            decoder.animate.set_opacity(0.9),
            cross_arrows.animate.set_stroke(opacity=0.8),
            run_time=0.6
        )
        self.play(
            encoder.animate.set_opacity(1),
            decoder.animate.set_opacity(1),
            cross_arrows.animate.set_stroke(opacity=0.6),
            run_time=0.6
        )
        self.wait(1.5)

        # Store for outro
        self.full_arch = VGroup(
            encoder, decoder, enc_label, dec_label,
            input_label, output_label, cross_arrows, data_flow, arch_title
        )

    # ========================================================================
    # SEGMENT 6: CINEMATIC OUTRO
    # ========================================================================
    def cinematic_outro(self):
        """Elegant closing with the architecture fading to logo."""

        # Fade architecture to center and scale down
        self.play(
            self.full_arch.animate.scale(0.6).set_opacity(0.3),
            run_time=1.5
        )

        # Final text
        final_text = Text("ATTENTION IS ALL YOU NEED", font_size=36, weight=BOLD)
        final_text.set_color_by_gradient(GLOW_BLUE, GLOW_PURPLE)

        # Elegant underline
        underline = Line(
            final_text.get_left() + DOWN * 0.3,
            final_text.get_right() + DOWN * 0.3,
            stroke_width=2,
            color=ACCENT_GOLD
        )

        self.play(
            Write(final_text),
            run_time=2.0
        )
        self.play(
            ShowCreation(underline),
            run_time=0.8
        )
        self.wait(3.0)

        # Fade everything out elegantly
        self.play(
            FadeOut(VGroup(final_text, underline, self.full_arch, self.particles, self.network_bg)),
            run_time=2.0
        )

    # ========================================================================
    # HELPER METHODS - PREMIUM VISUAL COMPONENTS
    # ========================================================================

    def create_particle_field(self, n_particles):
        """Create floating particles for background ambiance."""
        particles = VGroup()
        for _ in range(n_particles):
            x = np.random.uniform(-7, 7)
            y = np.random.uniform(-4, 4)
            size = np.random.uniform(0.02, 0.08)
            opacity = np.random.uniform(0.1, 0.4)

            particle = Dot(
                point=[x, y, 0],
                radius=size,
                color=interpolate_color(GLOW_BLUE, GLOW_PURPLE, np.random.random()),
                fill_opacity=opacity
            )
            particles.add(particle)
        return particles

    def create_network_background(self):
        """Create subtle neural network pattern in background."""
        nodes = VGroup()
        edges = VGroup()

        # Create grid of nodes
        for i in range(-3, 4):
            for j in range(-2, 3):
                node = Dot(
                    point=[i * 2, j * 1.5, 0],
                    radius=0.08,
                    color=GLOW_BLUE,
                    fill_opacity=0.3
                )
                nodes.add(node)

        # Create some connections
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i < j and np.random.random() < 0.15:
                    edge = Line(
                        node1.get_center(),
                        node2.get_center(),
                        stroke_width=0.5,
                        stroke_color=GLOW_PURPLE,
                        stroke_opacity=0.2
                    )
                    edges.add(edge)

        return VGroup(edges, nodes)

    def create_3d_token(self, text, index):
        """Create a 3D-style token cube."""
        # Main face
        main_face = RoundedRectangle(
            width=1.0,
            height=0.7,
            corner_radius=0.1,
            fill_color=interpolate_color(ACCENT_BLUE, ACCENT_PURPLE, index / 5),
            fill_opacity=0.8,
            stroke_color=SOFT_WHITE,
            stroke_width=1.5
        )

        # 3D depth effect (side)
        side = Polygon(
            main_face.get_corner(UR),
            main_face.get_corner(UR) + RIGHT * 0.12 + UP * 0.08,
            main_face.get_corner(DR) + RIGHT * 0.12 + UP * 0.08,
            main_face.get_corner(DR),
            fill_color=interpolate_color(ACCENT_BLUE, ACCENT_PURPLE, index / 5),
            fill_opacity=0.5,
            stroke_width=0
        )

        # Top face for 3D effect
        top = Polygon(
            main_face.get_corner(UL),
            main_face.get_corner(UR),
            main_face.get_corner(UR) + RIGHT * 0.12 + UP * 0.08,
            main_face.get_corner(UL) + RIGHT * 0.12 + UP * 0.08,
            fill_color=interpolate_color(ACCENT_BLUE, ACCENT_PURPLE, index / 5),
            fill_opacity=0.3,
            stroke_width=0
        )

        # Text label
        label = Text(text, font_size=22, weight=BOLD)
        label.set_color(SOFT_WHITE)
        label.move_to(main_face)

        return VGroup(side, top, main_face, label)

    def create_token_entrance(self, token):
        """Create entrance animation for a token."""
        return FadeIn(token, shift=DOWN * 0.3, scale=0.8)

    def create_embedding_bar(self, index):
        """Create a gradient embedding vector visualization."""
        n_segments = 12
        bar = VGroup()

        for i in range(n_segments):
            segment = Rectangle(
                width=0.15,
                height=0.12,
                fill_color=interpolate_color(ACCENT_BLUE, ACCENT_PURPLE, i / n_segments),
                fill_opacity=0.4 + 0.4 * np.sin(i * 0.5 + index),
                stroke_width=0
            )
            bar.add(segment)

        bar.arrange(DOWN, buff=0.02)
        return bar

    def create_positional_wave(self):
        """Create a sine wave representing positional encoding."""
        wave = FunctionGraph(
            lambda x: 0.3 * np.sin(2 * x) + 0.15 * np.sin(4 * x),
            x_range=[-5, 5, 0.1],
            color=ACCENT_GOLD,
            stroke_width=2
        )
        return wave

    def create_attention_matrix(self, size):
        """Create a beautiful attention matrix visualization."""
        matrix = VGroup()

        # Generate attention pattern (softmax-like)
        attention_weights = np.random.dirichlet(np.ones(size), size=size)

        for i in range(size):
            row = VGroup()
            for j in range(size):
                weight = attention_weights[i][j]
                cell = Square(
                    side_length=0.5,
                    fill_color=interpolate_color(DEEP_BLUE, ACCENT_GOLD, weight),
                    fill_opacity=0.3 + weight * 0.7,
                    stroke_color=SOFT_WHITE,
                    stroke_width=0.5,
                    stroke_opacity=0.3
                )
                row.add(cell)
            row.arrange(RIGHT, buff=0.05)
            matrix.add(row)

        matrix.arrange(DOWN, buff=0.05)
        return matrix

    def create_attention_head(self, color, index):
        """Create a single attention head visualization."""
        # Main circle
        head = Circle(
            radius=0.4,
            fill_color=color,
            fill_opacity=0.6,
            stroke_color=color,
            stroke_width=2
        )

        # Inner pattern (simplified attention pattern)
        inner = VGroup()
        for i in range(3):
            line = Line(
                head.get_center() + LEFT * 0.2,
                head.get_center() + RIGHT * 0.2,
                stroke_width=1.5,
                stroke_color=SOFT_WHITE,
                stroke_opacity=0.5
            )
            line.shift(UP * (i - 1) * 0.15)
            inner.add(line)

        # Head number
        num = Text(str(index + 1), font_size=14, weight=BOLD)
        num.set_color(SOFT_WHITE)
        num.move_to(head.get_center())

        return VGroup(head, inner, num)

    def create_encoder_stack(self):
        """Create encoder block stack."""
        blocks = VGroup()
        for i in range(4):
            block = self.create_transformer_block_mini(ACCENT_BLUE, i)
            blocks.add(block)
        blocks.arrange(UP, buff=0.2)
        return blocks

    def create_decoder_stack(self):
        """Create decoder block stack."""
        blocks = VGroup()
        for i in range(4):
            block = self.create_transformer_block_mini(ACCENT_TEAL, i)
            blocks.add(block)
        blocks.arrange(UP, buff=0.2)
        return blocks

    def create_transformer_block_mini(self, color, index):
        """Create a mini transformer block for architecture diagram."""
        # Main block
        block = RoundedRectangle(
            width=2.0,
            height=0.6,
            corner_radius=0.1,
            fill_color=color,
            fill_opacity=0.3 + index * 0.1,
            stroke_color=color,
            stroke_width=1.5
        )

        # Internal structure hint
        line1 = Line(
            block.get_left() + RIGHT * 0.3,
            block.get_right() + LEFT * 0.3,
            stroke_width=1,
            stroke_color=SOFT_WHITE,
            stroke_opacity=0.3
        )
        line1.shift(UP * 0.1)

        line2 = line1.copy().shift(DOWN * 0.2)

        return VGroup(block, line1, line2)

    def create_data_flow_particles(self, encoder, decoder):
        """Create flowing data particles between encoder and decoder."""
        particles = VGroup()

        for i in range(15):
            # Random path
            start = encoder[np.random.randint(len(encoder))].get_right()
            end = decoder[np.random.randint(len(decoder))].get_left()

            particle = Dot(
                radius=0.04,
                color=ACCENT_GOLD,
                fill_opacity=0.6
            )

            # Create path
            path = CubicBezier(
                start,
                start + RIGHT * 1,
                end + LEFT * 1,
                end
            )
            path.set_stroke(ACCENT_GOLD, width=0.5, opacity=0.3)
            particles.add(path)

        return particles
