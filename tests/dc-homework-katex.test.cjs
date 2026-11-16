'use strict';
const fs = require('node:fs');
const assert = require('node:assert/strict');
const katex = require('../scripts/vendor/katex.cjs');

const source = fs.readFileSync('courses/electrical-machines/lessons/dc-homework-review.js', 'utf8');
const marker = 'window.LN_LESSONS["electrical-machines/dc-homework-review"]=';
const payload = JSON.parse(source.slice(source.indexOf(marker) + marker.length).trim().replace(/;$/, ''));
const expressions = [...payload.html.matchAll(/data-dc-tex="([^"]+)"/g)].map(match =>
  match[1].replaceAll('&amp;', '&').replaceAll('&quot;', '"')
);
assert(expressions.length >= 150, 'Expected all calculation and inline KaTeX expressions');
let failures = 0;
for (const [index, expression] of expressions.entries()) {
  try {
    const rendered = katex.renderToString(expression, {
      throwOnError: true, strict: 'error', trust: false,
      output: 'htmlAndMathml'
    });
    assert(rendered.includes('katex-mathml'), 'MathML not emitted');
    assert(!rendered.includes('katex-error'), 'KaTeX rendered error');
  } catch (error) {
    failures++;
    console.error('KaTeX expression #' + (index + 1) + ': ' + expression);
    console.error(String(error));
  }
}
assert.equal(failures, 0, failures + ' invalid KaTeX expressions');
console.log('Verified ' + expressions.length + ' KaTeX expressions.');
