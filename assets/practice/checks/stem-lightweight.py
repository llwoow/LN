"""Original small verification tasks. Uses public CC0 data and installed SymPy."""
import csv, json, math
from pathlib import Path
import sympy
root=Path(__file__).resolve().parent
rows=list(csv.DictReader((root/'data/penguins.csv').open()))
valid=[r for r in rows if r['flipper_length_mm']!='NA' and r['body_mass_g']!='NA']
def corr(data):
 x=[float(r['flipper_length_mm']) for r in data]; y=[float(r['body_mass_g']) for r in data]
 mx=sum(x)/len(x); my=sum(y)/len(y)
 return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
x,h=sympy.symbols('x h',real=True)
quotient=sympy.simplify(((x+h)**2-x**2)/h)
print(json.dumps({'sympy_version':sympy.__version__,'difference_quotient':str(quotient),'limit':str(sympy.limit(quotient,h,0)),'rows':len(rows),'pairs':len(valid),'r':corr(valid),'by_species':{s:corr([r for r in valid if r['species']==s]) for s in sorted({r['species'] for r in valid})}},indent=2))
