<!--
![loopian_logo](doc/loopian_logo.gif)
-->
<img src="doc/loopian_logo.gif" width="50%">

loopian Alpha-version
=================================

about loopian
--------------

'loopian' is a sequencer for piano tones with text input that we are developing for use mostly in Live Coding.


loopian とは
------------

loopian は、Live Coding などで使うために開発している、テキスト入力によるピアノ音色用シーケンサです。



用語集 (Glossary)
-------------------

- phrase : 階名にて指定する単パートの音群
- composition : phrase に適用する数小節分の Chord 情報
- loop : loopian は基本的に、phrase/composition を繰り返し演奏する。この繰り返す単位
- part : phrase は独立した４つの Loop 再生が可能である。その４つを part と呼び、各 part は left 1(L1)/left 2(L2)/right 1(R1)/right 2(R2) という名前で示される。


起動と終了
--------------

- 起動
    - 'python loopian.py'  : 通常の python スクリプトと同じ
    - './loopian.sh'       : shell script として
- 入力
    - 'L1> ' : prompt
        - L1> は Left 1 の入力状態であることを示す
        - このプロンプトの後に、コマンドやフレーズを書き込む
    - カーソルによる過去入力のヒストリー呼び出しが可能
- 終了
    - 'quit' 'exit' : 終了


音を出すための外部環境
--------------------

- 外部 MIDI 音源を繋ぐ
- マルチパートで MIDI受信するアプリを同時に起動する。以下のアプリで動作確認済。
    - Logic : Mac で MIDI 演奏するための DAW


再生コントロール
--------------

- 'play' 'start' : シーケンス開始
- 'fine' : この小節の最後でシーケンス終了
- 'stop' : 直ちにシーケンス終了
- 'sync' : 次の小節の頭で、ループ先頭に戻る
    - sync       : そのパートのみ
    - sync right : 右手パート(right1/2)
    - sync left  : 左手パート(left1/2)
    - sync all   : 全パート


Phrase 追加
-------------

- [*note*][*duration*][*musical expression*] : phrase 追加の書式
    - *note*: 階名
    - *duration*: 音価
    - *musical expression*: 音楽表現
    - [*duration*] と [*musical expression*] は省略可能
        - 階名と音価の全体の数が合わないとき、階名の内容で数を合わせる。
        - 音価は、足りない時は最後の数値がそのまま連続し、多い時は途中で打ち切られる。
        - 音価を省略した場合全て四分音符とみなす。
    - [] : 全データ削除
    - +[d,r,m] : 最初に + を付けることで、今まで入力したPhraseの後ろに、新しい小節を連結できる。
        - + を使って複数のPhraseを連結する場合、音価、音楽表現の省略は、最初のデータに従う

- 階名表現
    - d,r,m,f,s,l,t: ド、レ、ミ、ファ、ソ、ラ、シ
    - di,ri,fi,si,li: ド#、レ#、ファ#、ソ#、ラ#
    - ra,ma,sa,lo,ta: レb、ミb、ソb、ラb、シb
    - -d: 1オクターブ下のド、 +d: 1オクターブ上のド、--d: 2オクターブ下、++d: 2オクターブ上
    - ',': 各音の区切り。１小節を超えたら捨てられる。カンマを連続すると直前の音を繰り返す。
    - '|': 小節区切り
    - x: 休符
    - d=m=s, : 同時演奏
    - |:d,r,m:3| : ドレミを３回繰り返し、合計４回演奏（数字がなければ1回繰り返し） <- 止める
    - <d,r,m>*4 : ドレミを４回演奏
    - d*4 : ドを４回連続して発音

- 音価表現
    - [8:] , [:8] は基準音価が 8 であることを示す
        - 基準音価は任意の数値が指定可能で、全音符の長さの何分の1かを示す数値となる
        - 基準音価(:n, n:)を省略した場合、全て四分音符とみなす
    - [1,1,1,1:8] : 八分音符を４回
        - :n と基準音価を書く場合、各音の音価指定の後ろに書く
        - [8:1,1,1,1] : n: と書く場合、各音の音価指定の前に書く
        - [2,1,2,1,3:12] : 一拍3連(12分音符)で、タータタータター
        - [1:2] のように書くと、どちらが基準音価か分からないので、値の大きい方を基準音価とみなす
    - [<2,1>:12] : とすると、この後もずっと 2,1 の長さを繰り返す
        - <2,1>*2 のように階名と同じように繰り返し回数の指定ができる
        - 繰り返し記号の終わりが音価表現全体の最後の場合、このパターン全体を回数制限なく繰り返すが、最後でないと回数指定分しか繰り返さない。

- 音楽表現
    - f,mf,mp,p,pp: 音量
    - ped,noped: Pedal 指定（ped がデフォルト)


Composition 指定
----------------------------

- {*chord*}{*musical expression*} : Composition の書式
    - *chord*: chordを小節ごとにカンマで区切って時系列で記述
    - *musical expression*: 音楽表現
    - {I,,IV,V} : １小節ごとに I -> I -> IV -> V と和音が変わる
        - 複数小節を同じchordにしたい場合、カンマのみ記述
    - {} : 全データ削除
    - +{I} : 最初に + を付けることで、今まで入力したchordの後ろに、新しい小節を連結できる。
        - + を使って複数のchordを連結する場合、音楽表現の省略は、最初のデータに従う


- Detail of description
    - chord
        - O : original phrase
        - I : d=m=s（Iの和音)
            - ローマ数字: I, II, III, IV, V, VI, VII
        - I# : di=mi=si (数字の後に # を付けると半音高いコードになる。b は半音）
        - V : s=t=r (Ⅴの和音)
        - VIm : l=d=m (m: minor)
        - IVM7 : f=l=d=m (M7: major7th)
        - IIIm7-5 : m=s=ta=r (m7-5: minor7th -5th)
        - diatonic : d=r=m=f=s=l=t (Diatonic Scale)
        - lydian : d=r=m=fi=s=l=t (Lydian Scale)
        - thru : 全ての音
    - 音楽表現
        - para : 和音変換時、root に合わせて並行移動する 


入力環境コマンド
----------------

- 'right 1' 'left 1' : 右手２パート、左手２パートの４パートを指定可能
- 'all' : 全パートの入力モードになる
- 'midi 1' : MIDI PORT 1 を選択
- 'panic' : 今鳴っている音を消音する


調、テンポ、拍子、音量
-------------------

- 'set bpm=100' : BPM（テンポ）=100 にセット
- 'set beat=4/4' : 拍子を 4/4 にセット
- 'set key=C4' : key を C4 にセット
    - loopian にとって key とは [d]（ド） と指示されたときの音名を表す
    - デフォルト値は C4(midi note number=60)
    - 音名は C-B と大文字で表現し、必要に応じて前に #, b を足すことができる
    - 音名の後ろの数値はオクターブを指示するが、省略可能
        - 省略した場合、今設定されているオクターブがそのまま適用される
- 'set oct=+1' : 現状から１オクターブ上げる
    - set 以降に all を付け足すと、全 part に効果、付けなければ入力中の part に対してのみ効果
    - 'set oct=0,0,-1,+1' : 4つのパートのオクターブを一度に設定できる
