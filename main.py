import sys
from openai import OpenAI
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileModifiedEvent, PatternMatchingEventHandler
import subprocess

SYSTEM_PROMPT='You are an expert at converting regular math-english into LaTeX. Please respond with ONLY the LaTeX, and nothing else. If you respond with anything but the direct translation of my prompt into LaTeX, then you will have failed me as a helpful AI assistant. It is important to turn my words into symbols (for example "gamma" into "\\gamma"), but it is also okay to keep my words in English when necessary, or when otherwise ambiguous. Additional rules: the words "theorem" and "proof" and "lemma" and "definition" and similar words should be bolded, and the content of the theorem/proof/lemma should be in a nice box. when making an example/lemma/theorem/proof section, just say \\begin{theorem}. Do not also type the word "theorem" or else the word "theorem" will show up twice. When you see a list of text separated by newlines, please use the enumerate package to list them nicely. If there are labels to each listing such as (a) (b) or 1. 2., please use the appropriate label as well. When I write "null set" or "empty set" please convert this into "\\varnothing". When I write < and > please use \\langle and \\rangle. Finally, you can fix my spelling errors (if you are sure that it is a spelling error), but please do not do anything else to the english I write. Thanks!'

LATEX_TEMPLATE=r'''\documentclass[12pt]{{article}}
\usepackage[margin=0.80in]{{geometry}}

\usepackage{{mdframed}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amsthm}}
\usepackage{{amssymb}}
\usepackage{{enumerate}}
\usepackage{{enumitem}}
\usepackage{{graphicx}}
\usepackage[all]{{xy}}
\usepackage{{wrapfig}}

\newmdtheoremenv{{theorem}}{{Theorem}}
\newmdtheoremenv{{definition}}{{Definition}}
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

class Handler(PatternMatchingEventHandler):
    def __init__(self, patterns, out_dir='./out/'):
        super().__init__(patterns=patterns)
        self.out_dir = out_dir

    def tex_filename(self, base_filename):
        return self.out_dir + change_ex(base_filename, 'tex')

    #def pdf_filename(base_filename):
    #    return out_dir + change_ex(base_filename, 'pdf')

    def read(self, fname):
        with open(fname, 'r') as f:
            return f.read()
    
    # return index at which two strings differ
    def diff_pos(self, text):
        pass

    def recompile(self, tex_file):
        subprocess.run(f'mkdir -p {self.out_dir}'.split())
        subprocess.run(f'pdflatex -output-directory {self.out_dir} {tex_file}'.split())

    def on_modified(self, event):
        print("event: ", str(event))
        if isinstance(event, FileModifiedEvent):
            print("HANDLING MODIFICATION")
            new = self.read(event.src_path)
            # compare new text with old text
            # TODO
            # naive approach for now
            latex = get_latex(new)
            with open(self.tex_filename(event.src_path), 'w') as f:
                code = LATEX_TEMPLATE.format(latex)
                f.write(code)

            self.recompile(self.tex_filename(event.src_path))
            
def main(in_dir):
    observer = Observer()
    handler = Handler(patterns=["*.txt"])
    observer.schedule(handler, in_dir)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python main.py <input directory>")
        sys.exit(1)

    in_dir = sys.argv[1]
    main(in_dir)
