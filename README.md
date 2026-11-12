# plecs-ai：PLECSモデルをAIに編集・実行させる道具と知見

PLECS Standalone のモデル（`.plecs`）を、Claude CodeなどのAIエージェントに編集させ、シミュレーションを実行させ、結果の数値と回路図の画像を見ながら反復させるためのリポジトリです。

AIにできること：

- モデルを読み込んで実行し、波形の数値から評価値（整定時間、ピーク、エネルギーなど）を計算する。
- 変数を変えて繰り返し実行する（ゲインの調整など）。
- ブロックや配線を追加・変更した新しいモデルファイルを作る。
- カタログの部品だけで、新しいモデルを一から作る（例：`examples/pmsm_foc`）。
- 回路図を画像で確認し、配置を直したり、枠線と説明文を付けたりする。

## 必要なもの

- Windows上の PLECS Standalone 5.0（他の版は未確認）
- Python 3.9以上（追加のライブラリは不要）
- Claude Code（他のエージェントでも、`.claude/skills/plecs/` の文書を読ませれば使えます）

## 準備

1. このリポジトリを取得し、直下で次を実行します。

   ```
   pip install -e .
   ```

2. PLECSを起動し、PreferencesでRPCインターフェースを有効にします（既定では無効です）。ポートは1080のままにします。変えた場合は、環境変数 `PLECS_RPC_URL` に `http://localhost:ポート番号` を設定します。
3. 動作を確かめます。PLECSが起動した状態で次を実行し、`results/balancer_v6.png` に回路図が出力されれば準備完了です。

   ```
   cd examples/balancer
   python -m plecs_ai.snapshot balancer_v6
   ```

## 使い方

このリポジトリのフォルダでClaude Codeを起動すると、`plecs` というskillが自動で使えるようになります。あとは普通に頼むだけです。

> `examples/balancer/balancer_v6.plecs` の負荷を5 Aから15 Aのステップにして、Ibatの偏差が1 A以内に戻るまでの時間を調べて。

> このモデルのACRの出力にリミッタを入れて、新しいファイルとして保存して。回路図の見た目も確認して。

頼むときのコツ：

- **評価したい量を数値で言えるようにする。**「良くして」ではなく、「ピークを15 A以下に」「1 A以内に戻る時間」のように伝えます。
- **見たい信号をトップレベルの Signal Outport につなぐ。** AIが数値を受け取れるのは出力ポートの信号だけです。AIに追加させることもできます。
- **PLECS上の変更は保存してから頼む。** AIはモデルを読み込み直すときに、保存していない変更を破棄します。
- **AIは元のファイルを上書きしません。** 編集結果は別名（`_v2` など）で保存されます。

自分の研究用のフォルダで使いたいときは、`pip install -e .` を済ませたうえで、`.claude/skills/plecs` フォルダを自分のリポジトリの `.claude/skills/` か、ホームの `~/.claude/skills/` にコピーします。コピーしたものは更新が自動では反映されないので、知見の追記はこのリポジトリ側で行ってください。

## フォルダの構成

| 場所 | 内容 |
|---|---|
| `.claude/skills/plecs/SKILL.md` | AI向けの手順書。作業の流れ、編集の規則、間違えやすい点 |
| `.claude/skills/plecs/reference/` | 知見の本体。`file-format.md`（ファイル書式）、`blocks.md`（ブロックの端子とパラメータ）、`rpc.md`（RPCの使い方と癖） |
| `plecs_ai/` | Pythonの道具。`edit`（編集）、`check`（検査）、`rpc`（実行）、`snapshot`（回路図の画像）、`harvest`（ブロックの取り込み） |
| `plecs_ai/blocks/` | ブロックのカタログ。PLECSが保存した記述そのもの |
| `samples/` | カタログの取り込み元にした見本モデル |
| `tests/block_tests.py` | カタログのブロックをPLECSで動かして、端子とパラメータを確かめる試験 |
| `examples/pmsm_foc/` | 一から生成したPMSMのベクトル制御モデル。生成、評価、波形の描画のスクリプト |
| `examples/balancer/` | 最初の実験の一式（スーパーキャパシタ用双方向DC-DC）。編集スクリプト、試験スクリプト、結果の報告 |

