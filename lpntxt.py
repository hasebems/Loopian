# -*- coding: utf-8 -*-
import re
import math
import lpnlib as nlib
import copy

def convert_exp2vel(exp_text):
    if exp_text == 'ff':
        vel = 127
    elif exp_text == 'f':
        vel = 114
    elif exp_text == 'mf':
        vel = 100
    elif exp_text == 'mp':
        vel = 84
    elif exp_text == 'p':
        vel = 64
    elif exp_text == 'pp':
        vel = 48
    elif exp_text == 'ppp':
        vel = 24
    elif exp_text == 'pppp':
        vel = 12
    elif exp_text == 'ppppp':
        vel = 1
    else:
        vel = nlib.END_OF_DATA
    return vel


def convert_doremi_2(doremi, last_pitch):
    last_note = last_pitch
    while last_note >= 12:
        last_note -= 12
    while last_note < 0:
        last_note += 12

    if len(doremi) == 0: return nlib.NO_NOTE
    oct_pitch = 0
    while len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'x': return nlib.NO_NOTE
        elif l0 == '+': oct_pitch += 12
        elif l0 == '-': oct_pitch -= 12
        else: break
        doremi = doremi[1:]

    base_note = 0
    if len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'd': base_note += 0
        elif l0 == 'r': base_note += 2
        elif l0 == 'm': base_note += 4
        elif l0 == 'f': base_note += 5
        elif l0 == 's': base_note += 7
        elif l0 == 'l': base_note += 9
        elif l0 == 't': base_note += 11
        else: return nlib.NO_NOTE
    else: return nlib.NO_NOTE
    doremi = doremi[1:]

    if len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'i': base_note += 1
        elif l0 == 'a': base_note -= 1

    base_pitch = 0
    if oct_pitch == 0:      # +/- が書かれていない場合
        diff = base_note - last_note
        if diff < 0: diff += 12
        if diff > 6:
            base_pitch = last_pitch+diff-12
        else:
            base_pitch = last_pitch+diff     

    elif oct_pitch > 0:     # + 書かれている場合
        while base_note < last_pitch: base_note += 12
        if oct_pitch > 12: base_note += (oct_pitch-12)
        base_pitch = base_note

    else:                   # - 書かれている場合
        while base_note > last_pitch: base_note -= 12
        if oct_pitch < -12: base_note -= (oct_pitch+12)
        base_pitch = base_note

    return base_pitch


def convert_doremi_1(doremi, last_pitch):
    if len(doremi) == 0: return nlib.NO_NOTE
    base_pitch = 0
    while len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'x': return nlib.NO_NOTE
        elif l0 == '+': base_pitch += 12
        elif l0 == '-': base_pitch -= 12
        else: break
        doremi = doremi[1:]

    if len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'd': base_pitch += 0
        elif l0 == 'r': base_pitch += 2
        elif l0 == 'm': base_pitch += 4
        elif l0 == 'f': base_pitch += 5
        elif l0 == 's': base_pitch += 7
        elif l0 == 'l': base_pitch += 9
        elif l0 == 't': base_pitch += 11
        else: return nlib.NO_NOTE
    else: return nlib.NO_NOTE
    doremi = doremi[1:]

    if len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'i': base_pitch += 1
        elif l0 == 'a': base_pitch -= 1
    return base_pitch


def convert_doremi_0(doremi):
    if len(doremi) == 0: return nlib.NO_NOTE
    base_pitch = 0
    solfa = True
    while len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'x': return nlib.NO_NOTE
        elif l0 == 'i': return base_pitch+1
        elif l0 == 'a': return base_pitch-1
        elif l0 == '+': base_pitch += 12
        elif l0 == '-': base_pitch -= 12
        elif solfa:
            if   l0 == 'd': base_pitch += 0
            elif l0 == 'r': base_pitch += 2
            elif l0 == 'm': base_pitch += 4
            elif l0 == 'f': base_pitch += 5
            elif l0 == 's': base_pitch += 7
            elif l0 == 'l': base_pitch += 9
            elif l0 == 't': base_pitch += 11
            solfa = False
        doremi = doremi[1:]
    return base_pitch


def convert_doremi(doremi, last_pitch):
    return convert_doremi_2(doremi, last_pitch)


