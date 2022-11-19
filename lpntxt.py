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

    if len(doremi) == 0: return nlib.REST
    oct_pitch = 0
    while len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'x': return nlib.REST
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
        else: return nlib.REST
    else: return nlib.REST
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
    if len(doremi) == 0: return nlib.REST
    base_pitch = 0
    while len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'x': return nlib.REST
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
        else: return nlib.REST
    else: return nlib.REST
    doremi = doremi[1:]

    if len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'i': base_pitch += 1
        elif l0 == 'a': base_pitch -= 1
    return base_pitch


def convert_doremi_0(doremi):
    if len(doremi) == 0: return nlib.REST
    base_pitch = 0
    solfa = True
    while len(doremi) != 0:
        l0 = doremi[0]
        if   l0 == 'x': return nlib.REST
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
    #   基準音価を変更せよ
    def _change_basic_note_dur(dur_text):
        base_note = 4
        # コロンで設定されている基本音価を調査し、tickに変更
        if ':' in dur_text:
            sp_txt = dur_text.split(':')
            base_note_text = '4'
            # 基本音価はコロンの前か後か？
            if (',' in sp_txt[0]) or ('(' and ')' in sp_txt[1]):
                dur_text = sp_txt[0]
                base_note_text = sp_txt[1]
            elif (',' in sp_txt[1]) or ('(' and ')' in sp_txt[0]):
                base_note_text = sp_txt[0]
                dur_text = sp_txt[1]
            elif sp_txt[0] == '':
                dur_text = '1'
                base_note_text = sp_txt[1]
            elif sp_txt[0].isdecimal() and sp_txt[1].isdecimal() and int(sp_txt[0]) < int(sp_txt[1]):
                dur_text = sp_txt[0]
                base_note_text = sp_txt[1]
            else:
                base_note_text = sp_txt[0]
                dur_text = sp_txt[1]

