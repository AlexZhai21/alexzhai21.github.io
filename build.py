"""Build the static portfolio pages from the copied project READMEs."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
MARKDOWN = MarkdownIt("commonmark", {"html": True}).enable("table")

PROJECTS = [
    {
        "slug": "robot-arm",
        "title": "Action Chunking Transformers, explained",
        "short_title": "Robot arm / ACT",
        "kind": "Robotics · machine learning",
        "description": "An implementation and explanation of the policy behind action chunking for robot control.",
        "github": "https://github.com/AlexZhai21/ActionChunkingTransformers",
        "source": "content/robot-arm.md",
        "image": "assets/robot-preview.webp",
    },
    {
        "slug": "svd",
        "title": "Image approximation using SVD",
        "short_title": "Image approximation / SVD",
        "kind": "Linear algebra · visual computing",
        "description": "A small experiment that rebuilds an image with fewer singular values, with a live rank slider in the app.",
        "github": "https://github.com/AlexZhai21/Image-Approximation-using-SVD",
        "source": "content/svd.md",
        "image": "assets/svd-rank_25.webp",
    },
]


def shell(*, title: str, description: str, body: str, prefix: str = "", math: bool = False) -> str:
    math_head = ""
    if math:
        math_head = """
  <script>
    window.MathJax = {
      tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], displayMath: [['$$', '$$'], ['\\[', '\\]']] },
      options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }
    };
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>"""
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
      <a class="wordmark" href="{prefix}index.html" aria-label="Alex Zhai, home"><span class="mark">AZ</span><span>Alex Zhai</span></a>
      <nav aria-label="Main navigation">
        <a href="{prefix}index.html#projects">Projects</a>
        <a href="{prefix}index.html#articles">Articles</a>
        <a href="https://github.com/AlexZhai21" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a>
      </nav>
    </div>
  </header>
  <main id="main">{body}</main>
  <footer class="site-footer">
    <div class="container footer-inner"><span>Alex Zhai · Projects &amp; writing</span><a href="https://github.com/AlexZhai21" target="_blank" rel="noopener noreferrer">GitHub profile <span aria-hidden="true">↗</span></a></div>
  </footer>
</body>
</html>
"""


def project_card(project: dict[str, str], index: int) -> str:
    article = f"articles/{project['slug']}.html"
    if project["slug"] == "svd":
        visual = """<div class="project-visual svd-visual" aria-label="An image before and after lower rank approximation">
          <img src="assets/svd-original_grayscale.webp" alt="Original grayscale photo of a dog in a field" loading="lazy" width="512" height="256">
          <img src="assets/svd-rank_10.webp" alt="The same photo approximated at rank 10" loading="lazy" width="512" height="256">
          <span class="visual-label">Original <span aria-hidden="true">/</span> Rank 10</span>
        </div>"""
    else:
        visual = """<div class="project-visual robot-visual">
          <img src="assets/robot-preview.webp" alt="A simulated robot arm reaching toward a can" loading="lazy" width="640" height="480">
          <span class="visual-label">Robot control simulation</span>
        </div>"""
    return f"""<article class="project-card">
      <a class="visual-link" href="{article}" aria-label="Read about {escape(project['short_title'])}">{visual}</a>
      <div class="project-meta"><span>0{index}</span><span>{escape(project['kind'])}</span></div>
      <h3><a href="{article}">{escape(project['short_title'])}</a></h3>
      <p>{escape(project['description'])}</p>
      <div class="card-links"><a href="{article}">Read the article <span aria-hidden="true">↗</span></a><a href="{project['github']}" target="_blank" rel="noopener noreferrer">View code <span aria-hidden="true">↗</span></a></div>
    </article>"""


