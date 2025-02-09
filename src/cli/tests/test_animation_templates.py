import pytest
from cli import animation_templates

def test_tokenized_economy_intro_template():
    title = "My Title"
    subtitle = "My Subtitle"
    result = animation_templates.tokenized_economy_intro_template(title, subtitle)
    assert "class TokenizedEconomyIntro(Scene):" in result
    assert f'Text("{title}", font_size=48)' in result
    assert f'Text("{subtitle}", font_size=24)' in result

def test_token_affiliates_animation_template():
    result = animation_templates.token_affiliates_animation_template()
    assert "class TokenAffiliatesAnimation(Scene):" in result
    assert "def construct(self):" in result
    assert "def intro_scene(self):" in result
    assert "def dashboard_scene(self):" in result
    assert "def link_commission_scene(self):" in result
    assert "def transaction_payout_scene(self):" in result
    assert "def benefits_scene(self):" in result