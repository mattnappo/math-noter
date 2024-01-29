import sys
from openai import OpenAI
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileModifiedEvent
import subprocess

SYSTEM_PROMPT='You are an expert at converting regular math-english into LaTeX. Please respond with ONLY the LaTeX, and nothing else. If you respond with anything but the direct translation of my prompt into LaTeX, then you will have failed me as a helpful AI assistant. It is important to turn my words into symbols (for example "gamma" into "\\gamma"), but it is also okay to keep my words in English when necessary, or when otherwise ambiguous. Additional rules: the words "theorem" and "proof" and "lemma" and "definition" and similar words should be bolded, and the content of the theorem/proof/lemma should be in a nice box. when making an example/lemma/theorem/proof section, just say \\begin{theorem}. Do not also type the word "theorem" or else the word "theorem" will show up twice. When you see a list of text separated by newlines, please use the enumerate package to list them nicely. If there are labels to each listing such as (a) (b) or 1. 2., please use the appropriate label as well. When I write "null set" or "empty set" please convert this into "\\varnothing". When I write < and > please use \\langle and \\rangle.'

LATEX_TEMPLATE=r'''\documentclass[12pt]{{article}}
\usepackage[margin=0.80in]{{geometry}}

\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amsthm}}
\usepackage{{amssymb}}
\usepackage{{enumerate}}
\usepackage{{enumitem}}
\usepackage{{graphicx}}
\usepackage[all]{{xy}}
\usepackage{{wrapfig}}

\newtheorem{{theorem}}{{Theorem}}
\newtheorem{{definition}}{{Definition}}
\newtheorem{{example}}{{Example}}

\title{{Notes}}
\author{{Author}}
\date{{\today}}

\begin{{document}}

\maketitle

{}

\end{{document}}
'''

client = OpenAI()

def get_latex(text):
    print("getting latex for", text)
    completion = client.chat.completions.create(
    temperature=0.0,
    #model="gpt-4",
    model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    )

    print("completed:", completion.choices[0].message)
    return completion.choices[0].message.content

def change_ex(filename, new_ex):
    return ''.join(filename.split('.')[:-1]) + '.' + new_ex

class Handler(FileSystemEventHandler):
    def __init__(self, filename, out_dir='./out/'):
        self.filename = filename
        self.out_dir = out_dir
        self.output = out_dir + change_ex(filename, 'tex')
        self.pdf = out_dir + change_ex(filename, 'pdf')
        self.text = self.read()

    def read(self):
        with open(self.filename, 'r') as f:
            return f.read()
    
    # return index at which two strings differ
    def diff_pos(self, text):
        pass

    def recompile(self):
        subprocess.run(f'mkdir -p {self.out_dir}'.split())
        subprocess.run(f'pdflatex -output-directory {self.out_dir} {self.output}'.split())

    def dispatch(self, event):
        print("event: ", str(event))
        if isinstance(event, FileModifiedEvent):
            print("HANDLING MODIFICATION")
            new = self.read()
            # compare new text with old text
            # TODO
            # naive approach for now
            latex = get_latex(new)
            with open(self.output, 'w') as f:
                code = LATEX_TEMPLATE.format(latex)
                f.write(code)

            self.recompile()
            
def main(filename):
    observer = Observer()
    handler = Handler(filename)
    observer.schedule(handler, filename)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python main.py <input filename>")
        sys.exit(1)

    filename = sys.argv[1]
    main(filename)