人が読むなら、まず `examples/balancer/REPORT.md`（何ができたか）、次に `reference/` の3つ（何が分かっているか）がお勧めです。

## 使えるブロックを増やす

AIは、PLECSが実際に保存した記述があるブロックしか追加しません。書式を推測して書くと、読み込みに失敗したときの切り分けに時間がかかるからです。カタログに無いブロックは次のように増やします。

1. PLECSで新しいモデルを作り、欲しいブロックを置いて、入出力を何かにつなぎます。
2. `samples/` に保存します（例：`samples/saturation.plecs`）。
3. 次を実行します。

   ```
   python -m plecs_ai.harvest samples/saturation.plecs
   ```

4. `tests/block_tests.py` に試験を足し、PLECSで通ることを確かめてから、`.claude/skills/plecs/reference/blocks.md` の表に端子番号とパラメータの意味を1行足します。この作業はAIに頼めます（「samplesに置いたブロックをカタログに取り込んで、試験して、blocks.mdに追記して」）。
5. 見本、`plecs_ai/blocks/` の変更、試験、`blocks.md` をまとめてコミットします。

`harvest` にはフォルダも渡せます。PLECS付属のデモ（`Documents/Plexim/PLECS 5.0 (64 bit)/demos`）から取り込んだ結果、現在のカタログは195種類です。一覧は `plecs_ai/blocks/INDEX.md`（自動生成）にあります。

カタログに入っただけでは、端子が入力か出力かまでしか分かりません。端子の意味とパラメータの番号は、`tests/block_tests.py` でPLECSに実際に動かさせて確かめ、`blocks.md` に書きます。現在、49種類が確認済みです。

## 知見を増やす

AIとの作業で新しく分かったことは、その場でAIに `reference/` へ追記させてください（skillにそう指示してあります）。人が気づいたことも同じ場所に書きます。

| 分かったこと | 書く場所 |
|---|---|
| ブロックの端子番号、パラメータの番号の意味 | `reference/blocks.md` |
| ファイルの書式 | `reference/file-format.md` |
| RPCのコマンド、挙動の癖 | `reference/rpc.md` |
| AIが繰り返し間違えたこと | `SKILL.md` の「特に間違えやすい点」 |
| 何度も書いた処理 | `plecs_ai/` の関数 |

書くときの決まり：

- PLECSで読み込んで動いたことは「確認済み」、そうでないことは「推定」と書き分けます。
- 自分のモデルでの作業記録は `examples/<題材>/` に置きます。編集スクリプト（`make_*.py`）と試験スクリプト（`run_*.py`）を残すと、他の人が同じ手順をたどれます。
- 変更はブランチを切ってプルリクエストにします。`reference/` と `plecs_ai/` は全員のAIの動作に影響するので、他の人に見てもらってから取り込みます。

## 今後の予定（未確認の機能）

ここまでに確かめたのは、時間領域の過渡解析（`plecs.simulate`）だけです。次のものは、AIから扱えるかをまだ確かめていません。

- **熱モデルを使った損失解析**：半導体の熱記述（`thermal` パラメータ）、ヒートシンク（`HeatSink`）、熱抵抗（`ThermalResistor`）などの部品と、導通損失・スイッチング損失の取り出し方。部品はデモからカタログに取り込み済みですが、試験はしていません。
- **過渡解析以外の解析**：定常解析（`SteadyStateAnalysis`）、ACスイープ（`ACSweep`）、周波数応答解析（`FrequencyResponseAnalysis`）など。RPCの `plecs.analyze` で実行できるはずですが、使い方と結果の受け取り方は未確認です。

確かめたら、分かったことを `.claude/skills/plecs/reference/` に追記し、この節から消してください。

## 注意

- `.plecs` は改行がCRLFのASCIIファイルです。gitが改行を変換しないように `.gitattributes` で設定してあります。エディタで開いて保存するときも、改行コードを変えないでください。
- `results/` は波形と画像の出力先で、gitの管理から外してあります。
- 回路図の画像の取得には、マニュアルに載っていないRPCコマンドを使っています。PLECSの版が変わると使えなくなる可能性があります。
