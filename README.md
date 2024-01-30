# Math Noter

Write your math notes in English in any editor, and have them converted to LaTeX in real time (on save).

# Setup

1. Install Python dependencies:
```pip install -r requirements.txt```

2. Make sure `pdflatex` is installed and in your `PATH`. You can install it via TeX Live [here](https://ctan.org/pkg/texlive).
3. Set the `$OPENAI_API_KEY` environment variable appropriately.

# Usage
Create a folder to hold your notes, which should be plain `.txt` files:

```mkdir notes/```

Then run the script on the directory

```python main.py notes/```

Now, any time a `.txt` file is saved in that folder, the pdf will be automatically regenerated, and can be found in `out/`.
