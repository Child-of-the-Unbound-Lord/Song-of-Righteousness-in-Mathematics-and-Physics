'use strict';
// Render mathematical notation during the build, not in visitors' browsers.
const fs = require('fs');
const katex = require('katex');
const items = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = items.map((item) => {
  try {
    return katex.renderToString(item.tex, {
      displayMode: !!item.display,
      output: 'htmlAndMathml',
      throwOnError: true,
      trust: false,
      strict: 'warn',
      maxExpand: 1000,
      maxSize: 50,
    });
  } catch (error) {
    throw new Error(`KaTeX cannot render ${JSON.stringify(item.tex)}: ${error.message}`);
  }
});
process.stdout.write(JSON.stringify(result));
