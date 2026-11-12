---
name: plecs
description: PLECS Standalone のモデル（.plecs）をAIが編集し、RPCでシミュレーションを実行し、波形の数値と回路図の画像を見て反復する。PLECSモデルの編集、ブロックや配線の追加、パラメータ調整、シミュレーション結果の評価、回路図の見た目の確認や注釈の追加を頼まれたときに使う。Use for editing or simulating PLECS models.
---

# PLECSモデルの編集と実行

`.plecs` はテキストファイルである。これをスクリプトで編集し、PLECSにRPCで読み込ませて実行し、数値と画像で結果を確かめる。道具はPythonパッケージ `plecs_ai` にある。

## 最初に確認すること

次のどれかが欠けていたら、作業を止めてユーザーに頼む。

- PLECS Standalone が起動していて、PreferencesでRPCが有効になっている（既定のポートは1080。違う場合は環境変数 `PLECS_RPC_URL`）。
- `python -c "import plecs_ai"` が通る。通らなければリポジトリの直下で `pip install -e .` を実行する。
- 数値を取りたい信号が、モデルのトップレベルの Signal Outport につながっている。出力ポートが無いと `simulate` は何も返さない。出力ポートは自分で追加してよい（カタログに `Output` がある）。

## 作業の流れ

1. **調べる。** 対象の `.plecs` を読む。部品の一覧、配線、`InitializationCommands` の変数を把握する。
2. **変数で済むか考える。** ゲインや設定値を変えるだけなら、ファイルを編集せず `ModelVars` で上書きして実行する。
3. **編集スクリプトを書く。** ブロックや配線を変えるときは、`make_<新しい名前>.py` を書いて別名のファイルを作る。元のファイルは上書きしない。
4. **検査する。** `python -m plecs_ai.check 新.plecs 元.plecs`。`CHECK OK` が出て、差分が意図どおりであることを確かめる。失敗したらPLECSに読ませない。
5. **実行する。** `plecs_ai.rpc.simulate` で実行し、評価値を計算する。評価用のコードは `run_<試験名>.py` として残す。
6. **見た目を確かめる。** 部品・配線・注釈を追加または移動したら、`python -m plecs_ai.snapshot 新.plecs` で画像を作り、Readで開いて見る。ラベルと配線が重なっていたら座標を直して繰り返す。
7. **報告する。** 下の「報告の形式」に従う。新しく分かった書式は reference に追記する。

モデルのあるフォルダを作業ディレクトリにしてコマンドを実行する。モデル名だけを渡すと、作業ディレクトリの `名前.plecs` を指す。

## 編集の規則

1. **ゲインや設定値は変数で変える。** ファイルを編集するのは構造（ブロック、配線、注釈）を変えるときだけである。パラメータを外から変えたいときは、値を変数名にして `InitializationCommands` に既定値を足す。
2. **書式を推測しない。** 追加してよいブロックは、カタログ（`plecs_ai.edit.list_blocks()`、一覧は `plecs_ai/blocks/INDEX.md`）にあるものと、編集対象のファイルにすでに実例があるものだけである。カタログには約200種類ある。
   - 端子の意味と選択肢の番号は [reference/blocks.md](reference/blocks.md) の「確認済みのブロック」で調べる。そこに無いブロックは、先に `tests/block_tests.py` に試験を足して端子とパラメータを確かめてから使う。INDEX.md で分かるのは端子が入力か出力かだけである。
   - カタログの記述にはデモの変数が入っていることがあるので、`new_block` でパラメータの値を必ず上書きする。
   - カタログに無いブロックが必要なときは、ユーザーにPLECS上で1つ置いて保存してもらい、`python -m plecs_ai.harvest` で取り込む（blocks.md の「ブロックを増やす手順」）。
