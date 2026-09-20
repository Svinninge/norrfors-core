# File version: v0.01
# Description: Text and HTML helpers shared by the notification senders
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - Initial implementation (Claude)
"""Formatting helpers for notifications.

``md_to_html`` uses the ``markdown`` package when it is installed and falls back to
a small built-in converter otherwise, so a project without the dependency still
gets readable mail instead of raw asterisks.
"""

from __future__ import annotations

import re

__all__ = ["split_message", "md_to_html", "html_email_wrapper"]


def split_message(text: str, limit: int = 4000) -> list[str]:
    """Split ``text`` into chunks of at most ``limit`` characters, preferring a
    newline as the cut so a table or list is not broken mid-row."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        chunks.append(remaining[:cut])
        remaining = remaining[cut:].lstrip("\n")
    return chunks


def _inline_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def _fallback_md(md_text: str) -> str:
    """Minimal Markdown to HTML: headings, tables, lists, rules, inline marks.
    Enough for a report mail; not a general-purpose converter."""
    html_lines: list[str] = []
    in_table = False
    for line in md_text.split("\n"):
        stripped = line.strip()
        if re.match(r"^---+$", stripped):
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append("<hr>")
            continue
        if "|" in line and stripped.startswith("|"):
            if re.match(r"^\|[-| :]+\|$", stripped):
                if not in_table:
                    continue
                html_lines.append("</tr></thead><tbody>")
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                html_lines.append("<table><thead><tr>")
                in_table = True
                tag = "th"
            else:
                tag = "td"
            html_lines.append(
                "<tr>" + "".join(f"<{tag}>{_inline_md(c)}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            html_lines.append("</tbody></table>")
            in_table = False
        heading = re.match(r"^(#{1,4})\s+(.*)", line)
        if heading:
            level = len(heading.group(1))
            html_lines.append(f"<h{level}>{_inline_md(heading.group(2))}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", line):
            html_lines.append(f"<li>{_inline_md(line[2:].strip())}</li>")
            continue
        if not stripped:
            html_lines.append("<br>")
            continue
        html_lines.append(f"<p>{_inline_md(line)}</p>")
    if in_table:
        html_lines.append("</tbody></table>")
    return "\n".join(html_lines)


def md_to_html(md_text: str) -> str:
    """Convert Markdown to an HTML fragment. Wrap it with :func:`html_email_wrapper`
    to get a full document."""
    try:
        import markdown as markdown_lib
    except ImportError:
        return _fallback_md(md_text)
    return markdown_lib.markdown(
        md_text, extensions=["tables", "fenced_code", "nl2br"])


def html_email_wrapper(
    html_body: str,
    *,
    title: str,
    subtitle: str = "",
    meta: str = "",
    footer: str = "",
    accent: str = "#1e3a8a",
    accent_light: str = "#3b82f6",
    logo: str = "",
) -> str:
    """Wrap an HTML fragment in the standard report layout.

    Branding is passed in rather than baked in: the same layout carries a finance
    report, a dubblaren digest and a mower alert without any of them inheriting
    another project's name. ``logo`` is an ``<img src>`` value — use a ``cid:``
    reference together with ``send_email(images=…)`` when the image lives behind an
    authenticated origin.
    """
    logo_html = (
        f'<img src="{logo}" alt="" style="width:70px;height:70px;margin-bottom:10px;'
        f'border-radius:12px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);"><br>'
    ) if logo else ""
    subtitle_html = (
        f'<p style="margin:8px 0 0 0;font-size:15px;opacity:0.9;color:#ffffff;">'
        f'{subtitle}</p>'
    ) if subtitle else ""
    meta_html = (
        f'<p style="margin:4px 0 0 0;font-size:12px;opacity:0.75;color:#e2e8f0;">'
        f'{meta}</p>'
    ) if meta else ""
    footer_html = (
        f'<div class="footer"><p>{footer}</p></div>'
    ) if footer else ""

    return f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;margin:0;padding:0;background-color:#f1f5f9;color:#334155;line-height:1.5;font-size:14px;}}
  .container {{max-width:600px;margin:20px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);}}
  .header {{background-color:{accent};background-image:linear-gradient(135deg,{accent} 0%,{accent_light} 100%);padding:30px 24px;color:#ffffff;text-align:center;}}
  .header h1 {{margin:0;font-size:22px;font-weight:700;border:none;padding:0;color:#ffffff;letter-spacing:-0.5px;}}
  .content {{padding:24px;}}
  .footer {{background:#f8fafc;padding:16px 24px;text-align:center;border-top:1px solid #e2e8f0;}}
  .footer p {{margin:0;font-size:12px;color:#94a3b8;}}
  h2 {{font-size:16px;color:#0f172a;margin:20px 0 12px 0;border-bottom:2px solid #f1f5f9;padding-bottom:8px;}}
  p {{margin:0 0 12px 0;}}
  table {{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px;border-radius:6px;overflow:hidden;}}
  th {{background:{accent};color:#ffffff;padding:8px 10px;text-align:left;}}
  td {{padding:8px 10px;border-bottom:1px solid #e2e8f0;}}
  tr:nth-child(even) {{background:#f8fafc;}}
  code {{background:#f1f5f9;padding:2px 4px;border-radius:4px;font-size:12px;color:#db2777;}}
  li {{margin-bottom:6px;}}
  ul, ol {{padding-left:20px;margin-top:4px;}}
  a {{color:#2563eb;text-decoration:none;}}
</style>
</head><body>
<div class="container">
  <div class="header">
    {logo_html}
    <h1>{title}</h1>
    {subtitle_html}
    {meta_html}
  </div>
  <div class="content">
{html_body}
  </div>
  {footer_html}
</div>
</body></html>"""
