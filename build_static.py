import os
import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).parent.resolve()
DB_PATH = ROOT / "main.db"
PAGES_DIR = ROOT / "pages"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"


def html_to_plaintext(html: str) -> str:
    # wrap escaped html in <pre>
    return "<pre>" + html.replace("<", "&lt;").replace(">", "&gt;") + "</pre>"


def ensure_dirs() -> None:
    # create output directories if missing
    PAGES_DIR.mkdir(parents=True, exist_ok=True)


def fetch_pages() -> list[tuple[str, int, str]]:
    # returns list of (name, rowid, code)
    if not DB_PATH.exists():
        return []
    con = sqlite3.connect(str(DB_PATH))
    cur = con.cursor()
    rows = cur.execute("SELECT name, rowid, code FROM pages").fetchall()
    con.close()
    return [(name, rowid, code) for (name, rowid, code) in rows]


def write_member_pages(pages: list[tuple[str, int, str]]) -> None:
    # write pages/{id}.html and pages/{id}-raw.html
    for _, rowid, code in pages:
        page_path = PAGES_DIR / f"{rowid}.html"
        raw_path = PAGES_DIR / f"{rowid}-raw.html"
        page_path.write_text(code, encoding="utf-8")
        raw_path.write_text(html_to_plaintext(code), encoding="utf-8")


def generate_index_html(pages: list[tuple[str, int, str]]) -> None:
    # base is templates/index.html with jinja removed and links made relative
    template_path = TEMPLATES_DIR / "index.html"
    if template_path.exists():
        html = template_path.read_text(encoding="utf-8")
    else:
        html = """<!DOCTYPE html><html lang=\"en\"><head><title>Pages</title><link href=\"static/output.css\" rel=\"stylesheet\"></head><body><div class=\"max-w-5xl mx-auto p-4\"><h1 class=\"text-3xl mb-4\">Member Pages</h1><table class=\"w-full\"><thead><tr><th class=\"text-left\">Name</th><th class=\"text-left\">Page</th><th class=\"text-left\">Code</th></tr></thead><tbody><!--ROWS--></tbody></table></div></body></html>"""

    # make css link relative
    html = html.replace("/static/output.css", "static/output.css")

    # update demo link to local demo.html, drop submit link
    html = html.replace("href=\"/demo\"", "href=\"demo.html\"")
    html = re.sub(r"\n\s*<a[^>]*href=\"/submit\"[\s\S]*?</a>\n", "\n", html)

    # build rows
    row_tpl = (
        "<tr class=\"hover:bg-slate-800/60 transition-colors\">"
        "<td class=\"px-4 py-2\"><p>{name}</p></td>"
        "<td class=\"px-4 py-2\"><a href=\"pages/{id}.html\" class=\"text-sky-400 underline decoration-sky-400/40 hover:text-emerald-300\">View Page</a></td>"
        "<td class=\"px-4 py-2\"><a href=\"pages/{id}-raw.html\" class=\"text-sky-400 underline decoration-sky-400/40 hover:text-emerald-300\">View Code</a></td>"
        "</tr>"
    )
    rows_html = "\n".join(row_tpl.format(name=name, id=rowid) for (name, rowid, _) in pages)

    # replace jinja tbody content with rows
    html = re.sub(
        r"\{\%\s*for\s+page\s+in\s+pages\s*\%\}[\s\S]*?\{\%\s*endfor\s*\%\}",
        rows_html or "",
        html,
        flags=re.MULTILINE,
    )

    # ensure tbody exists; if not, inject placeholder marker
    if "{%" in html:
        html = html.replace("{%", "")
        html = html.replace("%}", "")

    (ROOT / "index.html").write_text(html, encoding="utf-8")


def generate_demo_html() -> None:
    # copy demo template to root, fix links for gh pages
    src = TEMPLATES_DIR / "demo.html"
    if not src.exists():
        return
    html = src.read_text(encoding="utf-8")
    html = html.replace("/static/demo_style.css", "static/demo_style.css")
    html = html.replace("/demo/html", "templates/demo.txt")
    html = html.replace("/demo/css", "static/demo_style.txt")
    (ROOT / "demo.html").write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    pages = fetch_pages()
    write_member_pages(pages)
    generate_index_html(pages)
    generate_demo_html()
    print(f"Wrote {len(pages)} pages to {PAGES_DIR.relative_to(ROOT)} and index.html at repo root")


if __name__ == "__main__":
    main()


