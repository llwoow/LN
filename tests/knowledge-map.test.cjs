'use strict';
// Validate course graph data against the actual reading material before publishing.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const context = vm.createContext({ window: {} });
for (const file of ['courses/electrical-machines/manifest.js', 'courses/electrical-machines/knowledge-map.js', 'courses.js']) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
}
for (const course of context.window.LN_COURSES) {
  assert(course.sections?.length, `${course.id} must have real material`);
  const sections = new Map(course.sections.map(section => [section.id, section]));
  for (const section of sections.values()) assert(fs.existsSync(path.join(root, section.src)), `Missing lesson: ${section.id}`);
  const nodes = course.knowledgeMap?.nodes || [];
  const ids = new Set();
  for (const node of nodes) {
    assert(sections.has(node.section), `Node links to missing section: ${node.section}`);
    assert(!ids.has(node.section), `Duplicate map node: ${node.section}`);
    ids.add(node.section);
    assert(node.title && node.note, `Map node needs a useful label: ${node.section}`);
  }
  const links = new Set();
  for (const edge of course.knowledgeMap?.links || []) {
    assert(ids.has(edge.from) && ids.has(edge.to), `Knowledge relation has a missing endpoint: ${edge.from} -> ${edge.to}`);
    assert.notEqual(edge.from, edge.to);
    assert(edge.label && edge.description, 'Knowledge relations must explain what connects the concepts');
    const key = edge.from + '->' + edge.to;
    assert(!links.has(key), `Duplicate knowledge relation: ${key}`);
    links.add(key);
  }
}
console.log('Course materials, graph destinations and explained knowledge relations verified.');