##            if '(' and ')' in base_note_text:
##                percent = re.findall("(?<=\().+?(?=\))", base_note_text)
##                if '%' in percent[0]:
##                    per = percent[0].strip('%')
##                    if per.isdecimal() is True and int(per) <= 100:
##                        self.durPer = int(per)  # % の数値
##                elif percent[0] == 'stacc.':
##                    self.durPer = 50
            dur_len = re.sub("\(.+?\)", "", base_note_text)
            if dur_len.isdecimal() is True:
                base_note = int(dur_len)

        return dur_text, base_note


    #------------------------------------------------------------------------------
    #   省略された duration を戻せ
    def _fill_omitted_dur_data(dur_text, note_num):
        dur_flow = []
        if ',' in dur_text:
            dur_flow = re.split('[,|]', dur_text.replace(' ', ''))
        else:
            # ','が無い場合、全体を一つの文字列にし、リストとして追加
            dur_flow.append(dur_text)

        no_repeat = False
        while not no_repeat:
            no_repeat = True
            repeat_start = 0
            first_bracket = False
            for i, dur in enumerate(dur_flow):  # <  >*n
                if '<' in dur:
                    no_repeat = False
                    locate = dur.find('<')
                    if locate == 0:
                        dur_flow[i] = dur[1:]
                        repeat_start = i
                        first_bracket = True
                elif '>' in dur:
                    re_cnt = dur.rfind('>')
                    dur_flow[i] = dur[0:re_cnt]
                    if dur[re_cnt + 1:re_cnt + 2] == '*' and first_bracket is True:
                        repeat_count = 0
                        if dur[re_cnt + 2:].isdecimal():
                            repeat_count = int(dur[re_cnt + 2:])
                        if repeat_count > 1:
                            repeat_end_ptr = i + 1
                            for j in range(repeat_count - 1):
                                ins_ptr = repeat_end_ptr + j * (repeat_end_ptr - repeat_start)
                                dur_flow[ins_ptr:ins_ptr] = dur_flow[repeat_start:repeat_end_ptr]
                    elif i + 1 == len(dur_flow) and first_bracket is True:
                        cntr = 0
                        while True:
                            dur_flow.append(dur_flow[repeat_start + cntr])
                            cntr += 1
                            if note_num <= len(dur_flow):
                                break
                    break
            # end of for
        # end of while

        dur_num = len(dur_flow)
        if dur_num < note_num:
            for _ in range(note_num - dur_num):
                dur_flow.append(dur_flow[dur_num - 1])  # 足りない要素を補填
        elif dur_num > note_num:
            del dur_flow[note_num:]  # 多い要素を削除
        return dur_flow


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
            note_info.append('1')   # set default value
            note_info.append('raw') # set default exp. value
        elif bracket_num == 2:
            note_info.append('raw') # set default exp. value
        elif bracket_num == 0 or bracket_num > 3:
            # [] の数が 1〜3 以外ならエラー
            return None, 0

        # [][][] が三つある状態
        complement = []
        dt, num = TextParse._fill_omitted_note_data(note_info[0])
        complement.append(dt)
        dur_text, base_note = TextParse._change_basic_note_dur(note_info[1])
        complement.append(TextParse._fill_omitted_dur_data(dur_text, num))
        complement.append(note_info[2])
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
    def _add_note_duration(nt):
        if len(nt) > 0 and nt[-1] == 'o':
            nt = nt[0:-1] + ':F'    # note の後ろに :F をつけると小節残り全部
        else:
            length = 1
            ext_str = nt
            while len(ext_str) > 0 and (ext_str[-1] == '.' or ext_str[-1] == '~'):
                length += 1
                ext_str = ext_str[0:-1] if len(ext_str) > 0 else ''
            nt = ext_str + ':' + str(length)    # 音価 :n 
        return nt


    def _add_note(generated, tick, notes, real_dur, velocity=100):
        for note in notes:
            if note != nlib.REST:
                generated.append(['note', tick, real_dur, note, velocity])  # add real_dur


    def _cnv_note_to_pitch(keynote, note_text, last_note):
        end = False
        if note_text[-1] == '|':   # 小節最後のイベント
            note_text = note_text[0:-1]
            end = True
        note_text = TextParse._add_note_duration(note_text)
        nlists = note_text.replace(' ', '').split('=')  # 和音検出
        bpchs = []
        for nx in nlists:
            doremi = convert_doremi(nx, last_note)
            base_pitch = keynote + doremi if doremi != nlib.REST else doremi
            bpchs.append(base_pitch)
        return bpchs, end, doremi


    #------------------------------------------------------------------------------
    #   recombine data: duration テキスト解析
    def _cnv_duration(dur_text):
        if dur_text.isdecimal() is True:
            return int(dur_text)
        else:
            return 1


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


    #------------------------------------------------------------------------------
    #   recombine 内部フォーマットに再構築せよ
    def recombine_to_internal_format(complement, keynote, tick_for_onemsr, base_note):
        if complement is None or len(complement[0]) == 0:
            return 0, [], []

        expvel, others = TextParse._cnv_exp(complement[2])
        last_nt = 5
        tick = 0
        msr = 1
        read_ptr = 0
        rcmb = []
        note_cnt = len(complement[0])
        while read_ptr < note_cnt:
            notes, mes_end, nt = TextParse._cnv_note_to_pitch(keynote, complement[0][read_ptr], last_nt)
            if nt != nlib.REST: last_nt = nt
            dur = TextParse._cnv_duration(complement[1][read_ptr])
            if tick < tick_for_onemsr*msr:
                real_dur = math.floor(dur * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note) # add line
                TextParse._add_note(rcmb, tick, notes, real_dur, expvel)
                tick += real_dur #int(dur * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note)
            if mes_end:
                tick = msr*tick_for_onemsr
                msr += 1
            read_ptr += 1  # out from repeat

        return tick, rcmb, others


    #------------------------------------------------------------------------------
    #   recombine data for chord
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
