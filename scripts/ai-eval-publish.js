const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const report = path.join(root, 'reports/ai-substrate-eval.json');
const historyDir = path.join(root, 'docs/codex-migration/ai-substrate/eval-history');
if (!fs.existsSync(historyDir)) {
  fs.mkdirSync(historyDir, { recursive: true });
}

const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const dest = path.join(historyDir, `${timestamp}-ai-substrate-eval.json`);
fs.copyFileSync(report, dest);
fs.writeFileSync(path.join(historyDir, 'LATEST.json'), JSON.stringify({ timestamp: new Date().toISOString(), file: path.basename(dest) }, null, 2));
console.log('Published evaluation report to', dest);
