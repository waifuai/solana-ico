import argparse
from cli import animation_templates

def add_token_commands(subparsers):
    # Generate Animation Subcommand
    animation_parser = subparsers.add_parser("generate_animation", help="Generate a Manim animation script")
    animation_parser.add_argument("animation_type", choices=["tokenized_economy_intro", "token_affiliates_animation"], help="Type of animation to generate")
    animation_parser.add_argument("--title", help="Title of the animation")
    animation_parser.add_argument("--subtitle", help="Subtitle of the animation")

def handle_token_commands(args):
    if args.command == "generate_animation":
        animation_type = args.animation_type
        if animation_type == "tokenized_economy_intro":
            title = args.title or "The Tokenized Economy"
            subtitle = args.subtitle or "A Solana-Based Barter System"
            animation_script = animation_templates.tokenized_economy_intro_template(title, subtitle)
            print(f"Generated animation script:\n{animation_script}")
        elif animation_type == "token_affiliates_animation":
            animation_script = animation_templates.token_affiliates_animation_template()
            print(f"Generated animation script:\n{animation_script}")