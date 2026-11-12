# ブロックのカタログ

`plecs_ai/blocks/<キー>.plecs` に、PLECSが保存した部品の記述がそのまま入っている。`plecs_ai.edit.new_block(キー, 名前, (x, y), {パラメータ: 値})` で使う。キーは `Type` の名前で、ライブラリ参照（`Type Reference`）はライブラリ上の名前（英数字以外を `_` にしたもの）である。

情報は2段階になっている。

| 文書 | 内容 | 書き方 |
|---|---|---|
| [`plecs_ai/blocks/INDEX.md`](../../../../plecs_ai/blocks/INDEX.md) | 全195種類の一覧。パラメータ名、取り込み元のファイルでの各端子の使われ方（入力か出力か、信号か電気か） | `harvest` が自動生成する。手で編集しない |
| この文書 | 端子が**何の**入力か、選択肢の番号の意味。PLECSで確かめたものだけ | 人とAIが書き足す |

INDEX.md の端子情報は「その番号が入力側・出力側で使われていた」という事実だけである。入力が2つ以上あるブロックでは、どれが何の入力かは分からない（例：SignalSwitch は端子3が制御入力に見えるが、実際は端子4だった）。この文書に無いブロックを使うときは、先に `tests/block_tests.py` に試験を足して確かめる。

## 確認済みのブロック

「確認」の列が「試験」のものは、`tests/block_tests.py` の試験が通ることで確かめた。「実例」のものは、`examples/` のモデルで使って動いた。

### 信号源

| キー | 端子 | パラメータ | 確認 |
|---|---|---|---|
| `Constant` | 1：出力 | `Value` | 実例 |
| `Step` | 1：出力 | `Time`（時刻）、`Before`、`After` | 試験 |
| `Ramp` | 1：出力 | `slope`、`start`（開始時刻）、`X0`（初期値）、`XFinal`（最終値、`inf` 可） | 実例 |
| `SineGenerator` | 1：出力 | `Amplitude`、`Bias`、`Frequency`、`Phase`、`Units`（1：周波数がrad/s、2：Hz） | 試験 |
| `TriangleGenerator` | 1：出力 | `Min`、`Max`、`f`、`DutyCycle`、`Delay` | 実例 |

### 演算

| キー | 端子 | パラメータ | 確認 |
|---|---|---|---|
| `Gain` | 1：入力、2：出力 | `K` | 試験 |
| `Sum` | 1：出力、2以降：入力（`Inputs` の文字の順。`\|` は空き位置） | `Inputs`（例 `\|+-`、`\|++`）、`IconShape`（2が丸） | 実例 |
| `Product` | 1：出力、2以降：入力（`Inputs` の順） | `Inputs`（`*` が乗算、`/` が除算。例 `**/`） | 実例 |
| `Saturation` | 1：入力、2：出力 | `UpperLimit`、`LowerLimit` | 試験 |
| `RelationalOperator` | 1：入力a、2：入力b、3：出力（a 演算子 b） | `Operator`（1：`==`、2：`~=`、3：`<`、4：`<=`、5：`>=`、6：`>`） | 試験 |
| `Comparator` | 1：＋入力、2：−入力、3：出力（＋ > − で1、それ以外で0）。＋にベクトル、−にスカラーを入れると要素ごとに比べる | なし | 試験・実例 |
| `LogicalOperator` | 1：出力、2以降：入力 | `Operator`（6がNOT）、`Inputs`（入力数） | 実例（NOTのみ） |

### 連続系・離散系

