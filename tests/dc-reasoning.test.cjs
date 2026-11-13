const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const lab = require('../courses/electrical-machines/model/dc-learning-lab.js');

function near(actual, expected, tol = 1e-9) {
  assert.ok(Math.abs(actual - expected) < tol, `${actual} != ${expected}`);
}
for (const poles of [2, 4, 6, 8]) {
  for (const winding of ['lap', 'wave']) {
    const s = lab.calculate({ poles, winding, armatureCurrent: 40 });
    const expectedA = winding === 'lap' ? poles : 2;
    assert.equal(s.branches, expectedA);
    assert.equal(s.pairs * 2, s.branches);
    near(s.branchCurrent * s.branches, s.armatureCurrent);
    near(s.seriesConductors * s.branches, s.conductors);
    near(s.ce * s.flux * s.rpm, s.emf);
    near(s.ct * s.flux * s.armatureCurrent, s.torque);
    near(s.torque * (2 * Math.PI * s.rpm / 60), s.power, 1e-7);
  }
}
const lap = lab.calculate({ poles: 4, winding: 'lap', armatureCurrent: 40 });
const wave = lab.calculate({ poles: 4, winding: 'wave', armatureCurrent: 20 });
assert.equal(lap.branches, 4);
assert.equal(wave.branches, 2);
near(lap.emf, 240); near(wave.emf, 480);
near(lap.power, wave.power);
near(lap.branchCurrent, wave.branchCurrent);
assert.throws(() => lab.calculate({ poles: 3, winding: 'lap', armatureCurrent: 40 }), RangeError);
assert.throws(() => lab.calculate({ poles: 4, winding: 'duplex', armatureCurrent: 40 }), RangeError);
assert.throws(() => lab.calculate({ poles: 4, winding: 'lap', armatureCurrent: -1 }), RangeError);
for (const [id, correct, wrong] of [['wave6','b','a'],['lap4','c','b'],['generator','a','b'],['brushes','b','a'],['compare','c','a']]) {
  assert.equal(lab.check(id, correct).correct, true);
  assert.equal(lab.check(id, wrong).correct, false);
  assert.ok(lab.check(id, correct).explanation.length > 15);
}
assert.throws(() => lab.check('missing', 'a'), RangeError);

// The new lesson content must remain attached to real chapter sections.
global.window = { LN_LESSONS: {} };
const expected = [
  ['dc-sec32', 'dc-branch-reasoning'],
  ['dc-worked', 'dc-example-313-review'],
  ['dc-answers', 'dc-concept-diagnostics'],
  ['dc-quickref', 'dc-formula-thinking']
];
for (const [section, anchor] of expected) {
  const file = path.join(__dirname, '..', 'courses', 'electrical-machines', 'lessons', section + '.js');
  require(file);
  const entry = global.window.LN_LESSONS['electrical-machines/' + section];
  assert.ok(entry && entry.html.includes('id="' + anchor + '"'));
  assert.ok(entry.html.includes('</section>'));
}
const app = fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8');
assert.ok(app.includes("window.LN_DCMachinesLabs?.mount(body)"));
console.log('DC reasoning: winding comparisons, power identity, diagnostics and lesson integration passed.');
