from app.services.rendering.template_engine import TemplateEngine


def test_custom_template_supports_legacy_top_level_fields():
    template = "<h1>{{ contact.full_name }}</h1><p>{{ summary }}</p>"

    html = TemplateEngine().render_custom_template(
        template,
        "",
        {"contact": {"full_name": "Jane Doe"}, "summary": "Engineer"},
    )

    assert "<h1>Jane Doe</h1>" in html
    assert "<p>Engineer</p>" in html


def test_custom_template_handles_missing_contact():
    html = TemplateEngine().render_custom_template(
        "<h1>{{ contact.full_name }}</h1>",
        "",
        {},
    )

    assert html == "<h1></h1>"
