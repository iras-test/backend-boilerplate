import logging
from django.template import Context, Template
from django.utils import timezone

logger = logging.getLogger(__name__)


class TemplateRenderer:

    @classmethod
    def render_email_template(cls, template, context: dict) -> tuple[str, str]:
        """
        Render an EmailTemplate instance against a context dict.

        Parameters
        ----------
        template : EmailTemplate
            The EmailTemplate model instance.
        context : dict
            Key-value pairs used to resolve {{ variable }} placeholders.

        Returns
        -------
        tuple[str, str]
            (subject, html_body) — both ready to pass to send_email.
        """
        tmpl_json = template.body if hasattr(template, "body") else template
        meta      = tmpl_json.get("meta", {})
        blocks    = tmpl_json.get("blocks", [])

        ctx = Context(context, autoescape=False)

        subject   = Template(meta.get("subject",  "")).render(ctx)
        greeting  = Template(meta.get("greeting", "")).render(ctx)
        signature = meta.get("signature", "").replace("\n", "<br>")
        bg_color  = meta.get("bgColor",  "#f9fafb")
        max_width = meta.get("maxWidth", "600px")

        blocks_html = "\n".join(cls._render_block(b, ctx) for b in blocks)

        html = f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:{bg_color};font-family:Arial,sans-serif;">
<div style="max-width:{max_width};margin:40px auto;background:#ffffff;border-radius:8px;overflow:hidden;">

    <div style="background:#ba513f;padding:20px 30px;">
    <span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:0.5px;">NLTSS</span>
    </div>

    <div style="padding:30px;">
    <p style="margin:0 0 20px;color:#374151;font-size:15px;">{greeting}</p>
    {blocks_html}
    <p style="margin:24px 0 0;color:#6B7280;font-size:14px;">{signature}</p>
    </div>

    <div style="background:#f3f4f6;padding:14px 30px;text-align:center;">
    <span style="color:#9CA3AF;font-size:12px;">
        This is an automated message. Please do not reply directly to this email.
    </span>
    </div>

</div>
</body>
</html>
""".strip()

        return subject, html


    @staticmethod
    def _render_heading(block: dict, context: Context) -> str:
        html        = Template(block.get("html", "")).render(context)
        color       = block.get("color", "#374151")
        bg          = block.get("backgroundColor", "transparent")
        font_size   = block.get("fontSize", "22px")
        font_weight = block.get("fontWeight", "600")
        text_align  = block.get("textAlign", "left")
        padding     = block.get("padding", "0 0 10px")
        return (
            f'<h2 style="margin:0;padding:{padding};color:{color};background:{bg};'
            f'font-size:{font_size};font-weight:{font_weight};text-align:{text_align};">'
            f'{html}</h2>'
        )

    @staticmethod
    def _render_text(block: dict, context: Context) -> str:
        html        = Template(block.get("html", "")).render(context)
        color       = block.get("color", "#374151")
        bg          = block.get("backgroundColor", "transparent")
        font_size   = block.get("fontSize", "15px")
        font_weight = block.get("fontWeight", "400")
        text_align  = block.get("textAlign", "left")
        padding     = block.get("padding", "0 0 14px")
        return (
            f'<div style="padding:{padding};color:{color};background:{bg};'
            f'font-size:{font_size};font-weight:{font_weight};text-align:{text_align};">'
            f'{html}</div>'
        )

    @staticmethod
    def _render_button(block: dict, context: Context) -> str:
        label   = Template(block.get("html", "Click Here")).render(context)
        href    = Template(block.get("href", "#")).render(context)
        color   = block.get("color", "#FFFFFF")
        bg      = block.get("backgroundColor", "#2E75B6")
        radius  = block.get("borderRadius", "6px")
        padding = block.get("padding", "12px 24px")
        align   = block.get("align", "center")
        return (
            f'<div style="text-align:{align};padding:16px 0;">'
            f'<a href="{href}" style="display:inline-block;padding:{padding};'
            f'background:{bg};color:{color};border-radius:{radius};'
            f'text-decoration:none;font-family:Arial,sans-serif;font-size:15px;">'
            f'{label}</a></div>'
        )

    @staticmethod
    def _render_image(block: dict, context: Context) -> str:
        src   = Template(block.get("src", "")).render(context)
        alt   = block.get("alt", "")
        align = block.get("align", "center")
        width = block.get("maxWidth", "100%")
        if not src:
            return ""
        return (
            f'<div style="text-align:{align};padding:10px 0;">'
            f'<img src="{src}" alt="{alt}" style="max-width:{width};height:auto;display:inline-block;">'
            f'</div>'
        )

    @staticmethod
    def _render_divider(block: dict, context: Context) -> str:
        color   = block.get("color", "#E5E7EB")
        padding = block.get("padding", "16px 0")
        return f'<div style="padding:{padding};"><hr style="border:none;border-top:1px solid {color};margin:0;"></div>'


    BLOCK_RENDERERS = {
        "Heading": _render_heading,
        "Text":    _render_text,
        "Button":  _render_button,
        "Image":   _render_image,
        "Divider": _render_divider,
    }

    @classmethod
    def _render_block(cls, block: dict, context: Context) -> str:
        block_type = block.get("type")
        renderer   = cls.BLOCK_RENDERERS.get(block_type)
        if not renderer:
            logger.warning("EmailTemplate: unknown block type '%s' — skipped.", block_type)
            return ""
        return renderer(block, context)

    


    @staticmethod
    def build_generic_context(instance, recipient) -> dict:
        """
        Walks the instance's fields and pulls out simple scalar values.
        Used as a fallback when no specific context builder exists for a model.
        Any {{ variable }} in the template that matches a field name will resolve.
        """
        ctx = {
            "recipient_name": TemplateRenderer._full_name(recipient),
            "date":           timezone.now().strftime("%d %B %Y %H:%M"),
        }
        for field in instance._meta.get_fields():
            try:
                value = getattr(instance, field.name, None)
                if isinstance(value, (str, int, float, bool)) or value is None:
                    ctx[field.name] = value if value is not None else "N/A"
            except Exception:
                pass
        return ctx

    @staticmethod
    def _full_name(user) -> str:
        if not user:
            return "User"
        if hasattr(user, "get_full_name"):
            return user.get_full_name() or getattr(user, "username", "User")
        return str(user)

    @staticmethod
    def _fk_name(instance, field_name: str) -> str:
        obj = getattr(instance, field_name, None)
        if obj is None:
            return "N/A"
        return getattr(obj, "name", str(obj))

    @staticmethod
    def _nested(instance, rel: str, attr: str) -> str:
        obj = getattr(instance, rel, None)
        if obj is None:
            return "N/A"
        return getattr(obj, attr, "N/A") or "N/A"