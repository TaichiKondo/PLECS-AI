# `.plecs` ファイルの書式

PLECS Standalone 5.0 が保存したファイルから分かったことをまとめる。断りが無い項目は、編集したファイルをPLECSが読み込んで動いたことで確認済みである。

## 全体

- テキストファイルで、改行はCRLF、文字コードはASCIIである。
- 1行は79文字以内である。
- 構造は次のとおり。

```
Plecs {
  Name          "モデル名"            ← ファイル名（拡張子なし）と同じにする
  ...ソルバなどの設定...
  InitializationCommands "..."
  Terminal { Type Output / Index "1" }   ← トップレベルの入出力ポート1つにつき1個
  Schematic {
    Component { ... }                    ← 部品
    Connection { ... }                   ← 配線（部品のあと）
    RectangleAnnotation { ... }          ← 枠線（配線のあと）
    Annotation { ... }                   ← テキスト
  }
}
```

## 文字列

- **折り返し**：長い文字列は複数行に分かれる。1行目は `キー "` で始まり、79文字目に閉じ引用符が来るまで詰める。続きの行は行頭から `"` + 77文字 + `"` である。`\n` などのエスケープの途中では切らない。`plecs_ai.edit.wrap_string` がこの形を作る。元のファイルの `InitializationCommands` を1文字も違わず再現できる。
- **非ASCII**：日本語などを含む名前やテキストは `Name base64 "..."` の形になる。中身はUTF-8のbase64である。例：`base64 "6Zmk566X77yaRGl2aWRl"` は「除算：Divide」。既存のものはそのまま保つ。配線の `SrcComponent`／`DstComponent` も同じ `base64 "..."` で参照する。
- **部品名の改行**：`"Continuous PID\nController"` のように `\n` で書かれる。ライブラリ参照のパス（`SrcComponent`）の中では `\\n` になる。
- 新しく追加する部品名と変数名はASCIIにする。注釈のテキストは日本語でよい（`text_annotation` がbase64にする）。

- **パラメータ値の折り返し**：長い `Value` も同じ形で折り返される（例：`TransferFunction` の `Denominator`）。`set_param`／`new_block` は続きの行ごと置き換える。

## PLECS付属のデモ

`C:\Users\<user>\Documents\Plexim\PLECS 5.0 (64 bit)\demos` の92ファイルは、改行がLFで保存されている（Standaloneで保存したファイルはCRLF）。どちらもASCIIである。`plecs_ai.harvest` は両方を読める。`plecs_ai.edit.read` はCRLFだけを受け付けるので、デモを直接編集したいときは、Standaloneで開いて別名で保存してから扱う。

## サブシステム

サブシステムの部品は `Type Subsystem` で、中に自分の `Schematic { ... }` を持つ。中の部品と配線は、外側より字下げが深いだけで同じ書式である。部品名と配線の参照は、そのサブシステムの中だけで有効になる。中の入出力端子は `Type Input`／`Type Output`（信号）と `Type Port`（電気）である。サブシステムの編集はまだ試していない。

## 初期化コマンド

`InitializationCommands` にOctave形式の文が `\n` 区切りで入っている。`get_init_commands` で改行つきの文字列として取り出し、`set_init_commands` で書き戻す。`"` と `\` を含む文は書けない（`set_init_commands` が拒否する）。

## 部品

```
    Component {
      Type          Sum
      Name          "Sum2"
      Show          off                 ← 名前ラベルを表示するか
      Position      [65, 465]           ← 部品の中心
      Direction     up
      Flipped       off
      LabelPosition south               ← south / north / east / west
      Parameter {
        Variable      "Inputs"
        Value         "|+-"
        Show          off
      }
    }
