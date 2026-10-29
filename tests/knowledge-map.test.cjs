'use strict';
// Validate course graph data against the actual reading material before publishing.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const context = vm.createContext({ window: {} });
for (const file of ['courses/electrical-machines/manifest.js', 'courses/electrical-machines/knowledge-map.js', 'courses/highschool/courses.js', 'courses.js']) {
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

// Regression: dragging on a linked node must pan the view, never edit node coordinates.
let MapElement;
const navigation = { hash: '#course/electrical-machines/map' };
const uiContext = vm.createContext({
  HTMLElement: class {},
  customElements: { define: (_name, element) => { MapElement = element; } },
  location: navigation
});
vm.runInContext(fs.readFileSync(path.join(root, 'knowledge-map.js'), 'utf8'), uiContext);
const viewer = new MapElement();
const point = { id: 'magnetic-sec11', x: 48, y: 222 };
const captures = new Set();
viewer._course = { id: 'electrical-machines' };
viewer.byNode = new Map([[point.id, point]]);
viewer.pointers = new Map();
viewer.view = { x: 10, y: 20, k: 1 };
viewer.canvas = {
  setPointerCapture: id => captures.add(id),
  hasPointerCapture: id => captures.has(id),
  releasePointerCapture: id => captures.delete(id),
  classList: { add() {}, remove() {} },
  getBoundingClientRect: () => ({ left: 0, top: 0 })
};
viewer.transform = () => {};
viewer.highlight = () => {};
const event = (pointerId, x, y, node = true) => ({
  button: 0, pointerId, clientX: x, clientY: y,
  target: { closest: () => node ? { dataset: { node: point.id } } : null }
});
viewer.pointerDown(event(1, 100, 100));
viewer.pointerMove(event(1, 175, 140));
viewer.pointerEnd(event(1, 175, 140));
assert.equal(point.x, 48, 'Dragging edited a node x coordinate');
assert.equal(point.y, 222, 'Dragging edited a node y coordinate');
assert.equal(viewer.view.x, 85, 'Dragging on a node must pan the entire graph');
assert.equal(viewer.view.y, 60);
assert.equal(navigation.hash, '#course/electrical-machines/map', 'Dragging activated a link');
viewer.pointerDown(event(2, 100, 100));
viewer.pointerDown(event(3, 160, 100));
viewer.pointerMove(event(3, 220, 100));
viewer.pointerEnd(event(2, 100, 100));
viewer.pointerEnd(event(3, 220, 100));
assert(viewer.view.k > 1, 'Pinch zoom stopped working');
assert.equal(point.x, 48);
assert.equal(point.y, 222);
assert.equal(navigation.hash, '#course/electrical-machines/map', 'Pinch activated a link');
viewer.pointerDown(event(4, 100, 100));
viewer.pointerEnd(event(4, 100, 100));
assert.equal(navigation.hash, 'course/electrical-machines/magnetic-sec11', 'A tap must still open the lesson');
console.log('Fixed node coordinates, whole-map drag, pinch zoom and tap navigation verified.');
