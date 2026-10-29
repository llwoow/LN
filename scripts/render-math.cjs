'use strict';
const katex = require('./vendor/katex.cjs');
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  const expressions = JSON.parse(input);
  const output = expressions.map(({tex, display}) => katex.renderToString(tex, {
    displayMode: display, throwOnError: true, strict: 'error', trust: false, output: 'htmlAndMathml'
  }));
  process.stdout.write(JSON.stringify(output));
});
