#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const configPath = path.join(root, 'docs/codex-migration/ai-substrate/typed-context-config.json');
const indexPath = path.join(root, 'docs/codex-migration/ai-substrate/typed-context-index.json');

const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));

function resolveSafePath(relativePath) {
  const candidate = path.resolve(root, String(relativePath || ''));
  if (candidate !== root && !candidate.startsWith(root + path.sep)) {
    throw new Error(`Unsafe context path outside repo root: ${relativePath}`);
  }
  return candidate;
}

const missing = configData.filter((entry) => !fs.existsSync(resolveSafePath(entry.path)));
if (missing.length) {
  console.error('Missing context files:', missing.map((entry) => entry.path).join(', '));
  process.exit(1);
}

const payload = {
  generated_at: new Date().toISOString(),
  entries: configData.map((entry) => ({
    ...entry,
    resolved: path.relative(root, resolveSafePath(entry.path))
  }))
};

fs.writeFileSync(indexPath, JSON.stringify(payload, null, 2) + '\n');
console.log('Updated typed-context-index.json with', payload.entries.length, 'files.');