| キー | 端子 | パラメータ | 確認 |
|---|---|---|---|
| `Integrator` | 1：入力、2：出力（3：外部リセット、4：状態の出力。どちらも設定で現れる。未試験） | `x0`（初期値）、`UpperLimit`、`LowerLimit`（出力の飽和） | 試験 |
| `TransferFunction` | 1：入力、2：出力 | `Numerator`、`Denominator`（`[0.25 1]` は 0.25s+1）、`X0` | 試験 |
| `RateLimiter` | 1：入力、2：出力 | `RisingRateLimit`、`FallingRateLimit`（負の値）、`SampleTimeMode`（2で誤差なし。1だと1ステップ遅れて0.002ずれた） | 試験 |
| `ZeroOrderHold` | 1：入力、2：出力 | `Ts`（サンプル周期） | 試験 |
| `Continuous_PID_Controller` | 1：偏差入力、2：出力 | `cont_type`（3がPI）、`kp`、`ki`、`up_limit`、`low_limit`（`inf` 可）、`aw_method`（1がなし、2がBack-calculation）、`kbc`、`x0` | 実例 |
| `Discrete_PID_Controller` | 1：偏差入力、2：出力（連続版と同じなので `swap_block` で差し替えられる） | 連続版と同じ（`cont_type`、`kp`、`ki`、リミット、`aw_method`、`kbc`）に加えて、`t_sample`（サンプリング周期）、`int_method`（1：前進オイラー、2：後退オイラー、3：台形則） | 試験・実例 |
| `Turn_on_Delay` | 1：入力、2：出力（3：外部の遅れ時間。設定で現れる。未試験） | `T_d`（立ち上がりだけを遅らせる時間） | 試験 |
| `Moving_Average` | 1：出力、2：入力 | `T_period`、`buffer_size`、`x0` | 実例 |
| `PeriodicAverage` | 1：出力、2：入力 | `T_average`（平均をとる周期） | 試験 |
| `PeriodicImpulseAverage` | 1：出力、2：入力 | `T_average` | 動作のみ。下の注意を参照 |

### 信号の切り替え・配線

| キー | 端子 | パラメータ | 確認 |
|---|---|---|---|
| `SignalSwitch` | 1：出力、2：条件が成り立つときの入力、3：成り立たないときの入力、4：制御入力 | `Criteria`（1：制御 ≥ `Threshold`、2：制御 > `Threshold`、3：制御 ≠ 0）、`Threshold` | 試験 |
| `ManualSignalSwitch` | 1：出力、2：上の入力、3：下の入力 | `SwitchState`（2で端子3が選ばれる。`plecs.get` では `off`） | 実例 |
| `SignalMux` | 1：出力、2以降：入力 | `Width`（入力数）。`Frame` を `[-2, -5·Width; 7, 5·Width]` にしないと端子が枠からはみ出す（`new_block` が自動で直す）。1入力のMuxは赤く描かれるので使わない | 実例 |
| `Goto` | 1：入力 | `Tag` | 実例 |
| `From` | 1：出力 | `Tag` | 実例 |
| `Output` | 1：入力 | `Index`（ポート番号）、`Width`（-1がauto） | 実例 |
| `Scope` | 1以降：入力（軸の順） | `Axes`（軸の数。Parameterではなく直下の項目） | 実例（3軸） |

### 電気

| キー | 端子 | パラメータ | 確認 |
|---|---|---|---|
| `VoltageSource`（制御電圧源） | 1：＋、2：−、3：指令入力（信号） | なし | 実例・試験 |
| `DCVoltageSource` | 1：＋、2：− | `V` | 試験 |
| `CurrentSource`（制御電流源） | 1：流入側、2：流出側（電流は外部回路から1に入り2から出る）、3：指令入力（信号） | なし | 実例 |
| `Ground` | 1 | なし | 試験 |
| `Resistor` | 1、2 | `R` | 実例・試験 |
| `Inductor` | 1、2（1→2が正） | `L`、`i_init` | 実例 |
| `Capacitor` | 1：＋、2：− | `C`、`v_init` | 実例 |
| `Diode` | 1：アノード、2：カソード | `Vf`、`Ron` | 試験 |
| `Switch`（理想スイッチ） | 1、2：主端子、3：制御入力（信号。1で閉じる） | `s_init` | 試験 |
| `MosfetWithDiode` | 1：ドレイン、2：ソース、3：ゲート（信号） | `Ron` | 実例 |
| `Ammeter` | 1：流入、2：流出、3：測定値（信号） | なし | 実例・試験 |
| `Voltmeter` | 1：＋、2：−、3：測定値（信号） | なし | 実例・試験 |
| `2_Level_IGBT_Conv`（3相2レベル変換器） | 1〜3：a〜c相、4：ゲート（幅3の信号。1で上アームオン、−1で下アームオン）、5：直流＋、6：直流− | なし（`therm` は熱モデル） | 試験・実例 |

### モータドライブ

