"""Build the static portfolio pages from the copied project READMEs."""

from __future__ import annotations

import base64
from datetime import date
from html import escape
from pathlib import Path
import re

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
MARKDOWN = MarkdownIt("commonmark", {"html": True}).enable("table")
MATH = re.compile(r"\$\$([\s\S]*?)\$\$|\$([^$\n]+?)\$")

def load_projects() -> list[dict[str, str]]:
    projects = []
    for path in (ROOT / "content").glob("*.md"):
        if path.name.startswith("_") or path.name == "about.md":
            continue
        source = path.read_text(encoding="utf-8")
        if not source.startswith("---\n"):
            raise ValueError(f"{path}: article must start with --- metadata")
        try:
            header, body = source[4:].split("\n---\n", 1)
        except ValueError as error:
            raise ValueError(f"{path}: missing closing ---") from error
        project = {"slug": path.stem, "body": body}
        for line in header.splitlines():
            key, separator, value = line.partition(":")
            if not separator:
                raise ValueError(f"{path}: invalid metadata line {line!r}")
            project[key.strip()] = value.strip()
        for key in ("title", "short_title", "description", "github", "date"):
            if not project.get(key):
                raise ValueError(f"{path}: missing {key}")
        date.fromisoformat(project["date"])
        if not project["github"].startswith("https://github.com/"):
            raise ValueError(f"{path}: github must be a GitHub URL")
        projects.append(project)
    return sorted(projects, key=lambda project: (project["date"], project["slug"]), reverse=True)


def pretty_date(value: str) -> str:
    day = date.fromisoformat(value)
    return f"{day.strftime('%B')} {day.day}, {day.year}"


def date_markup(project: dict[str, str]) -> str:
    return f'<time datetime="{project["date"]}">{pretty_date(project["date"])}</time>'


def shell(*, title: str, description: str, body: str, prefix: str = "", math: bool = False) -> str:
    math_head = ""
    if math:
        math_head = '\n  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f6f5f0">
  <meta name="description" content="{escape(description, quote=True)}">
  <title>{escape(title)} · Alex Zhai</title>
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}assets/site.css">{math_head}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="wordmark" href="{prefix}index.html" aria-label="Alex Zhai, home">Alex Zhai</a>
      <nav aria-label="Main navigation">
        <a href="{prefix}index.html#about">About</a>
        <a href="{prefix}index.html#projects">Recent</a>
        <a href="https://github.com/AlexZhai21" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a>
        <a href="https://www.linkedin.com/in/alexwzhai/" target="_blank" rel="noopener noreferrer">LinkedIn <span aria-hidden="true">↗</span></a>
      </nav>
    </div>
  </header>
  <main id="main">{body}</main>
  <footer class="site-footer">
    <div class="container footer-inner"><span>Alex Zhai</span><div class="footer-links"><a href="https://github.com/AlexZhai21" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a><a href="https://www.linkedin.com/in/alexwzhai/" target="_blank" rel="noopener noreferrer">LinkedIn <span aria-hidden="true">↗</span></a></div></div>
  </footer>
