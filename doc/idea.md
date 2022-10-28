# Loopian developping memo

## what's this

- text command による loop sequencer
- 音色はピアノを想定し、ミニマルな音楽を指向する
- command は一行単位で入力
- 移動ド(d,r,m..)による階名指定
- コード(I,II..)指定で、入力に変化を与えながらループ再生
- 自動にピアノの表現を付加
- BPM, Key, 拍子(Beat)などの基本的な音楽指示が可能

## what you can do

- Live Coding
- Musical Education
- Loop Sequencer
- Dynamic Easy Listening
- Interactive Art(with Device)

## Spec.
### piano 専用 Realtime Loop Generator (Text Sequencer)

- Input Part は4つ
    - L(L1), L2, R(R1), R2
- Pedal 用隠しパートが一つ
- MIDI ch. は一つ

### 出力 MIDI

- Note On/Off
- Sustain CC#64
- Reverb Depth CC#91
- Volume CC#7

### テキスト入力

- ユーザーは、Phrase入力（ [] で入力）と、Composition入力（{}で入力）の二つの入力ができる
- Phrase入力の考え方
    - User は、ノート番号とタイミング、簡易な表情指示(Music Expression)を入力
    - exp.engine は、簡易な表情指示からベロシティ、微妙なタイミング、dulation、ペダル情報を自動生成
- Composition入力と、自動和音変換
    - Composition で指定された和音に従って、Phrase 入力の音は自動変換される
    - Composition も、各パートごとに設定する
    - 全体に同じ Composition を適用したい場合、全パート入力モードにする
- 各パートの Phrase も、Composition も、それぞれ独自の周期で loop する
- Phrase入力 Music Expression 一覧
    - ff,f,mf,mp,p,pp,ppp  （ベロシティ指定）
    - ped, noped （ペダル奏法）
    - artic: stacc,legato,marc （dulation指定）
    - p->f など音量の漸次的変化
- Composition入力 Music Expression 一覧
    - para  （コード変換の指定）


## Dev.

```mermaid
classDiagram
ElapseIF <|-- Part
ElapseIF <|-- Loop
Loop <|-- PhraseLoop
Loop <|-- CompositionLoop
ElapseIF <|-- Note
ElapseIF <|-- Damper
SeqStack o-- Part
SeqStack o-- PhraseLoop
SeqStack o-- CompositionLoop
SeqStack o-- Note
SeqStack o-- Damper
SeqDataAllStock *-- PhraseDataStock
SeqDataAllStock *-- DamperPartStock
SeqDataAllStock *-- CompositionPartStock
SeqDataAllStock <-- SeqStack
```

### 自動変換

- データは以下の過程で内容を書き換えられていく
    1. ユーザーが入力した生データ(生/raw)
    1. 生データに足りないデータを補填したり、追加フレーズを繋げたデータ(補填/complement)
    1. SMF 的な、tick/note/velocity をセットにしたデータ(再構成/recombined)
    1. コード変換時に自然な変換をするための分析データ(分析/analyzed)
    1. velocity/duration を生演奏に近づけたデータ(生演奏/humanized)
    1. random要素を加味したデータ(乱数/randomized)
    1. コードの反映(変換/translated)
    - 上記のうち、最初の５つはユーザーによる入力時に行う処理、楽譜情報から離れない状態
    - 小節冒頭にこのデータが Loop Obj.にロードされる
    - 再生時、リアルタイムに最後の二つの処理が行われる
- 上記の各データが、他の要因で変更されるタイミング
- bpm/beat/key が変わったら、「再構成」からやり直し
- 再生で Loop がひとまわりするたびに「乱数」からやり直し
- phrase が入力されたら、最初からやり直し
- composition が入力されたら、「再構成」からやり直し
- 実際の MIDI 出力はさらに、バッファに積まれ、latency の時間の後に出力される


### Filter

- [raw] を指定しない限り、勝手に exp.engine によるフィルタがかけられる
- Humanization Filter
    - 強拍/弱拍(linear) -> velocity [実装済み]
        - bpm が高いほど強調(bpm:72-180)
    - 時間間隔(Non-linear) -> velocity/duration
        - Note OffとNote Onの間隔は、短い音符になるほど、時間一定になりやすい
        - 細かい音符は大きな velocity で弾くことは困難(limit)
    - 未来密度、過去密度(linear) -> velocity/duration
        - 密度：現在より２拍以内（未満ではない）にある音符×距離の総和
        - 過去密度が高く、未来密度が低い場合、フレーズの終わりとみなし、velocity/duration は減らす
        - 過去密度が低く、未来密度が高い場合、フレーズの開始とみなし、volocity をちょっと減らす
        - 両密度とも高いとき、少し強め
    - 音高平均との差(linear) -> velocity
        - フレーズの平均音高より離れていると、velocity は強くなる
- Translation Filter
    - Common
    - Arpeggio
        - 連続して同じ音が出ない
        - 四分音符未満の長さに適用
    - Parallel

### 次にやること
- アルペジオで連続して同じ音が出ないようにする -> 同音回避型和音変換対応　済
- ベロシティが、周期的に変わる謎の現象 -> copy されていなかった不具合修正　済
- | を小節区切り対応、 ,, 連続で同じものを補填する対応　済
- 小節の先頭の音が、時々和音が変わらない音で出てしまう不具合　済
- 左手用に、平行移動型の和音変換、Music Expressionへの追加(trans:para/parallel)　済
- Composition を４つのパート独立に設定できる　済

- Pedal On/Off の Music Expressionへの追加(noped)
- さらなる humanized アルゴリズムの追加
- Load/Save機能、Auto Load機能

## loopian 計画
- loopian を使った動画制作
- loopian::device によるリアルタイム演奏
- GUI/MIDI以外を rust に書き換える

### 動画作成
- QuickTime Player で新規画面収録
- 画面サイズ 896 * 504
- オーディオ出力 : 複数出力装置（BlackHole & xxxのスピーカー）
    - DAWの出力も確認
- 録音設定 : オプションから BlackHole 2ch を選択
- Audio MIDI -> オーディオ装置 -> 「複数出力装置」選択 -> マスター装置: BlackHole 2ch
- iMovieに入れるが、YouTubeではなく、ファイル出力指定にする
- 紹介文
Loopian is a looping real-time sequencer that specifies notes by text.
It is primarily designed to control Piano tones.
It is being developed for use in Live Coding-like real-time text input to generate music, loop-based phrase transformations in real-time for performance, interactive art, etc.
- Loopian は、テキストで音符を指定するループ型のリアルタイムシーケンサです。
主に Piano 音色を操作するための機能を備えています。
Live Coding 風にリアルタイムにテキストを入力して音楽を生成したり、ループベースのフレーズをリアルタイムに変容させるパフォーマンスやインタラクティブアートなどに使用することを念頭に開発中。