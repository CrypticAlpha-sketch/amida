#!/usr/bin/env python3
"""Build pdf/index.html: a single, fully offline HTML file.

Inlines pdf.js, its worker, pdf-lib and pdf.js's CMaps (for PDFs whose
Japanese/Chinese/Korean fonts are not embedded) into src/editor.html.

    cd pdf && npm install && python3 build.py [node_modules_dir]
"""
import base64, json, os, re, sys

here = os.path.dirname(os.path.abspath(__file__))
nm = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(here, 'node_modules')
src = open(os.path.join(here, 'src', 'editor.html'), encoding='utf-8').read()

def safe(js):
    # keep the inlined text from closing or confusing the surrounding <script>
    return re.sub(r'</(script)', r'<\\/\1', js, flags=re.I).replace('<!--', '<\\!--')

def inline(m):
    return safe(open(os.path.join(nm, m.group(1)), encoding='utf-8').read())

def cmaps(m):
    d = os.path.join(nm, m.group(1))
    data = {f[:-6]: base64.b64encode(open(os.path.join(d, f), 'rb').read()).decode()
            for f in sorted(os.listdir(d)) if f.endswith('.bcmap')}
    return json.dumps(data, separators=(',', ':'))

out = re.sub(r'/\*@INLINE ([^*]+)\*/', inline, src)
out = re.sub(r'/\*@CMAPS ([^*]+)\*/', cmaps, out)
out = out.replace('<!-- Libraries are inlined by build.py; this file is the editable source. -->',
                  '<!-- Built by build.py from src/editor.html. Do not edit by hand. -->')
assert '@INLINE' not in out and '@CMAPS' not in out
path = os.path.join(here, 'index.html')
open(path, 'w', encoding='utf-8').write(out)
print(f'wrote {path} ({os.path.getsize(path) / 1e6:.2f} MB)')
