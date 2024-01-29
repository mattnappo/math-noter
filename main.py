import sys
import os.path
from openai import OpenAI
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileModifiedEvent, PatternMatchingEventHandler
import subprocess

with open("prompt.txt") as f:
    SYSTEM_PROMPT = f.read()

with open("template.tex") as f:
    LATEX_TEMPLATE = f.read()

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
    def __init__(self, out_dir='./out/'):
        super().__init__(patterns=['*.txt'], ignore_patterns=['prompt.txt'])
        self.out_dir = out_dir
        self.title = "Test Notes"
        self.author= "Matt"

    def tex_filename(self, base_filename):
        fname = os.path.basename(base_filename)
        return os.path.join(self.out_dir, change_ex(fname, 'tex'))

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
                code = LATEX_TEMPLATE.format(self.title, self.author, latex)
                f.write(code)

            self.recompile(self.tex_filename(event.src_path))
            
def main(in_dir):
    observer = Observer()
    handler = Handler()
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