| キー | 端子 | パラメータ | 確認 |
|---|---|---|---|
| `Perm_Magnet_SM`（PMSM） | 1〜3：a〜c相、4：軸（機械系） | `R`、`L`（`[Ld Lq]`）、`phi`（磁束鎖交数）、`p`（極対数）、`J`、`F`（粘性摩擦）、`wm0`、`thm0`、`is0`（`[id0 iq0]`）、`configuration`（2で動作確認。意味は未確認）。a相の磁束は phi·cos(p·θm) で、逆起電力は+q軸に出る | 試験・実例 |
| `3ph_RRF`（abc → dq） | 1：abc（幅3）、3：角度、2：`[d q]`（幅2） | なし。振幅不変の変換で、d軸は cos(角度) の向き | 試験 |
| `RRF_3ph`（dq → abc） | 1：`[d q]`（幅2。幅3を入れるとエラー）、3：角度、2：abc（幅3） | なし | 試験 |
| `RotationalSpeedSensor` | 1：軸、2：角速度 [rad/s]（信号） | `SecondFlange`（1で軸1本、基準は静止系） | 試験 |
| `AngleSensor` | 1：軸、2：機械角 [rad]（−π〜πに折り返す） | `SecondFlange`（1で軸1本）、`theta0` | 試験 |
| `ControlledTorque` | 1：軸、2：トルク指令（信号。正で軸を加速させる） | `SecondFlange`（1で軸1本） | 実例 |
| `Symmetrical_PWM`（三角波比較） | 2：変調率（ベクトル可）、1：スイッチング信号 | `fc`（搬送波周波数）、`carrier_limits`（`[-1 1]` で入力の範囲が±1）、`output_values`（`[-1 1]` で2レベル変換器のゲートにそのまま使える）、`sampling`（下の表） | 試験・実例。ただし新しいモデルでは使わず、三角波とコンパレータで作る（ユーザーの方針） |
| `SignalDemux` | 1：ベクトル入力、2以降：各要素の出力 | `Width` | 試験 |

`Symmetrical_PWM` の `sampling` の値（`plecs.get` が返す表示名で確認済み。GUIのメニューの並び順とは違う）：

| 値 | 方式 |
|---|---|
| 1 | ナチュラル（キャリア波形開始：中間値） |
| 2 | ナチュラル（キャリア波形開始：最大値） |
| 3 | レギュラー（ダブルエッジ更新） |
| 4 | レギュラー（シングルエッジ更新：最大値） |
| 5 | レギュラー（シングルエッジ更新：最小値） |
| 6 | ナチュラル（キャリア波形開始：最小値） |

選択肢のパラメータの番号は、このように `plecs.get(部品のパス, パラメータ名)` で表示名を読めば、推測せずに確かめられる。

機械系の配線は `Connection` の `Type` を `Rotational` にする。

`ControlledRotationalSpeed`（回転数を強制する源）は、慣性を持つ機械（PMSMなど）の軸に直接つなぐと「不整合なソース」で止まる。コンデンサに電圧源を直接つないだのと同じである。一定速度で回したいときは、機械の `J` を非常に大きくし（1e6など）、`wm0` に初速度を与えて惰性で回す。

## 向き（ユーザーがPLECS上で直したもの）

`Direction` と `Flipped` は見た目と直感的に対応しない。`examples/pmsm_foc/pmsm_foc.plecs` でユーザーが直した値を記録する。左から右へ流れる配置での値である。

| キー | `Direction` | `Flipped` | `LabelPosition` | 見た目 |
|---|---|---|---|---|
| `Ammeter` | `left` | off | `north` | 端子1が左、端子2が右、測定端子が上 |
| `2_Level_IGBT_Conv` | `down` | on | `south` | 直流側が左、交流側が右 |
| `RRF_3ph` | `up` | off | `north` | 入力が左、出力が右 |
| `3ph_RRF` | `up`（カタログのまま） | off | `south` | 入力が左、出力が右 |

## 使うときの注意

