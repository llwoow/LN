"""Independent numerical checks for the explicitly stated textbook approximations.

This does not import the figure generator and does not solve a physical 2-D device.
Run from the repository root. The output records exactly what was recomputed.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
checks = []

def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)

def integrate(function, lower, upper, n=2000):
    h = (upper-lower)/n
    return h*(0.5*function(lower)+sum(function(lower+i*h) for i in range(1,n))+0.5*function(upper))

# Independently integrate the sheet-charge current law for multiple M and overdrive.
for m in [1.0, 1.2, 1.6]:
    for overdrive in [1., 2., 3., 4.]:
        vsat = overdrive/m
        for fraction in [0.05, 0.5, 0.95, 1.0]:
            voltage = fraction*vsat
            charge_integral = integrate(lambda v: overdrive-m*v, 0, voltage)
            closed = overdrive*voltage-0.5*m*voltage**2
            check(math.isclose(charge_integral, closed, rel_tol=1e-11), f'sheet-charge integral M={m}, Vov={overdrive}, fraction={fraction}')
        check(math.isclose(overdrive*vsat-0.5*m*vsat**2, overdrive**2/(2*m), rel_tol=1e-12), f'pinch-off continuity M={m}, Vov={overdrive}')
        check(math.isclose(overdrive-m*vsat, 0, abs_tol=1e-12), f'zero charge at drain-side pinch-off M={m}, Vov={overdrive}')

# Check that the plotted boundary shares the actual knee of each plotted curve.
output = (HERE/'assets/output.svg').read_text(encoding='utf-8')
polylines = re.findall(r'<polyline points="([^"]+)"', output)
check(len(polylines) == 5 and 'stroke-dasharray="8 6"' in output, 'four output curves with a dashed region boundary')
boundary_points = set(polylines[-1].split())
for idx, curve in enumerate(polylines[:4], 1):
    points = curve.split()
    plateau_y = points[-1].split(',')[1]
    knee = f'{120+160*idx:.3f},{plateau_y}'
    check(knee in points and knee in boundary_points, f'dashed boundary passes through the modeled V_GS{idx} knee')
check('线性区（非饱和区）' in output and '饱和区：沟道夹断后近似恒流' in output,
      'region labels match the original question terminology')

# Voltage fraction -> depth fraction, solved by bisection rather than the builder's inverse.
levels = []
previous = 0
for volts in [0, 300, 600, 900, 1200]:
    target = volts/1200
    lo, hi = 0., 1.
    for _ in range(80):
        mid = (lo+hi)/2
        if 2*mid-mid*mid < target: lo=mid
        else: hi=mid
    depth = 0. if volts==0 else 1. if volts==1200 else (lo+hi)/2
    check(math.isclose(2*depth-depth**2, target, abs_tol=1e-12), f'NPT potential at {volts} V')
    levels.append({'volts':volts,'depth_over_W':depth,'interval_over_W':depth-previous})
    previous=depth
intervals=[r['interval_over_W'] for r in levels[1:]]
check(all(b>a for a,b in zip(intervals,intervals[1:])), 'equal voltage increments have increasing depth increments in the chosen NPT model')
check(math.isclose(sum(intervals),1,abs_tol=1e-12), 'NPT intervals sum to full depletion width')

# Dimensionless Poisson equation and zero-field outer boundary, by finite differences.
f=lambda u:2*u-u*u
h=1e-4
for u in [0.05, 0.134, 0.293, 0.5, 0.8, 0.95]:
    first=(f(u+h)-f(u-h))/(2*h)
    second=(f(u+h)-2*f(u)+f(u-h))/h**2
    check(math.isclose(first,2*(1-u),abs_tol=1e-8), f'potential derivative and field sign at {u}W')
    check(math.isclose(second,-2,abs_tol=1e-6), f'constant space charge at {u}W')
check(math.isclose((f(1+h)-f(1-h))/(2*h),0,abs_tol=1e-9), 'NPT outer-boundary electric field is zero')

source=(HERE/'answer-source.html').read_text(encoding='utf-8')
rounded=['0.133975','0.292893','0.500000','1.000000']
check(all(f"{r['depth_over_W']:.6f}"==s for r,s in zip(levels[1:],rounded)), 'reported normalized depths independently reproduced')
check(all(x in source for x in rounded), 'answer contains independently checked depth values')

# Check the plotted levels against the independently solved depth fractions.
blocking=(HERE/'assets/blocking.svg').read_text(encoding='utf-8')
levels_y=[float(y) for y in re.findall(r'<path d="M60 (\d+\.\d+) H650"',blocking)]
check(len(levels_y)==3, 'three interior one-dimensional contours')
for row,y in zip(levels[1:4],levels_y):
    check(abs((y-370)/330-row['depth_over_W'])<3e-6, f'plotted center depth for {row["volts"]} V')
check(re.search(r'<path d="M60 700 H650"[^>]+stroke-dasharray="10 6"',blocking) and 'M60 835 H1240' in blocking,
      'center depletion boundary is dashed and the applied drain boundary spans the entire back contact')
check('y="700" width="589" height="70" fill="url(#neutral-center)"' in blocking,
      'near-neutral region is marked within the drift layer above the n+ substrate')
terminal_curves=re.findall(r'<path d="M650 (\d+\.\d+) C795 \1 995 (\d+\.\d+) 1170 (\d+\.\d+)"[^>]+stroke-dasharray="7 6"',blocking)
check(len(terminal_curves)==3 and all(321<float(end)<float(control)<float(start) for start,control,end in terminal_curves),
      'terminal curves start tangent to their center sections and remain below the floating rings')
check(all([float(curve[i]) for curve in terminal_curves]==sorted({float(curve[i]) for curve in terminal_curves}) for i in range(3)),
      'terminal curves preserve contour ordering at every control depth')
check(blocking.count('stop-opacity="0"')==4, 'three terminal contours and the near-neutral tint fade toward the right')
current=(HERE/'assets/current.svg').read_text(encoding='utf-8')
branches=re.findall(r'M(\d+) 303 Q\1 (\d+) \d+ \2 H(\d+) V220',current)
check(len(branches)==4 and all(int(y)>280 for _,y,_ in branches), 'four orange branches bend and run inside silicon before rising into S metal')
check(sorted(int(contact) for _,_,contact in branches)==[220,350,430,560], 'branches enter the intended n+ source contacts')
check(all(f'M{x} 849 V303' in current for x in (285,495)), 'current trunks begin within the extended section drain contact')

# The same shallow source diffusions must appear in all three operating-state drawings.
for name in ('structure', 'blocking', 'current'):
    svg=(HERE/f'assets/{name}.svg').read_text(encoding='utf-8')
    sources=re.findall(r'<rect x="(\d+)" y="280" width="30" height="(\d+)" fill="#b7d4ef"',svg)
    check(sources==[(str(x), '21') for x in (115,215,325,425,535,635)], f'{name}: six shallow n+ sources at the source-contact overlaps')
    check('y="280" width="1180" height="490" fill="#edf4fb"' in svg, f'{name}: shared extended drift layer')
zoom=(HERE/'assets/zoom.svg').read_text(encoding='utf-8')
check('y="220" width="135" height="33" fill="#b7d4ef"' in zoom, 'local view shows a source depth of about one quarter of the body depth')
check('M335 223 L405 223' in zoom and 'M405 223 L670 223' in zoom, 'local inversion layer connects the n+ source to the accumulation layer at the p-base surface edge')

# Verify the original exercise inputs listed in the resource manifest.
resource=ROOT/'resources/local/power-semiconductors'
local_resources_present=resource.is_dir()
if local_resources_present:
    originals=json.loads((resource/'manifest.json').read_text(encoding='utf-8'))['files']
    check(len(originals)==5, 'five original exercise inputs declared')
    for entry in originals:
        p=resource/entry['name']
        check(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'], f'unchanged original: {p.name}')
        relative=p.relative_to(ROOT).as_posix()
        ignored=subprocess.run(['git','check-ignore','-q','--',relative],cwd=ROOT).returncode==0
        tracked=subprocess.run(['git','ls-files','--error-unmatch','--',relative],cwd=ROOT,capture_output=True).returncode==0
        check(ignored and not tracked, f'Git ignores untracked original: {p.name}')

report={'scope':'Textbook models, figure geometry and local resources; no 2-D TCAD, avalanche, or experimental validation.',
        'local_resources_verified':local_resources_present,
        'passed':len(checks),'checks':checks,'NPT_normalized_potential_levels':levels}
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if not local_resources_present:
    print('Local source PDFs unavailable in this checkout; original-file checks skipped.')
print(f'Passed {len(checks)} independent numeric/resource checks; report: {HERE / "verification.json"}')
