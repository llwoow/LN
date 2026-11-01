"""Reproduce one literal-character query, not a literary classification."""
import base64, hashlib, json, urllib.request
sha='6bf7e34b40b86e14edb21ae26c28d13b6c59a0a8'
url='https://api.github.com/repos/chinese-poetry/chinese-poetry/git/blobs/'+sha
request=urllib.request.Request(url,headers={'User-Agent':'LN-learning-reproduction'})
response=json.load(urllib.request.urlopen(request,timeout=30))
raw=base64.b64decode(response['content'])
assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha
records=json.loads(raw);matches=[r for r in records if any('月' in p for p in r['paragraphs'])]
print(json.dumps({'source':url,'git_blob_sha':sha,'records':len(records),'literal_matches':len(matches),
 'limits':'Non-random slice. 月 can mean a month, not only the moon; literal occurrence does not identify nostalgia or author intention.'},ensure_ascii=False,indent=2))
