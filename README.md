# Alex Zhai's portfolio

A small site with project articles. The article text and project details are in `content/`.

## Preview on your computer

Open PowerShell in this folder and run:

```powershell
python -m pip install -r requirements-build.txt
python build.py
python -m http.server 8000
```

Open <http://localhost:8000> in your browser. Press Ctrl+C in PowerShell when finished. After an edit, run `python build.py` again and refresh the page.

## Edit an article

Open its Markdown file in `content/`, change the text, and save it. For example:

- SVD article: `content/svd.md`
- Text immediately below the SVD **Try it** heading: `content/_svd-demo.md`
- Robot arm article: `content/robot-arm.md`
- GPT-2 article: `content/gpt-2.md`

The lines between the two `---` markers at the top of each article set the title, date, short home page title, description, and GitHub link. Keep dates in `YYYY-MM-DD` format. The rest of the file is normal Markdown. Set `math: true` if the article uses `$...$` or `$$...$$` equations. An optional `image: assets/your-image.webp` adds a preview image to the project card; without one, the card uses the short title.

## Add an article

1. Copy `content/_template.md` to a new file in `content/`, for example `content/new-project.md`. Do not start the new filename with `_`.
2. Fill in its details and write the article below the second `---` line. Put any images in `assets/` and link to them from the article as `../assets/your-image.webp`.
3. Run `python build.py` and refresh the local preview. The builder adds the project card, article link, date, and page automatically. Articles are ordered newest first.

The dates currently shown are the first Git commit dates for each project: GPT-2 on August 18, 2026; robot arm on August 20, 2026; SVD on September 16, 2026.

## Publish updates

This folder is prepared for a GitHub Pages repository called `AlexZhai21.github.io`. It is not connected to a remote repository yet. Create a public GitHub repository with that name (without adding a README or other starter files), then run these commands from this folder:

```powershell
git remote add origin https://github.com/AlexZhai21/AlexZhai21.github.io.git
git push -u origin main
```

After the first push, open the repository on GitHub and choose **Settings → Pages → Build and deployment → Source → GitHub Actions**. If the first workflow run happened before this setting was saved, open **Actions → Publish portfolio → Run workflow** once. Later pushes to `main` build and publish automatically. GitHub will show the live address in the Pages settings.

The simplest editing route after that is to open a file in `content/` on GitHub, click the pencil icon, make the change, and commit it to `main`. The workflow rebuilds the site automatically. For a local edit, use:

```powershell
python build.py
git add content index.html articles assets
git commit -m "Update portfolio"
git push origin main
```

The build step is useful for the local preview; the GitHub workflow also builds after the push. If you add a new article, include its generated page in the commit. If you edit only on GitHub, you do not need to run Python yourself.

The SVD demo runs in visitors' browsers and accepts their images there. The original Python Streamlit app is linked from the SVD article and repository.
