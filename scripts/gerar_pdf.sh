#!/usr/bin/env bash
# Gera docs/relatorio/relatorio.pdf a partir de docs/relatorio/relatorio.md:
# Markdown -> HTML (biblioteca Python markdown) -> PDF (Chrome headless).
# Caminhos de imagem no Markdown são relativos a docs/relatorio/.
set -euo pipefail

raiz="$(cd "$(dirname "$0")/.." && pwd)"
dir="$raiz/docs/relatorio"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
python="${PYTHON:-python3}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

{
  cat <<EOF
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<base href="file://$dir/">
<title>Akona Energy · Deploy Blindado</title>
<style>
  body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #1a1a1a; }
  h1 { font-size: 22pt; } h2 { font-size: 15pt; margin-top: 1.6em; }
  table { border-collapse: collapse; margin: 0.8em 0; }
  th, td { border: 1px solid #bbb; padding: 4px 8px; text-align: left; vertical-align: top; }
  code { font-size: 0.92em; background: #f2f2f2; padding: 0 3px; }
  pre { background: #f2f2f2; padding: 8px; white-space: pre-wrap; }
  img { max-width: 100%; }
  a { color: #0b57d0; }
  @page { size: A4; margin: 18mm; }
</style>
</head>
<body>
EOF
  "$python" -m markdown -x tables -x fenced_code "$dir/relatorio.md"
  printf '\n</body>\n</html>\n'
} > "$tmp/relatorio.html"

"$chrome" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$dir/relatorio.pdf" "file://$tmp/relatorio.html"

echo "PDF gerado em $dir/relatorio.pdf"
