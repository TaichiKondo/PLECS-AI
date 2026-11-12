# 見本モデル

ブロックのカタログ（`plecs_ai/blocks/`）に取り込むための見本を置く場所です。PLECS上でブロックを置いて保存したファイルを、手を加えずに入れてください。

```
python -m plecs_ai.harvest samples/<ファイル名>.plecs
```

手順の詳細は `.claude/skills/plecs/reference/blocks.md` の「ブロックを増やす手順」にあります。

現在のカタログは、次の順に取り込みました（先に取り込んだものが優先されます）。

1. `examples/balancer/balancer_apr.plecs`（23種類）
2. `parts_sample.plecs`（11種類）
3. PLECS 5.0 付属の `demos` フォルダの92ファイル（161種類）