- **パラメータの値は必ず上書きする。** カタログの記述には、取り込み元のモデルでの値がそのまま入っている。195種類のうち67種類は、取り込み元のデモの変数を参照している（例：`RateLimiter` の `1/tr`）。上書きしないと、PLECSが「変数が未定義」で止まる。`plecs_ai.check` はこれを検出できない。
- **端子が設定で増減するブロックがある。** `Integrator` の外部リセット、`Turn_on_Delay` の外部の遅れ時間など、パラメータで端子が現れるものは、そのパラメータを変えたときの端子番号を試験で確かめてから使う。
- **選択肢のパラメータの番号は推測しない。** 試験で確かめるか、PLECS上で設定を変えた同じブロックを見本に並べて保存し、ファイル上の値を比べる。
- **`PeriodicImpulseAverage` は連続信号に使わない。** 定数3を入れると、`T_average` が0.1でも0.01でも3000が出た（確認済み）。3 ÷ 最大ステップ幅（1e-3）に一致するので、インパルス（スイッチング損失など）の平均を取るための専用ブロックだと推測している。
- **`Input` と `Port` はサブシステムの端子である。** カタログにはあるが、トップレベルでの使い方は確かめていない。
- トップレベルに `Output` を足すときは、ファイル先頭側の `Terminal { Type Output / Index "n" }` も1つ足す。`plecs_ai.check` が数の不一致を検出する。
- `From` のタグには対応する `Goto` が必要で、`Goto` のタグは重複できない。

## カタログに入らないもの

- **サブシステム**（`Subsystem`、`ConfigurableSubsystem`）と**モデル参照**（`ModelReference`）は取り込まない。中に回路図を持っていて、単独のブロックではないからである。中の部品は取り込まれる。
- 種類が同じなら、最初に見つかった1つだけを取り込む。端子の数が設定で変わるブロック（入力数が可変のSumなど）は、取り込み元の設定のままになっている。

## 代用の例

カタログに本物があるので、新しく作るときは本物を使う。下の代用は、カタログが小さかった頃の実験（モデルは非公開）で動いた実績として残す。

| 欲しいブロック | 今後の使い方 | 以前の代用 |
|---|---|---|
| Saturation | `Saturation` | PIDを `kp=1`、`ki=0`、リミット付きにした |
| Integrator | `Integrator` | PIDを `kp=0`、`ki=1` にした |
| Rate Limiter | `RateLimiter`（`SampleTimeMode=2`） | Sum → 飽和 → 積分器の帰還ループにした。小信号では一次遅れになる |
| Step | `Step` | `Ramp` を `slope=1e7` にした |
| Gain | `Gain` | 使っていない |

## ブロックを増やす手順

1. PLECSで新しいモデルを作り、欲しいブロックを置く。できれば入出力をすべて何かにつなぐ（INDEX.md に端子の向きが載る）。選択肢のパラメータは、使いたい設定にしておく。
2. `samples/<内容>.plecs` として保存する。
3. `python -m plecs_ai.harvest samples/<内容>.plecs` を実行する。新しい種類ごとに `plecs_ai/blocks/<キー>.plecs` ができ、INDEX.md が更新される。フォルダを渡すと、中の `.plecs` をすべて読む（PLECS付属の `demos` フォルダも読める）。
4. `tests/block_tests.py` の `CASES` に試験を足す。分からないパラメータや端子は、まず `expect=None` で値を表示させて意味を調べ、分かったら期待値を書く。
5. `python tests/block_tests.py` がすべて通ったら、この文書の表に行を足す。
6. `samples/` の見本、`plecs_ai/blocks/` の変更、`tests/block_tests.py`、この文書をまとめてコミットする。

## 今後確かめたいブロック

デモから取り込み済みで、試験がまだのもの。電力変換でよく使いそうな順に挙げる。

`Delay`、`DiscreteTransferFunction`、`PulseGenerator`、`Relay`、`Abs`、`MinMax`、`Signum`、`Function`、`Math`、`Lookup1D`、`Offset`、`SignalSelector`、`Memory`、`EdgeDetection`、`Igbt`、`IgbtWithDiode`、`Mosfet`、`Thyristor`、`ACVoltageSource`、`DCCurrentSource`、`Transformer`、`MutInductor`、`ThreePhaseVoltageSource`、`ThreePhaseMeter`、`Space_Vector_PWM`、`Sawtooth_PWM`、`Blanking_Time`、`Single_Phase_PLL`、`Three_Phase_PLL`、`Inertia`、熱モデル（`HeatSink`、`ThermalResistor` など）。
