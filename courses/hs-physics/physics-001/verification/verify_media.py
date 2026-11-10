from pathlib import Path
from PIL import Image,ImageChops
import json,subprocess,math,sys
import numpy as np
import render_motion as R
P=Path(__file__).resolve().parent.parent/'animations';manifest=json.loads((P/'manifest.json').read_text());assert len(manifest['clips'])==20
specs={x['id']:x for x in R.CLIPS};selected=set(sys.argv[1:]);reports=[]
if selected and (P/'qa/media-verification.json').exists():reports=[x for x in json.loads((P/'qa/media-verification.json').read_text())['clips'] if x['id'] not in selected]
for clip in manifest['clips']:
 cid=clip['id']
 if selected and cid not in selected:continue
 p=P/'gifs'/clip['gif'];im=Image.open(p);elapsed=0;chosen={0,im.n_frames//3,2*im.n_frames//3,im.n_frames-2};metadata=json.loads((P/'qa'/f'{cid}-timeline.json').read_text());checks=[];count=im.n_frames
 for k in range(count):
  im.seek(k)
  if k in chosen:
   index=round(elapsed/100)
   if index<len(metadata):
    z=metadata[index];c,_=specs[cid]['fn'](z['t'],z['hold']);expected=c.image().quantize(palette=R.PAL,dither=Image.Dither.NONE).convert('RGB');actual=im.convert('RGB');diff=np.array(ImageChops.difference(actual,expected));mx=int(diff.max());checks.append(dict(gifFrame=k,sourceFrame=index,maximumChannelDifference=mx));assert mx==0,(cid,k,mx)
  elapsed+=im.info.get('duration',0)
 assert abs(elapsed-100*clip['framesPlanned'])<=1,(cid,elapsed,clip['framesPlanned'])
 assert im.size==(960,560)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,nb_frames','-of','json',str(P/'video'/clip['video'])]));stream=info['streams'][0]
 assert stream['codec_name']=='h264' and stream['width']==960 and stream['height']==560
 assert abs(float(info['format']['duration'])-elapsed/1000)<.02
 reports.append(dict(id=cid,gifFrames=count,durationSeconds=elapsed/1000,gifPixelParity=checks,videoCodec=stream['codec_name'],videoFrames=int(stream['nb_frames']),gifBytes=p.stat().st_size))
 print(cid,'verified',count,'GIF frames',flush=True)
(P/'qa/media-verification.json').write_text(json.dumps(dict(clips=reports,count=20,description='GIF decoded frames compared pixel-for-pixel with the same physical renderer used for the PDF sheets; MP4 timing and codec checked.'),ensure_ascii=False,indent=2));print('all 20 media files passed')
