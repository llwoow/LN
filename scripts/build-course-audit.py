"""Build an evidence-limited inventory of existing LN course files.

A manifest entry or a successful parse proves neither scholarly accuracy nor
interactive operation. Never infer 'verified' from content presence or reports.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ("automatic-control", "自动控制原理", None),
    ("electromagnetic-compatibility", "电磁兼容原理及应用", None),
    ("electrical-machines", "电机学：变压器与直流电机", ("第2章", "第3章")),
)
CHECKS = ("知识结构", "推导", "例题", "习题/测试入口", "图示", "交互组件", "知识链接/参考")


def assignment(source: str):
    match = re.search(r"window\.[A-Z_][A-Z_0-9]*(?:\[[^\]]+\])?\s*=\s*", source)
    if not match:
        raise ValueError("No LN JSON assignment")
    return json.JSONDecoder().raw_decode(source[match.end():])[0]


class HeadingReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active = None
        self.parts = []
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if self.active:
            self.depth += 1
            return
        attrs = dict(attrs)
        if tag in ("h3", "h4") and attrs.get("id"):
            self.active = (tag, attrs["id"])
            self.parts = []
            self.depth = 1

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if not self.active:
            return
        self.depth -= 1
        if self.depth == 0:
            heading = " ".join("".join(self.parts).split())
            if heading:
                self.headings.append({"id": self.active[1], "title": heading[:160]})
            self.active = None
            self.parts = []


def git_revision(root: Path):
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root,
            stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "未取得"


def inspect_section(root: Path, course_id: str, section: dict):
    kind = section.get("kind", "unknown")
    src = section.get("src") or ""
    path = root / src if src else None
    exists = bool(path and path.is_file())
    if kind == "outline":
        state = "骨架状态"
        reason = "课程清单明确标记为 outline；未找到该条目登记的独立正文入口"
    elif exists:
        state = "部分接入"
        reason = "正文/模型脚本存在；未据此核实学术准确性、完整性或浏览器行为"
    elif src:
        state = "明确存在的问题"
        reason = "manifest 指向的源文件不存在"
    else:
        state = "骨架状态"
        reason = "未登记可读取的正文脚本；是否存在其他内容需单独定位"
    headings = []
    signals = {"公式标记": 0, "图示标记": 0, "控件标记": 0, "章节链接标记": 0}
    if exists and path.suffix == ".js":
        script = path.read_text(encoding="utf-8", errors="replace")
        try:
            item = assignment(script)
            html = item.get("html", "") if isinstance(item, dict) else ""
        except (ValueError, TypeError, json.JSONDecodeError):
            html = ""
        if html:
            reader = HeadingReader()
            reader.feed(html)
            headings = reader.headings
            signals = {
                "公式标记": len(re.findall(r'<(?:math\b|mjx-container\b)|class=["\x27][^"\x27]*math-display', html, re.I)),
                "图示标记": len(re.findall(r'<(?:figure|svg)\b', html, re.I)),
                "控件标记": len(re.findall(r'<(?:button|input|select|canvas)\b', html, re.I)),
                "章节链接标记": len(re.findall(r'href=["\x27]#course/', html, re.I)),
            }
    return {
        "id": section["id"],
        "title": section.get("title", section["id"]),
        "group": section.get("group", "未分章"),
        "courseId": course_id,
        "kind": kind,
        "sourcePath": src,
        "sourceExists": exists,
        "status": state,
        "statusReason": reason,
        "evidenceClass": "仓库实际内容",
        "sourceSizeBytes": path.stat().st_size if exists else 0,
        "subsections": headings,
        "signals": signals,
        "checks": list(CHECKS),
        "entryHash": "#course/" + course_id + "/" + section["id"],
    }


def make_inventory(root: Path = ROOT):
    courses = []
    rows = []
    for course_id, label, chapter_prefixes in TARGETS:
        manifest_path = "courses/" + course_id + "/manifest.js"
        manifest = assignment((root / manifest_path).read_text(encoding="utf-8"))
        picked = [
            section for section in manifest["sections"]
            if not chapter_prefixes or section.get("group", "").startswith(chapter_prefixes)
        ]
        courses.append({"id": course_id, "label": label, "manifest": manifest_path,
                        "sections": len(picked)})
        rows.extend(inspect_section(root, course_id, item) for item in picked)
    return {
        "schemaVersion": 1,
        "sourceRevision": git_revision(root),
        "basis": "源码清单及已存在文件的静态检测；非内容/教学/浏览器验收",
        "courses": courses,
        "sections": rows,
        "rule": "文件存在最多归类部分接入；已验证必须提供人工确认的独立证据",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="audit/inventory.json")
    args = parser.parse_args()
    dest = Path(args.output)
    if not dest.is_absolute():
        dest = ROOT / dest
    data = make_inventory()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {}
    for row in data["sections"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print("Course audit inventory:", len(data["sections"]), "sections", counts)
    print("This is a source inventory only, not a content verification.")


if __name__ == "__main__":
    main()
