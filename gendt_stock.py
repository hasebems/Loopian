# -*- coding: utf-8 -*-
import lpnlib as nlib
import gendt_phrase as nph

#### 入力テキストデータの変換処理を集約するクラス
class PartDataStock:

    def __init__(self):
        self.raw = None
        self.complement = None
        self.generated = None
        self.random = None

        self.ptr = None
        self.whole_tick = 0

    @staticmethod
    def _complement_bracket(input_text):
        # [] のセットを抜き出し、中身を note_info に入れる
        note_info = []
        tx = input_text
        while True:
            num = tx.find(']')
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
            note_info.append('1')  # set default value
            note_info.append('100')
        elif bracket_num == 2:
            note_info.append('100')  # set default velocity value
        elif bracket_num == 0 or bracket_num > 3:
            # [] の数が 1〜3 以外ならエラー
            return None

        #note_info.insert(0, 'phrase')
        return note_info

    def set_raw(self, text):
        # 1. raw
        self.raw = text

        # 2.complement data
        cmpl = self._complement_bracket(text)
        if cmpl != None:
            self.complement = cmpl
            self.ptr.update_phrase()
        else:
            return False

        # 3.generated data
        pg = nph.PhraseGenerator(self.complement, self.ptr.keynote)
        self.whole_tick, self.generated = pg.convert_to_MIDI_like_format()

        return True

    def get_final(self):
        return self.whole_tick, self.generated


class SeqDataStock:

    def __init__(self):
        self.part_data = [PartDataStock() for _ in range(nlib.MAX_PART_COUNT)]

    def set_part_ptr(self, ptr, num):
        self.part_data[num].ptr = ptr

    def set_raw(self, part, text):
        if part >= nlib.MAX_PART_COUNT: return False
        if self.part_data[part].ptr == None: return False
        return self.part_data[part].set_raw(text)

    def get_final(self, part):
        if part >= nlib.MAX_PART_COUNT: return 0,None
        return self.part_data[part].get_final()
