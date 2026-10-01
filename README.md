# Alex Zhai — portfolio

A small static portfolio with project pages built from the READMEs for [Action Chunking Transformers](https://github.com/AlexZhai21/ActionChunkingTransformers) and [Image Approximation using SVD](https://github.com/AlexZhai21/Image-Approximation-using-SVD).

## Preview locally

Run `python -m http.server 8000` from this folder, then visit `http://localhost:8000`.

## Update the articles

The Markdown sources are in `content/`. Copy in the latest project README when you want to refresh an article, then run:

```bash
python -m pip install -r requirements-build.txt
python build.py
```

Commit the updated `content/` files and generated HTML together. `build.py` adjusts the robot demo image path for this site and adds a visual comparison to the SVD article.

## Publish with GitHub Pages

Create a public repository named `AlexZhai21.github.io`, push this folder's contents to its default branch, then set **Settings → Pages → Build and deployment → Deploy from a branch** and select the default branch and `/ (root)`. The site will be available at `https://alexzhai21.github.io/` after GitHub publishes it.

This site is plain HTML, CSS, and a small amount of JavaScript. No runtime build service or JavaScript framework is needed. The ACT article loads MathJax to render equations from its README. The SVD article includes a browser-based image upload and rank slider; it processes images locally at up to 192 pixels for a responsive preview. The original Python Streamlit app remains in its project repository.
