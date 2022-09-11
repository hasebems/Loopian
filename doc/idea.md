Loopian

- what's this
    - text command による loop sequencer
    - 音色はピアノを想定し、ピアノによるミニマル音楽を指向する
    - command は一行のみ
    - 移動ド(d,r,m..)による階名指定
    - 調指定(A-G#)とコード(I,II..)指定でループ再生
    - 自動にピアノの表現を付加

- piano 専用 Realtime Loop Generator (Text Sequencer)
    - Input Part は4つ
        - L(L1), L2, R(R1), R2
    - Pedal 用隠しパートが一つ
    - MIDI ch. は一つ
- 出力 MIDI
    - Note On/Off
    - Sustain CC#64
    - Reverb Depth CC#91
    - Volume CC#7
- Data 構造
    - 考え方
        - User は、ノート番号とタイミング、簡易な表情指示を入力
        - exp.engine はベロシティ、微妙なタイミング、dulation、ペダル情報を自動生成
        - 入力時の解析タイミングと、最終MIDI出力時のタイミングで、処理が分担される
            - 入力時には解析metaデータが生成される
            - 出力時に、metaデータをもとにMIDIデータが算出される
    - 入力フレーズデータ
        - KeyEvent: Note On Timing, Note Number, Expression
        - Expression: dolce, stac., legato, marc./marcato, con brio, 
            strong, normal, calm, fluent, leap
    - 解析metaデータ
        - RepeatData
        - Attribute
        - Chord
    - 出力データ
        - Timing
        - Velocity
        - Duration
        - PedalEvent
