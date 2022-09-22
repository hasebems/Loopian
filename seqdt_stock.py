# -*- coding: utf-8 -*-
import re
import math
import lpnlib as nlib
import expfilter_beat as efb

#### 入力テキストデータの変換処理を集約するクラス
class PartDataStock:

    def __init__(self, objs, seq):
        self.raw = None
        self.complement = None
        self.generated = None
        self.randomized = None

        self.seq = seq
        self.ptr = objs
        self.ptr.set_gendt_part(self)

        self.whole_tick = 0
        self.base_note = 0
        self.note_cnt = 0

    @staticmethod
    def _fill_omitted_note_data(note_data):
        # スペース削除し、',' '|' 区切りでリスト化
        note_flow = re.split('[,|]', note_data.replace(' ', ''))
        while '' in note_flow:
            note_flow.remove('')

        # If find Repeat mark, expand all event.
        no_repeat = False
        while not no_repeat:
            no_repeat = True
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

    @staticmethod
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


    @staticmethod
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


    @staticmethod
    def _complement_data(input_text):
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
            return None

        complement = []
        dt, num = PartDataStock._fill_omitted_note_data(note_info[0])
        complement.append(dt)
        dur_text, base_note = PartDataStock._change_basic_note_dur(note_info[1])
        complement.append(PartDataStock._fill_omitted_dur_data(dur_text, num))
        complement.append(note_info[2])

        return complement, base_note, num


    def _cnv_note_to_pitch(self, note_text):
        nlists = note_text.replace(' ', '').split('=')  # 和音検出
        bpchs = []
        for nx in nlists:
            base_pitch = self.ptr.keynote + nlib.convert_doremi(nx)
            bpchs.append(base_pitch)
        return bpchs


    @staticmethod
    def _cnv_duration(dur_text):
        if dur_text.isdecimal() is True:
            return int(dur_text)
        else:
            return 1


    def _add_note(self, generated, tick, notes, duration, base_note, velocity=100):
        for note in notes:
            if note != nlib.REST:
                real_dur = math.floor(duration * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note) # add line
                generated.append(['note', tick, real_dur, note, velocity])                      # add real_dur


    def convert_to_MIDI_like_format(self, base_note, note_cnt):
        if self.complement[0] is None or len(self.complement[0]) == 0:
            return 0, []

        tick = 0
        read_ptr = 0
        generated = []
        while read_ptr < note_cnt:
            notes = self._cnv_note_to_pitch(self.complement[0][read_ptr])
            dur = self._cnv_duration(self.complement[1][read_ptr])
            vel = nlib.convert_exp2vel(self.complement[2])
            self._add_note(generated, tick, notes, dur, base_note, vel)
            tick += int(dur * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note)
            read_ptr += 1  # out from repeat

        return tick, generated


    def set_raw(self, text):
        # 1. raw
        self.raw = text

        # 2.complement data
        cmpl, self.base_note, self.note_cnt = self._complement_data(text)   # リスト [3] = [note[],dur[],exp]
        print('complement:',cmpl)
        if cmpl != None:
            self.complement = cmpl
        else:
            return False

        # 3.generated data
        self.set_generated()

        return True


    def set_generated(self):
        if self.complement == None: return

        # 3.generated data
        self.whole_tick, self.generated = self.convert_to_MIDI_like_format(self.base_note, self.note_cnt)
        print('generated1:',self.generated)
        ### Add Filters
        self.generated = efb.BeatFilter().filtering(self.generated, self.seq.bpm, self.seq.tick_for_onemsr)
        print('generated2:',self.generated)
        self.ptr.update_phrase()


    def get_final(self):
        # 4. randomized data
        self.randomized = []
        for dt in self.generated:
            dt[nlib.VEL] += int(nlib.gauss_rnd10())
            if dt[nlib.VEL] > 127: dt[nlib.VEL] = 127
            elif dt[nlib.VEL] < 1: dt[nlib.VEL] = 1
            self.randomized.append(dt)

        return self.whole_tick, self.randomized


class DamperPartStock:

    def __init__(self, objs, seq):
        self.seq = seq
        self.ptr = objs
        self.ptr.set_gendt_part(self)
        self.ptr.update_phrase()    # always

    def get_final(self):
        return 1920, [['damper',40,1870,127]]

class SeqDataStock:

    def __init__(self, seq):
        self.part_data = [] #[PartDataStock() for _ in range(nlib.MAX_PART_COUNT)]
        self.seq = seq
        for i in range(nlib.MAX_PART_COUNT-1):
            pdt = PartDataStock(seq.sqobjs[i], seq)
            self.part_data.append(pdt)

        # Damper Pedal Part
        self.part_data.append(DamperPartStock(seq.sqobjs[nlib.MAX_PART_COUNT-1], seq))

    def set_raw(self, part, text):
        if part >= nlib.MAX_PART_COUNT-1: return False
        if self.part_data[part].ptr == None: return False
        return self.part_data[part].set_raw(text)

    def set_generated(self):
        for part in self.part_data:
            part.set_generated()