#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
class TextParse:

    def __init__(self):
        pass

    #------------------------------------------------------------------------------
    #   Phrase の省略されたノートを補填せよ
    def _fill_note_data1(nd):
        # ,| のみの入力による、休符指示の補填
        fill = ''
        doremi = 'x'
        doremi_end_flag = True
        for i in range(len(nd)):
            ltr = nd[i]
            if ltr == ',':
                fill += doremi + ','
                doremi = 'x'
                doremi_end_flag = True
            elif ltr == '|' or ltr == '/':
                fill += doremi + '|,'
                doremi = 'x'
                doremi_end_flag = True
            else:
                if doremi_end_flag:
                    doremi = ltr
                else:
                    doremi += ltr
                doremi_end_flag = False
        if doremi != '':
            fill += doremi
        return fill

    def _fill_note_data2(nf, no_repeat):
        # : :| による同フレーズの展開 -> 仕様削除
        '''
        repeat_start = 0
        for i, nt in enumerate(nf):  # |: :n|
            if ':' in nt:
                no_repeat = False
                locate = nt.find(':')
                if locate == 0:
                    nf[i] = nt[1:]
                    repeat_start = i
                else:
                    repeat_count = 0
                    num = nt.rfind(':') - len(nt)
                    nf[i] = nt[0:num]
                    if num == -1:
                        repeat_count = 1
                    else:
                        if nt[num + 1:].isdecimal():
                            repeat_count = int(nt[num + 1:])
                    repeat_end_ptr = i + 1
                    for j in range(repeat_count):
                        ins_ptr = repeat_end_ptr + j * (repeat_end_ptr - repeat_start)
                        nf[ins_ptr:ins_ptr] = nf[repeat_start:repeat_end_ptr]
                    break
        # end of for
        '''
        return nf, no_repeat


    def _fill_note_data3(nf, no_repeat):
        # < >*n による同フレーズの展開
        repeat_start = 0
        first_bracket = False
        for i, nt in enumerate(nf):  # <  >*n
            if '<' in nt:
                no_repeat = False
                locate = nt.find('<')
                if locate == 0:
                    nf[i] = nt[1:]
                    repeat_start = i
                    first_bracket = True
            elif '>' in nt:
                repeat_count = 0
                re_cnt = nt.rfind('>')
                nf[i] = nt[0:re_cnt]
                if nt[re_cnt + 1:re_cnt + 2] == '*' and first_bracket is True:
                    if nt[re_cnt + 2:].isdecimal():
                        repeat_count = int(nt[re_cnt + 2:])
                    if repeat_count > 1:
                        repeat_end_ptr = i + 1
                        for j in range(repeat_count - 1):
                            ins_ptr = repeat_end_ptr + j * (repeat_end_ptr - repeat_start)
                            nf[ins_ptr:ins_ptr] = nf[repeat_start:repeat_end_ptr]
                break
        # end of for
        return nf, no_repeat

    def _fill_note_data4(nf, no_repeat):
        # d*4 のような同音連打
        for i, nt in enumerate(nf):
            if '*' in nt:
                no_repeat = False
                locate = nt.find('*')
                nf[i] = nt[0:locate]
                repeat_count = 0
                if nt[locate + 1:].isdecimal():
                    repeat_count = int(nt[locate + 1:])
                if repeat_count > 1:
                    for j in range(repeat_count - 1):
                        nf.insert(i + 1, nt[0:locate])
                break
        # end of for
        return nf, no_repeat


    def _fill_omitted_note_data(note_data):
        ## ,| 重複による同音指示の補填
        fill = TextParse._fill_note_data1(note_data)

        # スペース削除し、',' 区切りでリスト化
        note_flow = re.split('[,]', fill)
        while '' in note_flow:  # 何も入ってない要素を削除
            note_flow.remove('')

        # If find Repeat mark, expand all event.
        no_repeat = False
        while not no_repeat:
            no_repeat = True
            note_flow, no_repeat = TextParse._fill_note_data2(note_flow, no_repeat)
            note_flow, no_repeat = TextParse._fill_note_data3(note_flow, no_repeat)
        # end of while

        # Same note repeat
        no_repeat = False
        while not no_repeat:
            no_repeat = True
            note_flow, no_repeat = TextParse._fill_note_data4(note_flow, no_repeat)
        # end of while

        return note_flow, len(note_flow)


    #------------------------------------------------------------------------------
    #   combine by '+'
    def _attached_to_noteinfo(block, delimiter_str, dur):
        # + で連結された一つ一つの attached_bracket/brace を一つにまとめる
        # dur: ２番目が duration かどうか？
        note_info = []
        total_block = len(block)    # + で繋がれた data block 数
        total_ninfo = len(block[0]) # 最初の raw データ内の [] の数に合わせる

        # note
        dtstr = ''
        for i in range(total_block):
            delimiter = delimiter_str if dtstr != '' else ''
            dtstr += delimiter + block[i][0]
        note_info.append(dtstr)

        # duration
        if total_ninfo >= 2 and dur:
            dtstr = block[0][1]
            dtstr_list = dtstr.split(':')
            durstr = dtstr_list[0]
            for i in range(1,total_block):
                if len(block[i]) >= 2:
                    durstr += ',' + block[i][1].split(':')[0]
            durstr += ':' + dtstr_list[1]
            note_info.append(durstr)

        # exp.
        exp_index = 2           # brace
        if dur: exp_index = 3   # bracket
        if total_ninfo >= exp_index:
            exstr = ''
            for i in range(total_block):
                if len(block[i]) >= exp_index:
                    comma = ',' if exstr != '' else ''
                    exstr += comma + block[i][exp_index-1]
            note_info.append(exstr)

        return note_info


    #------------------------------------------------------------------------------
    #   recognize [] set
    def complement_bracket(tx):
        # [] のセットを抜き出し、中身を attached_bracket/note_info に入れる
        num = tx.find('[')
        tx = tx[num:].strip()

        note_info = []
        attached_bracket = []
        while True:
            num = tx.find(']')
            if num == -1: # 見つからなかった時
                break
            note_info.append(tx[1:num])
            tx = tx[num+1:].strip()
            if len(tx) == 0:
                break
            if tx[0:2] == '+[':
                attached_bracket.append(copy.copy(note_info))
                note_info.clear()
                tx = tx[1:]
                continue
            if tx[0] != '[':
                break

        # 連結データ(attached_block)があった時の処理
        if attached_bracket and note_info:
            attached_bracket.append(note_info) # 最後の note_info を追加
            note_info = TextParse._attached_to_noteinfo(attached_bracket, '|', True)

        # [] の数が 1,2 の時は中身を補填
        bracket_num = len(note_info)
        if bracket_num == 1:
            note_info.append('raw') # set default exp. value
        elif bracket_num == 0 or bracket_num > 2:
            # [] の数が 1〜2 以外ならエラー
            return None, 0

        # 戻り値の生成
        complement = []
        base_note = 4
        dt, num = TextParse._fill_omitted_note_data(note_info[0])
        complement.append(dt)
        complement.append(note_info[1])
        return complement, base_note


    #------------------------------------------------------------------------------
    #   complement data for Composition
    def _fill_omitted_chord_data(chord_data):
        ## ,| 重複による同音指示の補填
        fill1 = ''
        doremi = ''
        doremi_end_flag = False
        for i in range(len(chord_data)):
            ltr = chord_data[i]
            if ltr == ',':
                fill1 += doremi + ','
                doremi_end_flag = True
            elif ltr == '|':
                fill1 += doremi + '|,'
                #doremi = ''
                doremi_end_flag = True
            else:
                if doremi_end_flag:
                    doremi = ltr
                else:
                    doremi += ltr
                doremi_end_flag = False
        if doremi != '':
            fill1 += doremi

        # スペース削除し、',' 区切りでリスト化
        chord_flow = re.split('[,]', fill1)
        while '' in chord_flow:  # 何も入ってない要素を削除
            chord_flow.remove('')
        return chord_flow


    def complement_brace(tx):
        # [] のセットを抜き出し、中身を attached_brace/note_info に入れる
        num = tx.find('{')
        tx = tx[num:].strip()

        note_info = []
        attached_brace = []
        while True:
            num = tx.find('}')
            if num == -1:
                break
            note_info.append(tx[1:num])
            tx = tx[num+1:].strip()
            if len(tx) == 0:
                break
            if tx[0:2] == '+{':
                attached_brace.append(copy.copy(note_info))
                note_info.clear()
                tx = tx[1:]
                continue
            if tx[0:1] != '{':
                break

        # 連結データ(attached_block)があった時の処理
        if attached_brace and note_info:
            attached_brace.append(note_info) # 最後の note_info を追加
            note_info = TextParse._attached_to_noteinfo(attached_brace, '|', False)

        exp = []
        if len(note_info) != 0:
            chord_flow_next = TextParse._fill_omitted_chord_data(note_info[0])
            if len(note_info) == 2:
                exp = note_info[1]
        else:
            return [], []
        return chord_flow_next, exp


    #------------------------------------------------------------------------------
    #   recombine data: カンマで区切られた単位の階名テキスト解析
    def _add_dur_info(nt):
        dur = 1
        if len(nt) > 0 and nt[-1] == 'o':
            nt = nt[0:-1]
            dur = nlib.FULL
        else:
            ext_str = nt
            while len(ext_str) > 0 and (ext_str[-1] == '.' or ext_str[-1] == '~'):
                dur += 1
                ext_str = ext_str[0:-1]
            if len(ext_str) == 0: dur -= 1  # '.~' しか存在しなかった
            nt = ext_str 
        return nt, dur


    def _cnv_note_to_pitch(keynote, note_text, last_note):
        end = False
        if note_text[-1] == '|':   # 小節最後のイベント
            note_text = note_text[0:-1]
            end = True
        note_text, dur = TextParse._add_dur_info(note_text)
        nlists = note_text.replace(' ', '').split('=')  # 和音検出
        bpchs = []
        for nx in nlists:
            doremi = convert_doremi(nx, last_note)
            base_pitch = keynote + doremi if doremi != nlib.NO_NOTE else doremi
            bpchs.append(base_pitch)
        return bpchs, end, dur, doremi


    #------------------------------------------------------------------------------
    #   recombine: Phrase を内部フォーマットに再構築せよ
    def _cnv_exp(dur_text):
        splited_txt = dur_text.replace(' ', '').split(',')
        exps = []
        vel = nlib.END_OF_DATA
        for exp in splited_txt:
            vel = convert_exp2vel(exp)
            if vel == nlib.END_OF_DATA:
                exps.append(exp)
        if vel == nlib.END_OF_DATA:
            vel = nlib.DEFAULT_VEL
        return vel, exps


    def _add_note(generated, tick, notes, real_dur, velocity=100):
        if len(notes) != 0:
            for note in notes:
                if note == nlib.REST:
                    print('error')
                elif note == nlib.NO_NOTE:  # '=' による和音入力時
                    same_tick = generated[-1][1]
                    cnt = 0
                    while True:
                        if len(generated) <= cnt: break
                        cnt += 1
                        if generated[-cnt][1] == same_tick:
                            generated[-cnt][2] += real_dur
                        else: break
                else:
                    generated.append(['note', tick, real_dur, note, velocity])  # add real_dur
        else:
            print('error!')


    def recombine_to_internal_format(complement, keynote, tick_for_onemsr, base_note):
        if complement is None or len(complement[0]) == 0:
            return 0, [], []

        expvel, others = TextParse._cnv_exp(complement[1])
        last_nt = 5 # d-t が同じオクターブで始まる値
        tick = 0
        msr = 1
        read_ptr = 0
        rcmb = []
        note_cnt = len(complement[0])
        while read_ptr < note_cnt:
            notes, mes_end, dur, nt = TextParse._cnv_note_to_pitch(keynote, complement[0][read_ptr], last_nt)
            if nt != nlib.NO_NOTE: last_nt = nt    # 次回の音程の上下判断のため
            if tick < tick_for_onemsr*msr:
                if dur == nlib.FULL:   # o があった場合
                    real_dur = tick_for_onemsr*msr-tick
                else:
                    real_dur = math.floor(dur * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note)
                TextParse._add_note(rcmb, tick, notes, real_dur, expvel)
                tick += real_dur #int(dur * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note)
            if mes_end:     # 小節線があった場合
                tick = msr*tick_for_onemsr
                msr += 1
            read_ptr += 1  # out from repeat

        return tick, rcmb, others


    #------------------------------------------------------------------------------
    #   recombine: chord データを内部データに再構築せよ
    def recombine_to_chord_loop(complement, tick_for_onemsr, tick_for_onebeat):
        if complement is None or len(complement) == 0:
            return 0, []

        tick = 0
        msr = 1
        read_ptr = 0
        rcmb = []
        same_chord = ''
        note_cnt = len(complement)
        while read_ptr < note_cnt:
            mes_end = False
            chord = complement[read_ptr]
            if chord[-1] == '|':
                mes_end= True
                chord = chord[0:-1]
            if tick < tick_for_onemsr*msr:
                adjust_tick = tick              # 途中拍で和音が変わる時、音が変わらない暫定対策
                if tick != 0: adjust_tick -= 1  # 
                if same_chord != chord:
                    same_chord = chord
                    rcmb.append(['chord', adjust_tick, chord])
                tick += tick_for_onebeat
            if mes_end:
                tick = msr*tick_for_onemsr
                msr += 1
            read_ptr += 1  # out from repeat

        tick = msr*tick_for_onemsr
        return tick, rcmb


    #------------------------------------------------------------------------------
    #   translate note
    def detect_chord_scale(chord):
        root = 0
        letter = chord[0]
        dtbl = nlib.CHORD_SCALE['diatonic']
        if letter == 'I' or letter == 'V':
            root_cnt = 0
            root_str = ''
            while letter == 'I' or letter == 'V':
                root_str += letter
                root_cnt += 1
                if len(chord) > root_cnt:
                    letter = chord[root_cnt]
                else:
                    break
            # #/b のチェック
            if letter == '#':
                root += 1
                root_cnt += 1
            elif letter == 'b':
                root -= 1
                root_cnt += 1
            # ローマ数字の文字列から root を求める
            try:
                ofs = nlib.ROOT_NAME.index(root_str)
                root += dtbl[ofs]
            except ValueError as error:
                root = 0
            
            if len(chord) > root_cnt:
                chord = '_' + chord[root_cnt:]
            else:
                chord = '_'

        chord_scale_tbl = nlib.CHORD_SCALE.get(chord, dtbl)
        return root, chord_scale_tbl
