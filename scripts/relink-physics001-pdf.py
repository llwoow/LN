"""Change playback URI annotations only; preserve all supplied printed PDF pages.
Requires PyMuPDF. This does not publish LN; links become live after the PR is deployed.
"""
from pathlib import Path
import fitz,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'courses/hs-physics/physics-001'
SOURCE=BASE/'verification/physics001-v1.2-source.pdf'
pdf=fitz.open(SOURCE);changes=[]
for page in pdf:
 for link in page.get_links():
  uri=link.get('uri','');m=re.search(r'/#q(\d+)/(q\d+[ab]?)',uri)
  if m:
   target='https://ln-llwoow.lqw193wql.chatgpt.site/#course/hs-physics/physics-001-q'+m[1].zfill(2)+'/motion-'+m[2]
   changes.append({'page':page.number+1,'old':uri,'new':target});link['uri']=target;page.update_link(link)
pdf.save(BASE/'files/physics001-solutions.pdf',garbage=4,deflate=True)
(BASE/'verification/pdf-link-migration.json').write_text(json.dumps({'pages':len(pdf),'changes':changes,'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print(f'Updated {len(changes)} annotations; retained {len(pdf)} printed pages.')
