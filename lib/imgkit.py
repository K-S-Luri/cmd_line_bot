import imgkit
import os

def from_string(string, output_path, options=None, toc=None, cover=None, css=None, config=None, cover_first=None):
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print("Write to %s" % output_path)
    imgkit.from_string(string, output_path,
                       options=options, toc=toc, cover=cover, css=css, config=config, cover_first=cover_first)
