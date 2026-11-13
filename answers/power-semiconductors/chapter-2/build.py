"""Build original answer figures and offline HTML. PDFs are printed from the HTML.

Run from the repository root: python answers/power-semiconductors/chapter-2/build.py
No textbook images or full textbook text are embedded in the deliverable.
"""
from pathlib import Path
import html
import json
import math
import re
import subprocess
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = HERE / 'assets'
ASSETS.mkdir(exist_ok=True)

COLORS = {'n': '#edf4fb', 'np': '#b7d4ef', 'p': '#f7e6e7', 'pp': '#dfafb7',
          'metal': '#606873', 'gate': '#bcaed9', 'oxide': '#f4d285',
          'dielectric': '#f2f0e9', 'passivation': '#c7ded4'}

def text(x, y, s, size=22, anchor='start', fill='#17202b', extra=''):
    label = re.sub(r'([VI])_([A-Za-z]+[0-9]?)', r'\1<tspan baseline-shift="sub" font-size="70%">\2</tspan>', html.escape(s))
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" {extra}>{label}</text>'

def rect(x, y, w, h, fill, stroke='#515b68', extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.4" {extra}/>'

def path(d, stroke='#283744', width=2, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'

def wrap(content, title, width=1300, height=800):
    marker_id = 'arrow-' + hashlib.sha256(title.encode()).hexdigest()[:8]
    content = content.replace('url(#arrow)', f'url(#{marker_id})')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">'
            f'<title>{html.escape(title)}</title><defs><marker id="{marker_id}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 Z" fill="context-stroke"/></marker></defs>'
            '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",Arial,sans-serif}path,rect,line{vector-effect:non-scaling-stroke}</style>'
            f'<rect width="100%" height="100%" fill="white"/>{content}</svg>')

def device(mode='structure'):
    substrate_top, drain_top, chip_bottom = 770, 835, 870
    c = [text(60, 40, 'N 沟道增强型 · 平面栅 VDMOS', 26),
         text(60, 72, '结构尺寸不按比例，局部结构放大显示', 20)]
    # Silicon is continuous below y=280. The n+ source and p+ contact lie INSIDE p-base.
    c += [rect(60, 280, 1180, substrate_top-280, COLORS['n']),
          rect(60, substrate_top, 1180, drain_top-substrate_top, COLORS['np']),
          rect(60, drain_top, 1180, chip_bottom-drain_top, COLORS['metal'])]
    # Interlayer dielectric is physically separate from gate oxide and passivation.
    c += [rect(60, 164, 1180, 116, COLORS['dielectric']),
          rect(60, 148, 1180, 16, COLORS['passivation'])]
    for idx, cx in enumerate([180, 390, 600], 1):
        c.append(path(f'M{cx-80} 280 C{cx-78} 342 {cx-53} 370 {cx} 370 C{cx+53} 370 {cx+78} 342 {cx+80} 280 Z', '#a9616f', 1.6, COLORS['p']))
        c += [rect(cx-65, 280, 30, 21, COLORS['np']), rect(cx+35, 280, 30, 21, COLORS['np']),
              rect(cx-16, 280, 32, 30, COLORS['pp']), rect(cx-45, 195, 90, 85, COLORS['metal'])]
        c.append(text(cx, 349, 'p-base', 19, 'middle'))
        if mode == 'structure':
            c.append(text(cx, 397, f'元胞 {idx}', 20, 'middle'))
    # Source metal touches both source regions and body contact via the window.
    c.append(rect(100, 170, 560, 25, COLORS['metal']))
    c.append(text(380, 189, '源极金属 S（源区与体区短接）', 19, 'middle', '#fff'))
    for x, w in [(60, 65), (235, 100), (445, 100), (655, 65)]:
        c += [rect(x, 250, w, 26, COLORS['gate']), rect(x, 276, w, 4, COLORS['oxide'])]
    # Floating p+ rings are not connected to either source or gate metal.
    for idx, x in enumerate([850, 980, 1110], 1):
        c.append(path(f'M{x-20} 280 L{x-20} 299 Q{x-20} 321 {x} 321 Q{x+20} 321 {x+20} 299 L{x+20} 280 Z', '#a9616f', 1.6, COLORS['pp']))
        c.append(text(x, 341, f'FR{idx}', 18, 'middle'))
    c += [path('M765 100 L765 142', '#7d8690', 1, extra='stroke-dasharray="5 5"'),
          text(360, 105, '有源区：三个重复条形元胞剖面', 22, 'middle'),
          text(995, 110, '终端区：P⁺ 浮置场限环', 23, 'middle'),
          text(995, 136, '（Floating Field Rings）', 20, 'middle'),
          text(650, substrate_top+38, 'n⁺ 衬底（重掺杂 n 型）', 23, 'middle')]
    if mode != 'blocking':
        c.append(text(650, drain_top+26, 'D：背面漏极金属', 21, 'middle', '#fff'))
    if mode == 'structure':
        c += [text(112, 137, 'n⁺ 源区', 21, 'middle'),
              text(222, 137, 'p⁺ 体接触区', 21, 'middle'),
              text(398, 137, '多晶硅栅极 G', 21, 'middle'),
              text(1258, 165, '正面钝化层（绝缘保护）', 20),
              text(1258, 207, '源极接触窗口', 21),
              text(1258, 246, '层间绝缘介质', 21),
              text(747, 244, '薄栅氧化层 SiO₂', 21),
              text(650, 594, 'n⁻ 漂移区（轻掺杂 n 型）', 28, 'middle'),
              rect(554, 195, 92, 85, 'none', '#fff', 'stroke-dasharray="4 4"'),
              text(60, 904, '多晶硅栅极在剖面外汇流，焊盘开窗省略。场限环上方由绝缘介质和钝化层覆盖。', 21)]
        for route, tx, ty in [
            ('M112 143 L126 167 V286', 126, 286),
            ('M222 143 L180 169 V289', 180, 289),
            ('M398 143 H242 V233 L265 258', 265, 258),
            ('M1249 158 H1190', 1190, 158),
            ('M1249 200 H722 L646 214', 646, 214),
            ('M1249 239 H1170', 1170, 239),
            ('M738 242 L709 278', 709, 278),
        ]:
            c += [path(route, '#fff', 3.2), path(route, width=1.2),
                  f'<circle cx="{tx}" cy="{ty}" r="2.4" fill="#283744" stroke="white" stroke-width="0.8"/>']
    elif mode == 'blocking':
        # Keep the model depth ratios in the active area. Terminal strokes
        # fade to show that the sketch does not locate their endpoints.
        y0, W = 370, 330
        for volts, color in [(300, '#006b86'), (600, '#145a47'), (900, '#9b5300')]:
            y = y0 + W * (1 - math.sqrt(1 - volts / 1200))
            gradient = f'terminal-{volts}'
            c += [f'<defs><linearGradient id="{gradient}" gradientUnits="userSpaceOnUse" x1="910" x2="1170">'
                  f'<stop stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>'
                  '</linearGradient></defs>',
                  path(f'M60 {y:.3f} H650', color, 2.6),
                  path(f'M650 {y:.3f} C795 {y:.3f} 995 {y-28:.3f} 1170 {y-68:.3f}',
                       f'url(#{gradient})', 2, extra='stroke-dasharray="7 6"'),
                  text(77, y-8, f'{volts} V', 21, fill=color)]
        boundary = y0 + W
        c += [text(365, 392, '等势线靠近主结较密', 20, 'middle'),
              text(992, 195, 'V_GS = 0，V_DS = 1200 V', 23, 'middle'),
              text(992, 229, 'S = G = 0 V，近中性体区 ≈ 0 V', 21, 'middle'),
              text(992, 261, '浮置场限环与源极金属隔离', 21, 'middle'),
              text(964, 591, '终端区等势线仅示意', 22, 'middle'),
              text(964, 622, '实际位置需二维仿真确定', 21, 'middle'),
              text(964, 691, '耗尽边界只标出中心区的一维结果', 19, 'middle'),
              '<defs><linearGradient id="neutral-center" gradientUnits="userSpaceOnUse" x1="515" x2="650">'
              '<stop stop-color="#eae2f5"/><stop offset="1" stop-color="#eae2f5" stop-opacity="0"/>'
              '</linearGradient></defs>',
              rect(61, boundary, 589, substrate_top-boundary, 'url(#neutral-center)', 'none'),
              path(f'M60 {boundary} H650', '#533178', 2.6, extra='stroke-dasharray="10 6"'),
              text(77, boundary-10, '1200 V · 中心区耗尽边界 y = W', 21, fill='#533178'),
              text(77, boundary+42, '未耗尽的 n⁻ 漂移区（+1200 V，一维近似）', 21, fill='#533178'),
              path(f'M60 {drain_top} H1240', '#533178', 3),
              text(650, drain_top+26, 'D = +1200 V（背面漏极金属，全宽等势）', 22, 'middle', '#fff'),
              text(60, 904, '中心区采用一维未穿通近似。终端虚线渐隐表示实际延伸位置待定。', 21)]
    elif mode == 'current':
        for x, left_contact, right_contact in [(285, 220, 350), (495, 430, 560)]:
            # Keep the highlighted surface layers and the orange streamlines
            # entirely on the silicon side of the oxide boundary at y=280.
            surface_y = 289
            c.append(rect(x-25.5, 284, 51, 10, '#9edcc0', '#14634c'))
            c.append(path(f'M{x} {drain_top+14} V303', '#b45000', 2.8))
            c.append(path(f'M{x} 590 V530', '#b45000', 2.8, extra='marker-end="url(#arrow)"'))
            for sign, contact in [(-1, left_contact), (1, right_contact)]:
                blue_start = min(x + sign * 25.5, x + sign * 40)
                c.append(rect(blue_start, 284, 14.5, 10, '#9bd9f4', '#006b86'))
                c.append(path(f'M{x} 303 Q{x} {surface_y} {x+sign*14} {surface_y} H{contact} V220',
                              '#b45000', 2.8, extra='marker-end="url(#arrow)"'))
        c += [rect(840, 395, 32, 15, '#9bd9f4', '#006b86'), text(882, 410, 'p-base 表面 n 型反型层', 22),
              rect(840, 429, 32, 15, '#9edcc0', '#14634c'), text(882, 444, 'n⁻ 表面电子积累层', 22),
              text(350, 395, 'JFET 区', 21), path('M345 390 L285 350', width=1.3),
              text(90, 580, 'n⁻ 漂移区', 24),
              text(840, 498, 'G = +15 V', 23), text(840, 532, 'S = 0 V，D > 0 V', 22),
              text(840, 578, '传统电流 D → S', 22, fill='#934200'),
              text(840, 612, '电子运动 S → D', 22),
              text(60, 904, '小正漏压下的代表性流线。蓝、绿薄层在硅侧示意加厚，橙线与栅氧分开。', 21)]
    return wrap(''.join(c), {'structure':'图1 三元胞平面栅功率 MOSFET 与场限环', 'blocking':'图3 关断时的定性等势线', 'current':'图4 正向导通的传统电流路径'}[mode],
                width=1500 if mode == 'structure' else 1300, height=930)

def zoom():
    c = [text(45, 35, '栅 / 源绝缘与表面沟道局部放大', 25), rect(60, 220, 700, 150, COLORS['n']),
         path('M60 220 L405 220 C397 310 350 355 260 355 L60 355 Z', '#a9616f', 1.7, COLORS['p']),
         rect(200, 220, 135, 33, COLORS['np']), rect(95, 220, 70, 45, COLORS['pp']),
         rect(60, 65, 700, 155, COLORS['dielectric']), rect(95, 120, 190, 100, COLORS['metal']),
         rect(95, 95, 520, 25, COLORS['metal']), rect(315, 165, 370, 47, COLORS['gate']),
         rect(315, 212, 370, 8, COLORS['oxide']),
         path('M335 223 L405 223', '#006b86', 5), path('M405 223 L670 223', '#145a47', 5),
         text(380, 114, 'S 源极金属', 19, 'middle', '#fff'), text(495, 194, 'G 多晶硅栅', 21, 'middle'),
         text(265, 244, 'n⁺', 23, 'middle'), text(130, 248, 'p⁺', 23, 'middle'), text(260, 327, 'p-base', 23, 'middle'),
         text(650, 327, 'n⁻', 23, 'middle'),
         text(825, 100, 'S 金属与 G 之间：层间介质', 21),
         path('M810 105 L630 140', width=1.5),
         text(825, 160, 'G 与硅之间：薄栅氧', 21), path('M810 165 L677 216', width=1.5),
         text(825, 220, '绿线：n 型表面的电子积累层', 21), path('M810 225 L600 223', '#145a47', 1.4),
         text(825, 280, '蓝线：p 型表面的 n 反型层', 21), path('M810 285 L369 223', '#006b86', 1.4),
         text(60, 410, '反型并不把整个 p-base 改掺杂成 n 型；两种表面层都不位于氧化物内部。', 22)]
    return wrap(''.join(c), '图1b 源栅绝缘与沟道、积累区局部放大', 1300, 450)

def output_curves():
    c = [text(55, 37, '固定结温的理想定性输出特性（未含串联电阻与沟道长度调制）', 24)]
    x0, y0, sx, sy = 120, 625, 160, 59
    c += [path(f'M{x0} 85 L{x0} {y0} L1115 {y0}', width=2.7),
          path(f'M{x0} {y0} L{x0} 80', width=2.7, extra='marker-end="url(#arrow)"'),
          path(f'M{x0} {y0} L1120 {y0}', width=2.7, extra='marker-end="url(#arrow)"'),
          text(66, 80, 'I_D', 26), text(1128, 660, 'V_DS', 26), text(100, 653, '0', 22)]
    overdrives = range(1, 5)
    voltage_samples = {i/240*5.8 for i in range(241)}
    for k in overdrives:
        points = []
        for v in sorted(voltage_samples | {k}):
            j = k*v-v*v/2 if v < k else k*k/2
            points.append(f'{x0+sx*v:.3f},{y0-sy*j:.3f}')
        c.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#17202b" stroke-width="2.8"/>')
        c.append(text(1065, y0-sy*k*k/2+4, f'V_GS{k}', 23))
    boundary_voltages = sorted({4.2*i/160 for i in range(161)} | set(overdrives))
    points = ' '.join(f'{x0+sx*v:.3f},{y0-sy*v*v/2:.3f}' for v in boundary_voltages)
    c.append(f'<polyline points="{points}" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="8 6"/>')
    c += [text(290, 110, '线性区（非饱和区）', 22, 'middle'), text(290, 141, '原点附近近似线性', 21, 'middle'),
          text(940, 80, '饱和区：沟道夹断后近似恒流', 22, 'middle'),
          text(790, 425, '虚线连接各曲线夹断点', 21), path('M785 430 L590 370', width=1.3),
          text(640, 702, 'V_GS4 > V_GS3 > V_GS2 > V_GS1 > V_th > 0', 25, 'middle'),
          text(640, 744, '曲线由同一平方律模型生成；坐标无实测刻度，不能用来读出某只 1200 V 器件的电流。', 20, 'middle')]
    return wrap(''.join(c), '图2 四条栅压下的 MOSFET 输出特性与抛物线夹断边界', height=775)

figures = {'structure':device(), 'zoom':zoom(), 'output':output_curves(), 'blocking':device('blocking'), 'current':device('current')}
for name, svg in figures.items():
    (ASSETS/f'{name}.svg').write_text(svg, encoding='utf-8')

source = (HERE/'answer-source.html').read_text(encoding='utf-8')
figure_refs = dict(zip(figures, ['图1(a)', '图1(b)', '图2', '图3', '图4']))
reference_ids = {label: f'fig-{name}' for name, label in figure_refs.items()}
reference_ids.update({f'式({n})': f'eq-{n}' for n in range(1, 7)})
reference_pattern = re.compile('|'.join(re.escape(label) + r'(?![.\d])' for label in reference_ids))

def link_references(content):
    def link(match):
        label = match.group()
        return f'<a class="jump-reference" href="#{reference_ids[label]}">{label}</a>'
    return reference_pattern.sub(link, content)

source = re.sub(r'(<p(?: [^>]*)?>)(.*?)(</p>)',
                lambda match: match[1] + link_references(match[2]) + match[3], source, flags=re.S)
for name, svg in figures.items():
    label = figure_refs[name]
    target = f'fig-{name}'
    source = source.replace(
        f'<figure>{{{{{name}}}}}<figcaption>{label}',
        f'<figure id="{target}" class="reference-target" tabindex="-1">'
        f'<div class="figure-view" tabindex="0" aria-label="{label}，横向滚动查看">{svg}</div>'
        f'<figcaption><a class="reference-mark" href="#{target}">{label}</a>',
    )
source = re.sub(r'(<figcaption><a[^>]*>[^<]*</a>)(.*?)(</figcaption>)',
                lambda match: match[1] + link_references(match[2]) + match[3], source, flags=re.S)
source = source.replace('<div class="equation" id=', '<div class="equation reference-target" tabindex="-1" id=')
pattern = re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', re.S)
matches = list(pattern.finditer(source))
jobs = [{'tex':m.group(1) if m.group(1) is not None else m.group(2), 'display':m.group(1) is not None} for m in matches]
proc = subprocess.run(['node', str(ROOT/'scripts/render-math.cjs')], input=json.dumps(jobs), text=True, encoding='utf-8', capture_output=True, check=True, cwd=ROOT)
rendered = iter(json.loads(proc.stdout))
source = pattern.sub(lambda m: next(rendered), source)
(HERE/'答案.html').write_text(source, encoding='utf-8')
print(f'Built 5 original SVGs and HTML; rendered {len(jobs)} math expressions.')
