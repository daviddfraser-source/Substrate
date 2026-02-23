#!/bin/bash
set -euo pipefail

npm install
npm run lint
npm run typecheck
npm run test
npx prisma generate
npm run schema:push
