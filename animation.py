from manim import *
import numpy as np

class SolanaICOAnimation(Scene):
    def construct(self):
        # Colors
        primary_color = "#4A90E2"  # Blue
        secondary_color = "#50C878"  # Green
        accent_color = "#FFD700"  # Gold
        background_color = "#2C3E50"  # Dark blue
        text_color = "#ECF0F1"  # Light gray

        # Set background
        self.camera.background_color = background_color

        # Title
        title = Text("Solana ICO & Resource Management CLI", font_size=48, color=text_color)
        title.to_edge(UP)
        self.play(Write(title))

        # Project overview section
        overview_objects = self.project_overview(primary_color, secondary_color, accent_color, text_color)
        self.wait(1)
        self.play(FadeOut(*overview_objects))

        # Architecture section
        arch_objects = self.architecture_diagram(primary_color, secondary_color, accent_color, text_color)
        self.wait(1)
        self.play(FadeOut(*arch_objects))

        # ICO workflow section
        ico_objects = self.ico_workflow(primary_color, secondary_color, accent_color, text_color)
        self.wait(1)
        self.play(FadeOut(*ico_objects))

        # Resource management section
        resource_objects = self.resource_management(primary_color, secondary_color, accent_color, text_color)
        self.wait(1)
        self.play(FadeOut(*resource_objects))

        # Bonding curve explanation
        bc_objects = self.bonding_curve_explanation(primary_color, secondary_color, accent_color, text_color)
        self.wait(1)
        self.play(FadeOut(*bc_objects))

        # Final scene
        final_objects = self.final_scene(primary_color, secondary_color, accent_color, text_color)
        self.wait(1)
        self.play(FadeOut(*final_objects))

        # Fade out main title at the very end
        self.play(FadeOut(title))
    
    def project_overview(self, primary_color, secondary_color, accent_color, text_color):
        """Project overview scene"""
        # Main description
        description = Text(
            "A Python CLI tool for managing Initial Coin Offerings (ICOs)\n"
            "on Solana blockchain with on-chain bonding curves and\n"
            "resource access control",
            font_size=32,
            color=text_color,
            line_spacing=1.2
        ).move_to(UP * 1.5)

        # Key features
        features_title = Text("Key Features:", font_size=36, color=accent_color)
        features_title.next_to(description, DOWN, buff=1)

        features = VGroup(
            Text("• On-chain bonding curve pricing", font_size=28, color=text_color),
            Text("• ICO management (buy/sell tokens)", font_size=28, color=text_color),
            Text("• Resource access control", font_size=28, color=text_color),
            Text("• Solana blockchain integration", font_size=28, color=text_color),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        features.next_to(features_title, DOWN, buff=0.5)

        # Animate
        self.play(Write(description))
        self.play(Write(features_title))
        for feature in features:
            self.play(Write(feature), run_time=0.7)

        # Wait
        self.wait(2)

        # Return all objects for cleanup
        return [description, features_title, features]

    def architecture_diagram(self, primary_color, secondary_color, accent_color, text_color):
        """Architecture diagram scene"""
        arch_title = Text("System Architecture", font_size=42, color=accent_color)
        arch_title.move_to(UP * 3.5)
        
        # Define components first
        cli_label = Text("CLI Interface (Typer)", font_size=20, color=text_color)
        cli_rect = RoundedRectangle(width=4.5, height=1, corner_radius=0.2, color=primary_color, fill_opacity=0.3)
        cli_group = VGroup(cli_rect, cli_label)

        app_components = VGroup(
            Text("• ICO Manager", font_size=18, color=text_color),
            Text("• Resource Manager", font_size=18, color=text_color),
            Text("• Solana Client", font_size=18, color=text_color),
            Text("• Configuration", font_size=18, color=text_color)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        app_label = Text("Application Logic", font_size=20, color=text_color).next_to(app_components, UP, buff=0.3)
        app_rect = RoundedRectangle(width=4.5, height=2.5, corner_radius=0.2, color=secondary_color, fill_opacity=0.3)
        app_group = VGroup(app_rect, app_label, app_components)

        solana_components = VGroup(
            Text("• Smart Program", font_size=18, color=text_color),
            Text("• ICO State PDA", font_size=18, color=text_color),
            Text("• Resource State PDA", font_size=18, color=text_color),
            Text("• Token Accounts", font_size=18, color=text_color)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        solana_label = Text("Solana Blockchain", font_size=20, color=text_color).next_to(solana_components, UP, buff=0.3)
        solana_rect = RoundedRectangle(width=4.5, height=2.5, corner_radius=0.2, color=accent_color, fill_opacity=0.3)
        solana_group = VGroup(solana_rect, solana_label, solana_components)

        # Arrange layers and create master group
        layers = VGroup(cli_group, app_group, solana_group).arrange(DOWN, buff=0.75)
        master_group = VGroup(layers).move_to(ORIGIN)

        # Create arrows after positioning
        arrow1 = Arrow(cli_group.get_bottom(), app_group.get_top(), color=text_color, buff=0.1)
        arrow2 = Arrow(app_group.get_bottom(), solana_group.get_top(), color=text_color, buff=0.1)

        # Animate
        self.play(Write(arch_title))
        self.play(FadeIn(cli_group))
        self.play(GrowArrow(arrow1))
        self.play(FadeIn(app_group))
        self.play(GrowArrow(arrow2))
        self.play(FadeIn(solana_group))

        self.wait(3)

        return [arch_title, cli_group, app_group, solana_group, arrow1, arrow2]

    def ico_workflow(self, primary_color, secondary_color, accent_color, text_color):
        """ICO workflow scene"""
        ico_title = Text("ICO Workflow", font_size=42, color=accent_color)
        ico_title.move_to(UP * 3.5)

        bc_note = Text("All transactions use on-chain bonding curve pricing", font_size=24, color=text_color, slant=ITALIC)

        init_step = self.create_step_box("1. Initialize ICO", "Owner sets up ICO parameters\n(base price, scaling factor, total supply)", primary_color, text_color)
        buy_step = self.create_step_box("2. Buy Tokens", "Users purchase CTX tokens\nusing SOL via bonding curve", secondary_color, text_color)
        sell_step = self.create_step_box("3. Sell Tokens", "Users sell CTX tokens back\nreceiving SOL via bonding curve", secondary_color, text_color)
        withdraw_step = self.create_step_box("4. Withdraw Funds", "Owner withdraws accumulated\nSOL from escrow account", accent_color, text_color)

        top_row = VGroup(init_step, buy_step, sell_step).arrange(RIGHT, buff=1)
        full_diagram = VGroup(top_row, withdraw_step).arrange(DOWN, buff=1.5)
        
        master_group = VGroup(full_diagram).scale(0.7).move_to(ORIGIN)
        bc_note.next_to(master_group, DOWN, buff=0.5)

        arrow1 = Arrow(init_step.get_right(), buy_step.get_left(), color=text_color)
        arrow2 = Arrow(buy_step.get_right(), sell_step.get_left(), color=text_color)
        arrow3 = Arrow(sell_step.get_corner(DL), withdraw_step.get_corner(UR), color=text_color)
        arrow4 = Arrow(withdraw_step.get_corner(UL), init_step.get_corner(DL), color=text_color)

        self.play(Write(ico_title))
        self.play(FadeIn(init_step))
        self.play(GrowArrow(arrow1))
        self.play(FadeIn(buy_step))
        self.play(GrowArrow(arrow2))
        self.play(FadeIn(sell_step))
        self.play(GrowArrow(arrow3))
        self.play(FadeIn(withdraw_step))
        self.play(GrowArrow(arrow4))
        self.play(Write(bc_note))
        
        self.wait(3)

        return [ico_title, init_step, buy_step, sell_step, withdraw_step, arrow1, arrow2, arrow3, arrow4, bc_note]

    def resource_management(self, primary_color, secondary_color, accent_color, text_color):
        """Resource management scene"""
        resource_title = Text("Resource Access Control", font_size=42, color=accent_color)
        resource_title.move_to(UP * 3.5)

        create_step = self.create_step_box("1. Create Resource", "Server creates resource access info\nwith fee amount on blockchain", primary_color, text_color)
        access_step = self.create_step_box("2. Access Resource", "Users pay fee to access\noff-chain resources via on-chain payment", secondary_color, text_color)
        payment_step = self.create_step_box("3. Payment Processing", "SOL payment transferred to server\nAccess granted to off-chain resource", accent_color, text_color)

        examples = VGroup(
            Text("Example Resources:", font_size=24, color=text_color),
            Text("• Premium API endpoints", font_size=20, color=text_color),
            Text("• Private data feeds", font_size=20, color=text_color),
            Text("• Exclusive content", font_size=20, color=text_color)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        # Arrange layout
        top_row = VGroup(create_step, access_step).arrange(RIGHT, buff=1.0)
        payment_step.next_to(access_step, DOWN, buff=1.0).align_to(access_step, RIGHT)
        workflow_group = VGroup(top_row, payment_step)
        
        master_group = VGroup(workflow_group, examples).arrange(RIGHT, buff=1.5, aligned_edge=UP)
        master_group.scale(0.7).move_to(ORIGIN)

        # Create arrows after positioning
        arrow1 = Arrow(create_step.get_right(), access_step.get_left(), color=text_color, buff=0.1)
        arrow2 = Arrow(access_step.get_corner(DR), payment_step.get_corner(UL), color=text_color, buff=0.1)

        self.play(Write(resource_title))
        self.play(FadeIn(create_step))
        self.play(GrowArrow(arrow1))
        self.play(FadeIn(access_step))
        self.play(GrowArrow(arrow2))
        self.play(FadeIn(payment_step))
        self.play(Write(examples))

        self.wait(3)

        return [resource_title, create_step, access_step, payment_step, arrow1, arrow2, examples]

    def bonding_curve_explanation(self, primary_color, secondary_color, accent_color, text_color):
        """Bonding curve explanation scene"""
        bc_title = Text("Bonding Curve Mechanism", font_size=42, color=accent_color).to_edge(UP)

        formula = MathTex("Price = StartingPrice \\times (1 + \\frac{TokensSold}{ScalingFactor})", font_size=36, color=text_color)
        
        explanation = VGroup(
            Text("• Linear bonding curve implemented on-chain", font_size=24, color=text_color),
            Text("• Price increases as more tokens are sold", font_size=24, color=text_color),
            Text("• Client-side estimator for price predictions", font_size=24, color=text_color),
            Text("• Automatic minting/burning of tokens", font_size=24, color=text_color)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)

        content_group = VGroup(formula, explanation).arrange(DOWN, buff=0.8, aligned_edge=LEFT).move_to(LEFT * 3)

        axes = Axes(
            x_range=[0, 100, 25], y_range=[0, 100, 25],
            axis_config={"color": text_color},
            x_length=5, y_length=4
        )
        x_label = axes.get_x_axis_label(Text("Tokens Sold", font_size=20, color=text_color), edge=DOWN, direction=DOWN, buff=0.4)
        y_label = axes.get_y_axis_label(Text("Price", font_size=20, color=text_color).rotate(90 * DEGREES), edge=LEFT, direction=LEFT, buff=0.4)
        curve = axes.plot(lambda x: 10 + 0.8 * x, color=secondary_color, x_range=[0,100])
        
        graph_group = VGroup(axes, x_label, y_label, curve).move_to(RIGHT * 3.5 + DOWN*0.5)

        self.play(Write(bc_title))
        self.play(Write(formula))
        self.play(Write(explanation))
        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Create(curve))

        self.wait(3)

        return [bc_title, content_group, graph_group]

    def final_scene(self, primary_color, secondary_color, accent_color, text_color):
        """Final scene with project benefits"""
        benefits_title = Text("Project Benefits", font_size=42, color=accent_color)
        benefits_list = VGroup(
            Text("• Decentralized ICO with fair pricing", font_size=28, color=text_color),
            Text("• Trustless resource access control", font_size=28, color=text_color),
            Text("• On-chain transparency and security", font_size=28, color=text_color),
            Text("• Scalable Solana blockchain performance", font_size=28, color=text_color),
            Text("• Modern Python CLI with comprehensive features", font_size=28, color=text_color)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)

        tech_title = Text("Technology Stack:", font_size=32, color=primary_color)
        tech_stack_list = VGroup(
            Text("• Python 3.8+ with Typer CLI framework", font_size=24, color=text_color),
            Text("• Solana blockchain integration", font_size=24, color=text_color),
            Text("• SPL token standards", font_size=24, color=text_color),
            Text("• Program Derived Addresses (PDAs)", font_size=24, color=text_color),
            Text("• On-chain bonding curve implementation", font_size=24, color=text_color)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        thank_you = Text("Thank you for exploring the Solana ICO CLI project!", font_size=36, color=accent_color)

        benefits_section = VGroup(benefits_title, benefits_list).arrange(DOWN, buff=0.5)
        tech_section = VGroup(tech_title, tech_stack_list).arrange(DOWN, buff=0.5)

        master_group = VGroup(benefits_section, tech_section).arrange(DOWN, buff=1.0).scale(0.8).move_to(ORIGIN)
        thank_you.scale(0.8).next_to(master_group, DOWN, buff=0.8)

        self.play(Write(benefits_title))
        for item in benefits_list:
            self.play(Write(item), run_time=0.6)
        
        self.play(Write(tech_title))
        for item in tech_stack_list:
            self.play(Write(item), run_time=0.5)

        self.wait(2)
        self.play(Write(thank_you))
        self.wait(2)

        return [master_group, thank_you]

    def create_step_box(self, title, description, color, text_color):
        """Helper method to create a step box with title and description"""
        title_text = Text(title, font_size=22, color=text_color, weight=BOLD)
        desc_text = Text(description, font_size=16, color=text_color, line_spacing=1.1)
        content = VGroup(title_text, desc_text).arrange(DOWN, buff=0.25)
        rect = RoundedRectangle(
            width=content.width + 0.5, 
            height=content.height + 0.5, 
            color=color, 
            fill_opacity=0.3,
            corner_radius=0.2
        )
        return VGroup(rect, content)