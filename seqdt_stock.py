# -*- coding: utf-8 -*-
import math
import lpnlib as nlib
import expfilter_beat as efb
import lpntxt as tx

#### 入力テキストデータの変換処理を集約するクラス
class PartDataStock:

    def __init__(self, objs, seq):
        self.raw = None
        self.complement = None
        self.generated = None
        self.randomized = None

        self.seq = seq
        self.ptr = objs
        self.ptr.set_seqdt_part(self)

        self.whole_tick = 0
        self.base_note = 0
        self.note_cnt = 0


    def _add_note(self, generated, tick, notes, duration, base_note, velocity=100):
        for note in notes:
            if note != nlib.REST:
                real_dur = math.floor(duration * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note) # add line
                generated.append(['note', tick, real_dur, note, velocity])                      # add real_dur


    def _cnv_note_to_pitch(keynote, note_text):
        nlists = note_text.replace(' ', '').split('=')  # 和音検出
        bpchs = []
        for nx in nlists:
            base_pitch = keynote + nlib.convert_doremi(nx)
            bpchs.append(base_pitch)
        return bpchs


    def _cnv_duration(dur_text):
        if dur_text.isdecimal() is True:
            return int(dur_text)
        else:
            return 1


    def convert_to_internal_format(self, base_note, note_cnt):
        if self.complement[0] is None or len(self.complement[0]) == 0:
            return 0, []

        tick = 0
        read_ptr = 0
        cmpl = []
        while read_ptr < note_cnt:
            notes = PartDataStock._cnv_note_to_pitch(self.ptr.keynote, self.complement[0][read_ptr])
            dur = PartDataStock._cnv_duration(self.complement[1][read_ptr])
            vel = nlib.convert_exp2vel(self.complement[2])
            self._add_note(cmpl, tick, notes, dur, base_note, vel)
            tick += int(dur * nlib.DEFAULT_TICK_FOR_ONE_MEASURE / base_note)
            read_ptr += 1  # out from repeat

        return tick, cmpl


    def set_generated(self):
        if self.complement == None: return

        # 3.generated data
        self.whole_tick, self.generated = self.convert_to_internal_format(self.base_note, self.note_cnt)
        print('generated1:',self.generated)
        ### Add Filters
        self.generated = efb.BeatFilter().filtering(self.generated, self.seq.bpm, self.seq.tick_for_onemsr)
        print('generated2:',self.generated)
        self.ptr.update_phrase()


    def set_raw(self, text):
        # 1. raw
        self.raw = text

        # 2.complement data
        cmpl, self.base_note, self.note_cnt = tx.TextParse._complement_data(text)   # リスト [3] = [note[],dur[],exp]
        print('complement:',cmpl)
        if cmpl != None:
            self.complement = cmpl
        else:
            return False

        # 3.generated data
        self.set_generated()

        return True


    def get_final(self):
        if self.generated == None: return 0,[]

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
        self.ptr.set_seqdt_part(self)
        self.ptr.update_phrase()    # always

    def set_raw(self, text):
        pass

    def set_generated(self):
        pass

    def get_final(self):
        return 1920, [['damper',40,1870,127]]


class CompositionPartStock:

    def __init__(self, objs, seq):
        self.seq = seq
        self.ptr = objs
        self.ptr.set_seqdt_part(self)

        self.raw = []
        self.complement = []
        self.generated = ['chord',0,'thru']

        self.whole_tick = 0

    def set_raw(self, text):
        # 1. raw
        self.raw = text

        # 2.complement data
        cmpl = tx.TextParse.complement_brace(text)
        if cmpl != None:
            self.complement = cmpl
        else:
            return False
        self.ptr.update_phrase()

        # 3. generated data
        self.set_generated()
        return True


    def set_generated(self):
        # 3. generated
        self.generated = []
        self.whole_tick = 0
        for cd in self.complement:
            self.generated.append(['chord', self.whole_tick, cd])
            self.whole_tick += 1920

    def get_final(self):
        return self.whole_tick, self.generated


class SeqDataAllStock:

    def __init__(self, seq):
        self.part_data = []
        self.seq = seq
        for i in range(nlib.MAX_NORMAL_PART):
            pdt = PartDataStock(seq.get_part(i), seq)
            self.part_data.append(pdt)

        # Damper Pedal Part
        self.damper_part = DamperPartStock(seq.get_part(nlib.DAMPER_PEDAL_PART), seq)

        # Composition Part
        self.composition_part = CompositionPartStock(seq.get_part(nlib.COMPOSITION_PART), seq)


    def set_raw(self, part, text):
        if part >= nlib.MAX_NORMAL_PART: return False
        if self.part_data[part].ptr == None: return False
        return self.part_data[part].set_raw(text)

    def set_raw_for_composition(self, text):
        self.composition_part.set_raw(text)

    def set_generated(self):
        self.composition_part.set_generated()
        self.damper_part.set_generated()
        for part in self.part_data:
            part.set_generated()
