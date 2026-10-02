#!/usr/bin/env bash
# Build rotor-site into dist/ (deploy-ready static files).
#
# Usage:
#   ./build.sh
#
# What it does:
#   1. Runs writing/gen.py -> generates article pages, list page, /tmp/articles.js
#   2. Injects /tmp/articles.js into a copy of index.html
#   3. Assembles dist/ with only the files needed for deployment
#
# Then deploy dist/ to Cloudflare Pages, Netlify, or any static host.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST="$ROOT/dist"

echo "==> [1/3] generating pages"
(cd "$ROOT/writing" && python3 gen.py > /dev/null)
echo "    articles.js: $(python3 -c "print(len(open('/tmp/articles.js').read()))") bytes"

echo "==> [2/3] assembling dist/"
rm -rf "$DIST"
mkdir -p "$DIST/writing"
python3 - "$ROOT" "$DIST" <<'EOF'
import re, sys, shutil, os
root, dist = sys.argv[1], sys.argv[2]
s = open(os.path.join(root, "index.html"), encoding="utf-8").read()
new = open("/tmp/articles.js", encoding="utf-8").read().strip()
s2, n = re.subn(r'const ARTICLES = \[.*?\]', lambda m: new, s, count=1, flags=re.S)
assert n == 1, "ARTICLES block not found in index.html"
open(os.path.join(dist, "index.html"), "w", encoding="utf-8").write(s2)
shutil.copy(os.path.join(root, "og.png"), dist)
w = os.path.join(root, "writing")
for fn in sorted(os.listdir(w)):
    if fn == "index.html" or (fn[:1].isdigit() and fn.endswith(".html")):
        shutil.copy(os.path.join(w, fn), os.path.join(dist, "writing", fn))
EOF

echo "==> [3/3] done"
echo "    dist/ is ready. Deploy it, e.g.:"
echo "      npx wrangler pages deploy dist --project-name=rotor-site"
find "$DIST" -type f | sort
