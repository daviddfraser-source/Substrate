const fs = require("fs");
const path = require("path");

const file = path.join(__dirname, "../templates/ai-substrate/lib/auth/policy.ts");
const content = fs.readFileSync(file, "utf8");

if (!content.includes("defineAbilities")) {
  console.error("defineAbilities missing in policy.ts");
  process.exit(1);
}

console.log("policy contract looks good");
