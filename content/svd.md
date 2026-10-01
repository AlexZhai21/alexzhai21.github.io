Built an SVD class to perform rank approximations on images!
svd.py contains my implementation of an SVD class that takes in an image and outputs a rank approximation.
rank_comparison contains the rank approximated images for a multitude of images.
More detailed Read Me coming soon!

## Interactive app

Run the local Streamlit app with:

```bash
python -m streamlit run app.py
```

The app lets you upload an image and drag a live rank slider to watch the SVD approximation update.

For a public link later, deploy this repo to Streamlit Community Cloud or Hugging Face Spaces with `app.py` as the entry point and `requirements.txt` as the dependency file.