```

- `Name` はモデル内で重複してはいけない。
- ライブラリの部品（PID、Ramp、Moving Averageなど）は `Type Reference` で、`SrcComponent "Components/Control/..."` と `Frame`、`Terminal { ... }` の並びを持つ。この種類は必ず実例の複製で作る。
- 選択肢のパラメータは番号で保存される（例：PIDの `cont_type "3"` がPI）。`plecs.get` はGUIの表示文字列を返すので、番号は分からない。番号は実例か、ユーザーにPLECS上で切り替えて保存してもらって調べる。
- 新しい部品は、最初の `Connection {` の直前に入れる。

## 配線

```
    Connection {
      Type          Signal              ← Signal（制御信号）か Wire（電気配線）
      SrcComponent  "From5"
      SrcTerminal   1
      Points        [235, 655]          ← 折れ点。省略できる
      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }
      Branch {
        Points        [235, 760]
        DstComponent  "Mux"
        DstTerminal   2
      }
    }
```

- `Type` は領域ごとに決まっている：`Signal`（制御信号）、`Wire`（電気）、`Rotational`（回転機械）、`Translational`（直動機械）、`Magnetic`（磁気）、`HeatPipe`（熱）。
- 分岐が無ければ `DstComponent`／`DstTerminal` を直接書く。
- 分岐は `Points` の最後の点から `Branch` を2つ出す。3方向以上に分けるときは `Branch` の中に `Points` と `Branch` を入れ子にする。
- 端子番号は部品の種類ごとに決まっている（[blocks.md](blocks.md)）。1つの端子は1つの配線にしか使えない。
- 直結の配線を分岐に書き換えても読み込める。
- `Points` を省くとPLECSが端子どうしを直線で結ぶ。斜めの線になることがあるので、端子の高さが違うときは折れ点を書く。
- **配線が、どこにもつながっていない端子の上を通ると、PLECSは読み込みを拒否する**（「回路図中に他の要素と重複した無接続のターミナルがあります」）。確認済み。長い配線には折れ点を付けて部品の列を避けるか、Goto／Fromを使う。`plecs_ai.check` はこれを検出できない。
- **`Schematic` の中では、配線（`Connection`）を注釈（`RectangleAnnotation`、`Annotation`）より前に置く。** 後ろに置いた配線は、PLECSが読み込み時にエラーを出さずに無視する（確認済み：同じ内容で順序だけを変えると描かれた）。PLECSが保存したファイルは注釈が末尾にあるので、配線を足すときに注意する。`plecs_ai.check` が検出する。
- 1つの端子から2本の `Connection` を出してはいけない。分岐（`Branch`）にする。`plecs_ai.check` が検出する。

## 座標と見た目

- 座標の単位は画面の1画素相当で、グリッドは5刻みである。y は下向きが正である。
- 端子の位置の目安：四角いブロックは枠の辺上。丸いSum（`IconShape 2`）は半径10で、`|+-` なら2が左、3が下。2入力のProductは入力が上下5、3入力は上下10の間隔。PIDブロックは枠が ±40 × ±25 で、入力が左、出力が右。
- 名前ラベルは枠の外側に、高さ約13（1行あたり）で描かれる。配線は枠から20以上離す。ラベルが配線と重なるときは `LabelPosition` を変える。
- 文字の幅の目安：日本語が約10、英数字が約6.5。
- 見た目は必ず `python -m plecs_ai.snapshot` の画像で確かめる。ラベルの大きさはファイルにもRPCの戻り値にも無い。

## 注釈

```
    RectangleAnnotation {
      Position     [770, 485]           ← 枠の中心
      Width        190
      Height       140
      CornerRadius 3
      Thickness    2
      PenColor     4278190080           ← 0xFF000000（黒）
      PenAlpha     1
      BrushColor   0
      BrushAlpha   0                    ← 塗りつぶしなし
    } 
    Annotation {
      Name          "<html><body>\n<p>ACR</p></body></html>"
      Position      [760, 400]          ← テキスト全体の中心
    } 
```

- どちらも閉じ括弧のあとに空白が1つ付く（`} `）。
- テキストはHTMLである。`<p>` を並べると複数行になり、左揃えで描かれる。
- `rect_annotation(left, top, right, bottom)` と `text_annotation(lines, center)` を使う。
- 枠の題名は、枠の上辺から15上に置くと収まりがよい。