3. **元のファイルの体裁を保つ。** 改行はCRLF、文字コードはASCIIである。非ASCIIの名前は `base64 "..."` で保存されている。長い文字列は79文字で折り返す。`plecs_ai.edit` の `read`／`write`／`set_init_commands`／`text_annotation` がこれを守る。ファイル先頭の `Name` はファイル名に合わせる（`set_model_name`）。
4. **該当箇所だけを置換する。** ファイル全体を書き直さない。`replace_once` は対象がちょうど1回だけ現れることを確かめる。同じ記述が複数の部品にあるときは `replace_in_component` や `set_param` で部品を絞る。
5. **新しい部品は最初の `Connection {` の直前に入れる**（`insert_components`）。配線は最後の `Connection` の直後、注釈は `Schematic` の末尾に入れる（`append_connections` が振り分ける）。**注釈より後ろに置いた配線は、PLECSがエラーを出さずに無視する**（確認済み）。`plecs_ai.check` が検出する。
6. **生成・編集したモデルには必ずScopeを置く。** 人はRPCの数値を見られないので、PLECSで開いてすぐ波形を確認できるようにする。評価に使う信号（指令と応答、電流など）を軸ごとにまとめる。新しく組むときは `Model.scope`、既存のモデルの編集では `make_pmsm_foc_v2.py` の例を使う。
7. **PLECSに読ませる前に必ず検査する。** `plecs_ai.check` が、波括弧、部品名の重複、配線の接続先、端子の二重使用、From／Gotoのタグ、行の長さ、出力ポートの数を確かめる。
8. **失敗したら原因を1つに絞る。** PLECSのエラー文を記録する。当てずっぽうで同じ編集を繰り返さない。読み込みに2回続けて失敗したら、作業を止めてユーザーに相談する。

書式の詳細は [reference/file-format.md](reference/file-format.md)、ブロックごとの端子番号とパラメータは [reference/blocks.md](reference/blocks.md)、RPCの使い方と癖は [reference/rpc.md](reference/rpc.md) にある。編集の前に、関係するものを読む。

## ゼロからモデルを作るとき

`plecs_ai.build.Model` で、空のモデルにカタログの部品を置いて配線する。実例は `examples/pmsm_foc/make_pmsm_foc.py`（PMSMのベクトル制御。初回の読み込み・初回のシミュレーションで動いた）。

1. **使う部品を洗い出し、規約を先に試験で確かめる。** blocks.md の「確認済みのブロック」に無い部品は、`tests/block_tests.py` に試験を足す。分からない点は `expect=None` で値を表示させて調べる（例：`tests/drive_probe.py`）。dq変換の向き、ゲート信号の値、極対数の定義などを推測のまま組むと、動かなかったときに原因を切り分けられない。
2. **パラメータは初期化コマンドの変数にし、ブロックは平坦な変数を直接参照させる。** あとで `ModelVars` で調整できる。
3. **遠くへ行く信号は Goto／From でつなぐ。** 長い直線の配線が、つながっていない端子の上を通ると、PLECSが読み込みを拒否する。
4. **Scope（`Model.scope`）と出力ポートを置き、評価スクリプト（`run_*.py`）を書く。** Scopeは人が波形を見るため、出力ポートはAIが数値を受け取るためである。 理論値と比べられる量（例：負荷時のq軸電流 = T/Kt）を入れておくと、モデルの誤りに気づける。
5. 画像で配置を確かめる。部品の向き（`Direction`）は見た目と直感的に対応しない。ユーザーがPLECS上で直した向きは blocks.md の「向き」に記録してあるので、それに合わせる。
6. **PWMは三角波（`TriangleGenerator`）とコンパレータで作る**（ユーザーの方針）。中で何が起きているかが見えるからである。コンパレータの出力0/1は、2·s − 1 で変換器のゲート値±1にする。`Symmetrical_PWM` ブロックは使わない。
7. **生成したファイルを、生成スクリプトの再実行で上書きしない。** ユーザーがPLECS上で手直ししていることがある。`Model.write` は既存のファイルを上書きしない。続きの変更は、手直し後のファイルを元にした編集スクリプトで別名に書く（例：`make_pmsm_foc_v2.py`）。

## 道具の早見表