</body>
</html>
"""


def project_card(project: dict[str, str]) -> str:
    article = f"articles/{project['slug']}.html"
    if project["slug"] == "svd":
        visual = """<div class="project-visual svd-visual" aria-label="An image before and after lower rank approximation">
          <img src="assets/svd-original_grayscale.webp" alt="Original grayscale photo of a dog in a field" loading="lazy" width="512" height="256">
          <img src="assets/svd-rank_10.webp" alt="The same photo approximated at rank 10" loading="lazy" width="512" height="256">
        </div>"""
    elif project.get("image"):
        visual_class = "logo-visual" if project["slug"] == "gpt-2" else "robot-visual"
        image_alt = "OpenAI logo" if project["slug"] == "gpt-2" else f"{project['short_title']} project preview"
        image_size = 'width="721" height="721"' if project["slug"] == "gpt-2" else 'width="640" height="480"'
        visual = f'''<div class="project-visual {visual_class}">
          <img src="{escape(project['image'], quote=True)}" alt="{escape(image_alt, quote=True)}" loading="lazy" {image_size}>
        </div>'''
    else:
        visual = f'<div class="project-visual text-visual"><span>{escape(project["short_title"])}</span></div>'
    return f"""<article class="project-card">
      <a class="visual-link" href="{article}" aria-label="Read about {escape(project['short_title'])}">{visual}</a>
      <h3><a href="{article}">{escape(project['short_title'])}</a></h3>
      <div class="project-date">{date_markup(project)}</div>
      <p>{escape(project['description'])}</p>
      <div class="card-links"><a href="{article}">Read more <span aria-hidden="true">↗</span></a><a href="{project['github']}" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a></div>
    </article>"""


def index_page(projects: list[dict[str, str]]) -> str:
    cards = "\n".join(project_card(project) for project in projects)
    about = MARKDOWN.render((ROOT / "content/about.md").read_text(encoding="utf-8"))
    body = f"""
  <section class="hero container" aria-labelledby="hero-title">
    <div class="hero-copy">
      <h1 id="hero-title">Alex Zhai</h1>
    </div>
  </section>
  <section class="section about-section container" id="about" aria-labelledby="about-title">
    <div class="section-heading"><h2 id="about-title">About me</h2></div>
    <div class="about-copy">{about}</div>
  </section>
  <section class="section container" id="projects" aria-labelledby="projects-title">
    <div class="section-heading"><h2 id="projects-title">Recent</h2></div>
    <div class="project-grid">{cards}</div>
  </section>
  """
    return shell(title="Recent", description="Recent work by Alex Zhai in robotics, machine learning, and image processing.", body=body)


def render_readme(source: str, *, math: bool) -> str:
    if not math:
        return MARKDOWN.render(source)

    expressions: list[tuple[str, str, bool]] = []

    def protect(match: re.Match[str]) -> str:
        display = match.group(1) is not None
        tex = (match.group(1) if display else match.group(2)).strip()
        marker = f"MATHMARKER{len(expressions)}END"
        expressions.append((marker, tex, display))
        return marker

    rendered = MARKDOWN.render(MATH.sub(protect, source))
    for marker, tex, display in expressions:
        if display:
            replacement = f'<div class="math-display">\\[{escape(tex)}\\]</div>'
            rendered = rendered.replace(f"<p>{marker}</p>", replacement)
        else:
            replacement = f'<span class="math-inline">\\({escape(tex)}\\)</span>'
        rendered = rendered.replace(marker, replacement)
    return rendered


def svd_demo() -> str:
    sample_bytes = (ROOT / "assets/svd-original_grayscale.webp").read_bytes()
    sample_data = base64.b64encode(sample_bytes).decode("ascii")
    intro = MARKDOWN.render((ROOT / "content/_svd-demo.md").read_text(encoding="utf-8"))
    return f"""<section class="svd-demo" aria-labelledby="svd-demo-title">
      <h2 id="svd-demo-title">Try it</h2>
      {intro}
      <div class="demo-controls">
        <label for="svdUpload">Image</label>
        <input id="svdUpload" type="file" accept="image/png,image/jpeg,image/webp,image/bmp,image/gif">
        <label for="svdRank">Rank <output id="svdRankValue" for="svdRank">1</output></label>
        <input id="svdRank" type="range" min="1" max="1" value="1" disabled>
        <p id="svdStatus" class="demo-status" role="status" aria-live="polite">Preparing the example image…</p>
      </div>
      <div class="demo-images">
        <figure><img id="svdOriginalImage" src="data:image/webp;base64,{sample_data}" alt="Original example image of a dog in a field"><figcaption>Original</figcaption></figure>
        <figure><canvas id="svdResultCanvas" role="img" aria-label="Low-rank approximation of the selected image">Your browser does not support canvas.</canvas><figcaption>Approximation</figcaption></figure>
      </div>
      <p class="demo-note">The preview is converted to grayscale and resized to at most 192 pixels. Uploaded images stay in your browser.</p>
    </section>"""


def article_page(project: dict[str, str]) -> str:
    source = project["body"]
    source = re.sub(r"\A# .+\n+", "", source, count=1)
    source = re.sub(r"(?m)^##\s*$\n?", "", source)
    if project["slug"] == "robot-arm":
        source = source.replace("outputs/can_demo_0.gif", "../assets/robot-demo.webp")
    if project["slug"] == "svd":
        source = re.split(r"(?m)^## Interactive app\s*$", source, maxsplit=1)[0]
    rendered = render_readme(source, math=project.get("math") == "true")
    rendered = rendered.replace("<img ", '<img loading="lazy" decoding="async" ')
    if project["slug"] == "svd":
        demo = svd_demo()
        demo_script = '<script defer src="../assets/svd-demo.js"></script>'
        gallery = """<div class="example-block"><h2>Image examples</h2><p>The same image at different approximation ranks.</p>
          <div class="comparison-grid">
            <figure><img src="../assets/svd-original_grayscale.webp" alt="Original grayscale image of a dog in a field" loading="lazy" width="512" height="256"><figcaption>Original</figcaption></figure>
            <figure><img src="../assets/svd-rank_10.webp" alt="Rank 10 approximation of the same image" loading="lazy" width="512" height="256"><figcaption>Rank 10</figcaption></figure>
            <figure><img src="../assets/svd-rank_25.webp" alt="Rank 25 approximation of the same image" loading="lazy" width="512" height="256"><figcaption>Rank 25</figcaption></figure>
          </div>
        </div>"""
    else:
        demo = ""
        demo_script = ""
        gallery = ""
    body = f"""
  <div class="article-shell container">
    <a class="back-link" href="../index.html#projects"><span aria-hidden="true">←</span> Back to Recent</a>
    <header class="article-header"><div class="article-date">{date_markup(project)}</div><h1>{escape(project['title'])}</h1><p class="article-deck">{escape(project['description'])}</p><div class="article-actions"><a class="button button-dark" href="{project['github']}" target="_blank" rel="noopener noreferrer">GitHub repository <span aria-hidden="true">↗</span></a></div></header>
    <div class="article-rule"></div>
    <article class="prose" aria-label="Project article">{demo}{rendered}{gallery}</article>
    <div class="article-end"><a href="{project['github']}" target="_blank" rel="noopener noreferrer">GitHub repository <span aria-hidden="true">↗</span></a></div>
    <a class="back-link bottom-back" href="../index.html#projects"><span aria-hidden="true">←</span> Back to Recent</a>
  </div>{demo_script}
  """
    return shell(title=project["title"], description=project["description"], body=body, prefix="../", math=project.get("math") == "true")


def main() -> None:
    projects = load_projects()
    ARTICLES.mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(index_page(projects), encoding="utf-8")
    for project in projects:
        (ARTICLES / f"{project['slug']}.html").write_text(article_page(project), encoding="utf-8")
    print(f"Built index.html and {len(projects)} article pages")


if __name__ == "__main__":
    main()
