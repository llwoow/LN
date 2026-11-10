"""Verify unchanged page rendering and LN anchor destinations, independently of LaTeX."""
from pathlib import Path
import fitz,json,hashlib,runpy
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'courses/hs-physics/physics-001'
A=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
source=fitz.open(BASE/'verification/physics001-v1.2-source.pdf');current=fitz.open(BASE/'files/physics001-solutions.pdf')
assert len(source)==len(current)==84
links=[]
for i,(before,after) in enumerate(zip(source,current)):
 assert before.rect==after.rect
 assert before.get_pixmap().samples==after.get_pixmap().samples,('Changed printed page',i+1)
 for l in after.get_links():
  if l.get('uri'):
   uri=l['uri'];assert uri.startswith('https://ln-llwoow.lqw193wql.chatgpt.site/#course/hs-physics/')
   parts=uri.split('#course/hs-physics/')[1].split('/');body=A(ROOT/'courses/hs-physics/lessons'/(parts[0]+'.js'))['html'];assert 'id="'+parts[1]+'"' in body
   links.append(uri)
assert len(set(links))==20 and len(links)==22
(BASE/'verification/pdf-verification.json').write_text(json.dumps({'printedPagesPixelIdentical':84,'playbackAnnotations':len(links),'distinctPlaybackTargets':len(set(links)),'everyTargetExistsInLN':True,'pdfSHA256':hashlib.sha256((BASE/'files/physics001-solutions.pdf').read_bytes()).hexdigest()},indent=2)+'\n')
print('84 printed pages pixel-identical; 22 playback annotations reach 20 LN anchors.')
