"""Original sequence inspection; the short translated sequence is synthetic."""
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
import Bio
root=Path(__file__).resolve().parent
import urllib.request, io, hashlib
url='https://raw.githubusercontent.com/biopython/biopython/caf68c465fc6c571e4c67a8833f73bdfedcb1f89/Doc/examples/ls_orchid.fasta'
raw=urllib.request.urlopen(url,timeout=30).read()
assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\\0'+raw).hexdigest()=='978e198c4791f49f528d108367ac0109fd46b57f'
records=list(SeqIO.parse(io.StringIO(raw.decode()),'fasta'))
print('Biopython',Bio.__version__,'records',len(records),'first length',len(records[0]),'GC fraction',gc_fraction(records[0].seq))
s=Seq('ATGGCCATTGTA')
print('synthetic',s,'standard-code translation',s.translate(),'shifted triplets',s[1:10].translate(),'one substitution',Seq('ATGACCATTGTA').translate())
print('The orchid FASTA includes rRNA/ITS regions: do not interpret blind translation as an expressed protein.')
