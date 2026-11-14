"""Static QA server with byte ranges so native video seeking matches CDN hosting.
Run from repository root: python tests/serve.py 4173
"""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import re,sys
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  self.bounds=None
  path=Path(self.translate_path(self.path))
  if not path.is_file():return super().send_head()
  file=path.open('rb');size=path.stat().st_size;start,end=0,size-1
  value=self.headers.get('Range')
  if value:
   m=re.fullmatch(r'bytes=(\d*)-(\d*)',value)
   if not m or not any(m.groups()):file.close();self.send_error(416);return None
   if m[1]:start=int(m[1]);end=min(int(m[2]),size-1) if m[2] else size-1
   else:start=max(0,size-int(m[2]))
   if start>=size or end<start:file.close();self.send_error(416);return None
   self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.bounds=(start,end);file.seek(start)
  else:self.send_response(200)
  self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1));self.end_headers();return file
 def copyfile(self,source,output):
  if self.bounds is None:return super().copyfile(source,output)
  remaining=self.bounds[1]-self.bounds[0]+1
  try:
   while remaining:
    block=source.read(min(65536,remaining))
    if not block:break
    output.write(block);remaining-=len(block)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*args):pass
if __name__=='__main__':
 ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1]) if len(sys.argv)>1 else 4173),Handler).serve_forever()
