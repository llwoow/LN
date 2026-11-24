"""Cross-course knowledge: source passages, routes, and semantic data invariants."""
from pathlib import Path
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[1]
REF=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
ASSIGN=REF['assignment']
DOC=REF['Document']

class CrossKnowledge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=ASSIGN(ROOT/'courses/cross-knowledge-data.js')
        cls.nodes={n['id']:n for n in cls.data['nodes']}
        cls.courses={c['id']:c for c in (ASSIGN(p) for p in (ROOT/'courses').glob('*/manifest.js'))}

    def test_nodes_resolve_to_unique_actual_paragraphs(self):
        self.assertEqual(len(self.nodes),len(self.data['nodes']))
        topics={t['id'] for t in self.data['topics']}
        for n in self.nodes.values():
            self.assertIn(n['topic'],topics)
            sections={s['id']:s for s in self.courses[n['course']]['sections']}
            section=sections[n['section']]
            self.assertEqual(section['kind'],'html')
            html=ASSIGN(ROOT/section['src'])['html']
            paragraphs=[p for p in DOC(html).root.walk() if p.tag=='p']
            # Read raw text, including MathML annotations where present, as in DOM textContent.
            def raw(p):
                return ''.join(raw(c) if hasattr(c,'children') else c for c in p.children)
            self.assertEqual(sum(n['match'] in raw(p) for p in paragraphs),1,n['id'])
            self.assertNotIn('id="cross-'+n['id']+'"',html)

    def test_edges_and_pending(self):
        seen=set(); connected=set()
        for e in self.data['links']:
            a,b=e['from'],e['to']
            self.assertIn(a,self.nodes);self.assertIn(b,self.nodes)
            self.assertNotEqual(a,b)
            key=frozenset((a,b))
            self.assertNotIn(key,seen);seen.add(key)
            self.assertEqual(self.nodes[a]['topic'],self.nodes[b]['topic'])
            self.assertTrue(e['label'] and e['description'])
            connected.update((a,b))
        self.assertEqual(connected,set(self.nodes))
        for p in self.data['pending']:
            self.assertTrue(p['description'])
            self.assertTrue(set(p['nodes'])<=set(self.nodes))
        self.assertNotIn('electromagnetic-field',self.courses)

if __name__=='__main__':unittest.main()