def index_page() -> str:
    cards = "\n".join(project_card(project, i) for i, project in enumerate(PROJECTS, 1))
    articles = "\n".join(
        f"""<li><a href="articles/{p['slug']}.html"><span class="article-number">0{i}</span><span class="article-list-text"><strong>{escape(p['title'])}</strong><small>{escape(p['kind'])}</small></span><span class="arrow" aria-hidden="true">↗</span></a></li>"""
        for i, p in enumerate(PROJECTS, 1)
    )
    body = f"""
  <section class="hero container" aria-labelledby="hero-title">
    <div class="hero-copy">
      <p class="eyebrow"><span class="eyebrow-dot" aria-hidden="true"></span> Projects &amp; writing</p>
      <h1 id="hero-title">Building things to <em>understand</em> how they work.</h1>
      <p class="hero-description">I’m Alex. I explore robotics, machine learning, and the math behind visual computing through code and experiments.</p>
      <div class="hero-actions"><a class="button button-dark" href="#projects">Explore projects <span aria-hidden="true">↘</span></a><a class="text-link" href="https://github.com/AlexZhai21" target="_blank" rel="noopener noreferrer">Find me on GitHub <span aria-hidden="true">↗</span></a></div>
    </div>
    <div class="hero-side" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><span class="hero-monogram">AZ<span class="monogram-dot">.</span></span><span class="hero-side-caption">CODE / EXPERIMENTS / NOTES</span></div>
  </section>
  <section class="section container" id="projects" aria-labelledby="projects-title">
    <div class="section-heading"><div><p class="section-kicker">01 / Selected work</p><h2 id="projects-title">Projects</h2></div><p>Things I’ve built and explored, with notes on how they work.</p></div>
    <div class="project-grid">{cards}</div>
  </section>
  <section class="section articles-section" id="articles" aria-labelledby="articles-title"><div class="container">
    <div class="section-heading"><div><p class="section-kicker">02 / The details</p><h2 id="articles-title">Articles</h2></div><p>Project READMEs, set up for a more comfortable read.</p></div>
    <ol class="article-list">{articles}</ol>
  </div></section>
  <section class="closing container"><p>Curious about the implementation?</p><a href="https://github.com/AlexZhai21" target="_blank" rel="noopener noreferrer">See all my work on GitHub <span aria-hidden="true">↗</span></a></section>
  """
    return shell(title="Projects & writing", description="Projects and articles by Alex Zhai, exploring robotics, machine learning, and visual computing.", body=body)


def article_page(project: dict[str, str]) -> str:
    source = (ROOT / project["source"]).read_text(encoding="utf-8")
    source = re.sub(r"\A# .+\n+", "", source, count=1)
    source = re.sub(r"(?m)^##\s*$\n?", "", source)
    if project["slug"] == "robot-arm":
        source = source.replace("outputs/can_demo_0.gif", "../assets/robot-demo.webp")
    rendered = MARKDOWN.render(source)
    rendered = rendered.replace("<img ", '<img loading="lazy" decoding="async" ')
    if project["slug"] == "svd":
        gallery = """<div class="example-block"><h2>What the ranks look like</h2><p>The same image, reconstructed with different numbers of singular values.</p>
          <div class="comparison-grid">
            <figure><img src="../assets/svd-original_grayscale.webp" alt="Original grayscale image of a dog in a field" loading="lazy" width="512" height="256"><figcaption>Original</figcaption></figure>
            <figure><img src="../assets/svd-rank_10.webp" alt="Rank 10 approximation of the same image" loading="lazy" width="512" height="256"><figcaption>Rank 10</figcaption></figure>
            <figure><img src="../assets/svd-rank_25.webp" alt="Rank 25 approximation of the same image" loading="lazy" width="512" height="256"><figcaption>Rank 25</figcaption></figure>
          </div>
        </div>"""
    else:
        gallery = ""
    body = f"""
  <div class="article-shell container">
    <a class="back-link" href="../index.html#projects"><span aria-hidden="true">←</span> All projects</a>
    <header class="article-header"><p class="section-kicker">{escape(project['kind'])} / Project notes</p><h1>{escape(project['title'])}</h1><p class="article-deck">{escape(project['description'])}</p><div class="article-actions"><a class="button button-dark" href="{project['github']}" target="_blank" rel="noopener noreferrer">View project on GitHub <span aria-hidden="true">↗</span></a><span>From the project README</span></div></header>
    <div class="article-rule"></div>
    <article class="prose" aria-label="Project article">{rendered}{gallery}</article>
    <div class="article-end"><p>That’s the project. The code and latest README live on GitHub.</p><a href="{project['github']}" target="_blank" rel="noopener noreferrer">Explore the repository <span aria-hidden="true">↗</span></a></div>
    <a class="back-link bottom-back" href="../index.html#articles"><span aria-hidden="true">←</span> Back to all articles</a>
  </div>
  """
    return shell(title=project["title"], description=project["description"], body=body, prefix="../", math=project["slug"] == "robot-arm")


def main() -> None:
    ARTICLES.mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for project in PROJECTS:
        (ARTICLES / f"{project['slug']}.html").write_text(article_page(project), encoding="utf-8")
    print("Built index.html and 2 article pages")


if __name__ == "__main__":
    main()