```python
from plecs_ai import edit as pe
from plecs_ai.rpc import connect, simulate, frange

t = pe.read("model.plecs")                       # CRLF/ASCIIを確かめてLFで読む
t = pe.set_model_name(t, "model", "model_v2")
blk = pe.new_block("Constant", "K1", (100, 200), {"Value": "5"})   # カタログから
blk2 = pe.clone_component(t, "Sum2", "SumX", (300, 200))           # 同じファイルから
t = pe.insert_components(t, [blk, blk2])
t = pe.set_param(t, "C1", "v_init", "Vcap_init")
t = pe.append_connections(t, [pe.connection("Signal", "K1", 1, "SumX", 2)])
t = pe.set_init_commands(t, pe.get_init_commands(t) + "\nVcap_init = 10")
t = pe.append_connections(t, [pe.rect_annotation(80, 170, 330, 240),
                              pe.text_annotation(["説明の1行目", "2行目"], (205, 155))])
pe.write("model_v2.plecs", t)

plecs = connect()
time, values, wall = simulate(plecs, "model_v2", {"Vcap_init": 5.0},
                              {"TimeSpan": 1.0, "OutputTimes": frange(0, 1, 1e-4)},
                              reload=True)
```

| コマンド | 用途 |
|---|---|
| `python -m plecs_ai.check 新.plecs [元.plecs]` | 検査。元を渡すと差分と初期化コマンドも表示する |
| `python -m plecs_ai.snapshot モデル [サブシステム]` | 回路図を `results/*.png` に保存する |
| `plecs_ai.build.Model` | 新しいモデルを一から組み立てる（`add`、`wire`、`node`、`goto`、`from_`、`outport`、`scope`、`frame`、`write`） |
| `plecs_ai.edit.remove_component` | 部品と、それにつながる配線をまとめて消す |
| `plecs_ai.edit.swap_block` | 部品を別の種類に差し替える（位置・向き・指定したパラメータを引き継ぐ。端子番号が同じことを先に試験で確かめる） |
| `python -m plecs_ai.harvest 見本.plecs または フォルダ` | 見本にある新しい種類のブロックをカタログに取り込み、INDEX.md を作り直す |
| `python tests/block_tests.py [試験名 ...]` | カタログのブロックをPLECSで動かし、端子とパラメータの意味を確かめる |

## 特に間違えやすい点

- `ModelVars` は初期化コマンドの**後に**代入される。初期化コマンドの中でしか使われない変数（他の変数の計算元）を上書きしても効かない。構造体は辞書で丸ごと渡す。`"APR.Ki"` のような点つきの名前は、エラーにならずに無視される。
- ディスク上のファイルを編集したら、`reload=True` で読み込み直す。`reload=True` は先に `plecs.close` を呼ぶので、ユーザーがPLECS上で保存していない変更は破棄される。ユーザーが開いて作業中のモデルに対して使うときは、先に保存を頼む。
- スイッチング波形をそのまま受け取ると点数が膨大になる。`OutputTimes` で間引く。リップルの真のピークが要るときだけ、短い区間を間引かずに取る。
- ユーザーがPLECS上で手を入れたファイルを、編集スクリプトの再実行で上書きしない。続きの編集は新しいファイル名で行う。

## 報告の形式

課題ごとに短くまとめる。

- 何を変えたか（追加した部品、配線、変数）。
- 検査の結果と、PLECSが読み込めたかどうか。
- 評価項目の数値と、基準値との比較。
- 画像で見た目を確認したかどうか。
- うまくいかなかった点と原因の見立て。確かめた事実と推測は分けて書く。

## 知見を残す

作業の中で新しく分かったことは、同じ作業の中でリポジトリに書き戻す。

| 分かったこと | 書く場所 |
|---|---|
| ブロックの端子番号、パラメータの意味と選択肢の番号 | [reference/blocks.md](reference/blocks.md) の該当ブロックの行 |
| 新しい種類のブロック | `python -m plecs_ai.harvest` で取り込み、`tests/block_tests.py` に試験を足し、blocks.md に行を足す |
| ファイル書式（新しい種類の記述、折り返しなど） | [reference/file-format.md](reference/file-format.md) |
| RPCのコマンドや癖 | [reference/rpc.md](reference/rpc.md) |
| 繰り返し使う処理 | `plecs_ai/` の関数にする |

「確認済み」（PLECSで読み込んで動いた）と「推定」は区別して書く。
