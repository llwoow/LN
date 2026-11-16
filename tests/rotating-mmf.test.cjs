'use strict';
// Deterministic mathematical regression tests; browser interaction needs separate visual review.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { calculate, mount } = require('../courses/electrical-machines/model/rotating-mmf-lab.js');
const close = (actual, expected, label) =>
  assert.ok(Math.abs(actual - expected) < 1e-10, label + ': got ' + actual + ', expected ' + expected);
assert.equal(typeof mount, 'function');
const twoPi = 2 * Math.PI;
for (let i = 0; i <= 24; i++) {
  const phase = twoPi * i / 24;
  const current = calculate(phase, 0).currents;
  close(current.reduce((a, b) => a + b, 0), 0, 'balanced three-phase current');
  for (let j = -24; j <= 48; j++) {
    const theta = twoPi * j / 24;
    const mmf = calculate(phase, theta);
    close(mmf.perPhase.reduce((a, b) => a + b, 0), mmf.total, 'three-phase summation');
    close(mmf.total, 1.5 * Math.cos(theta - phase), 'rotating MMF');
    close(mmf.forward, mmf.total, 'forward rotating wave');
    close(mmf.backward, 0, 'cancelled backward waves');
  }
  close(calculate(phase, phase).total, 1.5, 'constant peak');
  close(calculate(phase, phase + Math.PI).total, -1.5, 'opposite pole');
}
const zero = calculate(0, 0);
close(zero.currents[0], 1, 'phase A current at t=0');
close(zero.currents[1], -.5, 'phase B current at t=0');
close(zero.currents[2], -.5, 'phase C current at t=0');
close(zero.perPhase[0], 1, 'phase A contribution at A axis');
close(zero.perPhase[1], .25, 'phase B contribution at A axis');
close(zero.perPhase[2], .25, 'phase C contribution at A axis');
// The chapter route, UI mount and extended angle presets remain discoverable.
const base = path.resolve(__dirname, '..');
const manifest = fs.readFileSync(path.join(base, 'courses/electrical-machines/manifest.js'), 'utf8');
const lesson = fs.readFileSync(path.join(base, 'courses/electrical-machines/lessons/mmf-sec47.js'), 'utf8');
const script = fs.readFileSync(path.join(base, 'courses/electrical-machines/model/rotating-mmf-lab.js'), 'utf8');
const app = fs.readFileSync(path.join(base, 'app.js'), 'utf8');
assert.match(manifest, /"id":"mmf-sec47"/);
assert.match(lesson, /data-mmf-lab/);
assert.match(lesson, /三相合成基波磁动势/);
assert.match(script, /value="1080" selected/);
assert.match(script, /\[-360, 720\]/);
assert.match(app, /LN_RotatingMMFLab\?\.mount\(body\)/);
console.log('rotating MMF: 25 phases × 73 space angles, amplitude / direction / 3-phase balance / integration checks passed');
