'use strict';
// Keep the reviewed release sequence within the deployment command length limit.
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const cwd = path.resolve(__dirname, '..');
for (const [program, args] of [
  ['node', ['scripts/buyer-intent-release.cjs', '.']],
  ['node', ['scripts/consolidate-stories.cjs']],
  ['python3', ['scripts/format-directory.py']],
  ['node', ['scripts/paginate-directory.cjs']],
  ['python3', ['scripts/apply-alert-expiry.py']],
  ['python3', ['scripts/normalize-news-links.py']],
  ['node', ['scripts/practical-homepage.cjs', '.']],
  ['python3', ['service_buying_guides.py']],
  ['python3', ['scripts/connect-visit-guides.py']],
]) execFileSync(program, args, {cwd, stdio:'inherit'});
