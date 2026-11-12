# PLECSのRPC

PLECS Standalone のXML-RPCサーバーに、同じPCから接続する。Preferencesで有効にする必要がある（既定では無効）。接続先は `http://localhost:1080` で、環境変数 `PLECS_RPC_URL` で変えられる。

```python
from plecs_ai.rpc import connect, simulate, load, circuit_bitmap, frange
plecs = connect()
```

## コマンド

| コマンド | 用途 |
|---|---|
| `plecs.load(path)` | モデルを開く。絶対パスで指定する |
| `plecs.close(name)` | 保存せずに閉じる。未保存の変更は破棄される |
| `plecs.simulate(name[, opts])` | 実行する。トップレベルに出力ポートがあれば `{"Time": [...], "Values": [[...], ...]}` を返す |
| `plecs.get(path[, param])` | 部品のパラメータを読む。`param` を省くと全部返す |
| `plecs.set(path, param, value)` | 開いているモデルの部品のパラメータを変える（保存はされない） |
| `plecs.scope(path, cmd, ...)` | スコープの波形を保持・消去・保存する（`HoldTrace`、`ClearTraces`、`SaveTraces`） |
| `plecs.analyze(name, analysisName[, opts])` | 定常解析やACスイープを実行する（未使用） |
| `plecs.webserver("getCircuitBitmap", path, {})` | 回路図のPNGと部品の枠を返す。マニュアルに無い |
| `plecs.getModelTree(path)` | モデルの木構造を返す。絶対パスが要る（未使用） |
| `system.listMethods()` | 公開されているメソッドの一覧 |

部品のパスは `モデル名/部品名` である。`simulate` と `analyze` は同時に1つしか実行できない。

## `simulate` のオプション

```python
opts = {
    "ModelVars": {"Icap_max": 6.0, "ACR": {"Kp": 0.09, "Ti": 2e-4, "Ki": 400.0}},
    "SolverOpts": {"TimeSpan": 10.0, "OutputTimes": frange(0, 10, 1e-4)},
}
```

- **`ModelVars` は初期化コマンドの後に代入される。** 初期化コマンドの中で他の変数の計算にしか使われない変数（例：`omega_n`）を上書きしても、計算済みの値（`ACR.Kp` など）は変わらない。結果が基準と完全に一致したら、これを疑う。対策は、ブロックが直接参照している変数を上書きするか、スクリプト側で派生値を計算して渡すことである。
- **構造体は辞書で丸ごと渡す。** フィールドを1つだけ変えることはできない。
- **`"APR.Ki"` のような点つきの名前は、エラーにならずに無視される。**
- 出力ポートが複数あると、`Values` は Out1 の信号、Out2 の信号の順に並ぶ。Muxでまとめた信号は入力の順に展開される。
- `OutputTimes` を付けると、その時刻の値だけが返る。付けないとソルバの全ステップ（スイッチングの瞬間を含む）が返る。100 kHzのスイッチングで0.1秒が約8万点である。
- 出力時刻をキャリアの谷（スイッチング周期の倍数）に合わせると、インダクタ電流の標本値はほぼ周期平均になる。リップルの真のピークを見るには、`OutputTimes` を付けないか、0.1 µs刻みの短い区間を指定する。

## `plecs.get` の戻り値

選択肢のパラメータは、ファイル上の番号ではなくGUIの表示文字列で返る（例：`cont_type` は `PI`、`aw_method` は `Back-Calculation`、日本語UIでは `ex_sat` が `内部`）。ライブラリの部品は `Type` が `Subsystem` と返る。パラメータ名の調査には使えるが、ファイルに書く値は分からない。

## 回路図の画像

```python
png, comps = circuit_bitmap(plecs, "model")      # reload=True が既定
```

- `comps` は `{部品名: {"dimensions": {"left", "top", "width", "height"}, "type": ...}}` である。値は画像の画素で、回路図の座標と1対1（ずれは図全体で一定）。名前ラベルと注釈は含まれない。
- サブシステムの中は `モデル名/サブシステム名` で取れる（`python -m plecs_ai.snapshot モデル サブシステム`）。
- 回路図をPDFで出力するRPCメソッドは無い。

## エラー

- PLECSのエラーは `xmlrpc.client.Fault` として届く（`plecs_ai.rpc.Fault`）。PLECSが日本語表示なら、エラー文も日本語である。
- **エラー文はPLECSからは正しいUTF-8で届く**（確認済み）。以前「文字化けする」と書いたのは誤りで、日本語版Windowsのコンソールに出すときにPythonがcp932で出力し、AIがそれをUTF-8として読んでいたのが原因だった。`import plecs_ai` で標準出力がUTF-8に切り替わる。`plecs_ai` を使わないスクリプトでは、環境変数 `PYTHONIOENCODING=utf-8` を設定する。
- エラー文には原因の部品のパスが入っている（例：「コンポーネント 'model/dq2abc' …ターミナル（2）に接続された信号は、信号数（3）と一致しません」）。まずそれを読む。
- `OutputTimes` に `TimeSpan` を少しでも超える時刻があるとエラーになる。浮動小数点の誤差でも起きるので、`plecs_ai.rpc.frange` を使う（最後の値を終了時刻で切る）。
- 実行時間が急に延びたら、追加した連続系のループが速すぎないか（高い帯域の一次遅れなど）を疑う。原因の切り分けはまだしていない。
