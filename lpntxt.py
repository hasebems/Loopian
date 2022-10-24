# -*- coding: utf-8 -*-
import re
import math
import lpnlib as nlib


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


class TextParse:

    def __init__(self):
        pass

    #------------------------------------------------------------------------------
    #   complement data
    def _fill_omitted_note_data(note_data):
        ## ,| 重複による同音指示の補填
        fill1 = ''
        doremi = ''
        ntstr_end_flag = False
        for i in range(len(note_data)):
            ltr = note_data[i]
            if ltr == ',':
                fill1 += doremi + ','
                ntstr_end_flag = True
            elif ltr == '|':
                fill1 += doremi + '|,'
                doremi = ''
                ntstr_end_flag = True
            else:
                if ntstr_end_flag:
                    doremi = ltr
                else:
                    doremi += ltr
                ntstr_end_flag = False
        if doremi != '':
            fill1 += doremi

        # スペース削除し、',' 区切りでリスト化
        fill2 = fill1.replace(' ', '').replace('|','|,')
        note_flow = re.split('[,]', fill2)
        while '' in note_flow:  # 何も入ってない要素を削除
            note_flow.remove('')

        # If find Repeat mark, expand all event.
        no_repeat = False
        while not no_repeat:
            no_repeat = True
            '''
            repeat_start = 0
            for i, nt in enumerate(note_flow):  # |: :n|
                if ':' in nt:
                    no_repeat = False
                    locate = nt.find(':')
                    if locate == 0:
                        note_flow[i] = nt[1:]
                        repeat_start = i
                    else:
                        repeat_count = 0
                        num = nt.rfind(':') - len(nt)
                        note_flow[i] = nt[0:num]
                        if num == -1:
                            repeat_count = 1
                        else:
                            if nt[num + 1:].isdecimal():
                                repeat_count = int(nt[num + 1:])
                        repeat_end_ptr = i + 1
                        for j in range(repeat_count):
                            ins_ptr = repeat_end_ptr + j * (repeat_end_ptr - repeat_start)
                            note_flow[ins_ptr:ins_ptr] = note_flow[repeat_start:repeat_end_ptr]
                        break
            # end of for
            '''
            repeat_start = 0
            first_bracket = False
            for i, nt in enumerate(note_flow):  # <  >*n
                if '<' in nt:
                    no_repeat = False
                    locate = nt.find('<')
                    if locate == 0:
                        note_flow[i] = nt[1:]
                        repeat_start = i
                        first_bracket = True
                elif '>' in nt:
                    repeat_count = 0
                    re_cnt = nt.rfind('>')
                    note_flow[i] = nt[0:re_cnt]
                    if nt[re_cnt + 1:re_cnt + 2] == '*' and first_bracket is True:
                        if nt[re_cnt + 2:].isdecimal():
                            repeat_count = int(nt[re_cnt + 2:])
                        if repeat_count > 1:
                            repeat_end_ptr = i + 1
                            for j in range(repeat_count - 1):
                                ins_ptr = repeat_end_ptr + j * (repeat_end_ptr - repeat_start)
                                note_flow[ins_ptr:ins_ptr] = note_flow[repeat_start:repeat_end_ptr]
                    break
            # end of for
        # end of while

        # Same note repeat
        no_repeat = False
        while not no_repeat:
            no_repeat = True
            for i, nt in enumerate(note_flow):
                if '*' in nt:
                    no_repeat = False
                    locate = nt.find('*')
                    note_flow[i] = nt[0:locate]
                    repeat_count = 0
                    if nt[locate + 1:].isdecimal():
                        repeat_count = int(nt[locate + 1:])
                    if repeat_count > 1:
                        for j in range(repeat_count - 1):
                            note_flow.insert(i + 1, nt[0:locate])
                    break
            # end of for
        # end of while

        return note_flow, len(note_flow)


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


    def complement_data(input_text):
        # [] のセットを抜き出し、中身を note_info に入れる
        note_info = []
        tx = input_text
        while True:
            num = tx.find(']')  # 見つからなかった時
            if num == -1:
                break
            note_info.append(tx[1:num])
            tx = tx[num + 1:].strip()
            if len(tx) == 0:
                break
            if tx[0:1] != '[':
                break

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

        complement = []
        dt, num = TextParse._fill_omitted_note_data(note_info[0])
        complement.append(dt)
        dur_text, base_note = TextParse._change_basic_note_dur(note_info[1])
        complement.append(TextParse._fill_omitted_dur_data(dur_text, num))
        complement.append(note_info[2])
        return complement, base_note


    def complement_brace(input_text):
        # {} のセットを抜き出し、中身を note_info に入れる
        note_info = []
        exp = []
        tx = input_text
        while True:
            num = tx.find('}')
            if num == -1:
                break
            note_info.append(tx[1:num])
            tx = tx[num + 1:].strip()
            if len(tx) == 0:
                break
            if tx[0:1] != '{':
                break

        if len(note_info) != 0:
            if ',' in note_info[0]:
                chord_flow_next = note_info[0].strip().split(',') # chord
            else:
                chord_flow_next = note_info
            if len(note_info) == 2:
                exp = note_info[1]
        else:
            # if no ':', set 'all" pattern
            chord_flow_next = []
        return chord_flow_next, exp


    #------------------------------------------------------------------------------
    #   recombine data
    def _add_note(generated, tick, notes, real_dur, velocity=100):
        for note in notes:
            if note != nlib.REST:
                generated.append(['note', tick, real_dur, note, velocity])                      # add real_dur


    def _cnv_note_to_pitch(keynote, note_text):
        end = False
        if note_text[-1] == '|':   # 小節最後のイベント
            note_text = note_text[0:-1]
            end = True
        nlists = note_text.replace(' ', '').split('=')  # 和音検出
        bpchs = []
        for nx in nlists:
            doremi = nlib.convert_doremi(nx)
            base_pitch = keynote + doremi if doremi != nlib.REST else doremi
            bpchs.append(base_pitch)
        return bpchs, end


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


    def recombine_to_internal_format(complement, keynote, tick_for_onemsr, base_note):
        if complement is None or len(complement[0]) == 0:
            return 0, [], []

        expvel, others = TextParse._cnv_exp(complement[2])
        tick = 0
        msr = 1
        read_ptr = 0
        rcmb = []
        note_cnt = len(complement[0])
        while read_ptr < note_cnt:
            notes, mes_end = TextParse._cnv_note_to_pitch(keynote, complement[0][read_ptr])
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
