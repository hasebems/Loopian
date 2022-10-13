# -*- coding: utf-8 -*-
import lpnlib as nlib
import expfilter_beat as efb
import lpntxt as tx
import copy

#------------------------------------------------------------------------------
#   Phrase の入力テキストの変換
class PhraseDataStock:

    def __init__(self, objs, seq):
        self.raw = None
        self.complement = None
        self.generated = None
        self.analysed = None        # no convert process
        self.randomized = None
        self.exps = []

        self.seq = seq
        self.part = objs
        self.part.set_seqdt_part(self)

        self.whole_tick = 0
        self.base_note = 0


    def _basic_analysis(generated):
        # make beat analysis data: 
        #       [   note count,           : in same tick
        #           tick, 
        #           dur, 
        #           [ all note num ]      : general purpose
        #       ]
        # 同tickの note を、一つのデータにまとめて beat_analysis に格納
        beat_analysis = []
        crnt_tick = -1
        crnt_dur = 0
        note_cnt = 0
        note_all = []
        for note in generated: # ['note', tick, dur, note, vel]
            if note[nlib.TICK] == crnt_tick: # 同じ tick なら、note_all に Note 追加
                note_cnt += 1
                note_all.append(note[3])
            else:                   # tick が進んだら、前の tick のデータを記録
                if note_cnt > 0:
                    beat_analysis.append([note_cnt, crnt_tick, crnt_dur, note_all])
                crnt_tick = note[nlib.TICK]
                crnt_dur = note[nlib.DUR]
                note_cnt = 1
                note_all = [note[3]]
        if note_cnt > 0: # add last one
            beat_analysis.append([note_cnt, crnt_tick, crnt_dur, note_all])
        return beat_analysis


    def _arp_translation(beat_analysis, option):
        # for arpeggio
        # 上記で準備した beat_analysis の後ろに、arpeggio 用の解析データを追加
        #  [ 'com'/'arp', $DIFF ]
        #       'arp': arpeggio 用 Note変換を発動させる（前の音と連続している）
        #       $DIFF: 上記が True の場合の、前の音との音程の差分
        last_note = nlib.REST   # 前回のノート
        last_cnt = 0            # 前回の同時発音数
        total_tick = 0          # 現在の Loop 内 tick 数
        for ana in beat_analysis:
            # total_tick の更新
            if total_tick != ana[nlib.TICK]: # 休みがあった
                total_tick = ana[nlib.TICK]
                last_note = nlib.REST       # arp にならない
                last_cnt = 0
            elif ana[nlib.DUR] >= 480:      # 今回、四分音符以上なら arp にならない
                total_tick = ana[nlib.TICK]
                last_note = nlib.REST
                last_cnt = 0
            else:
                total_tick += ana[nlib.DUR]

            # crnt_note の更新
            crnt_note = nlib.NO_NOTE
            crnt_cnt = ana[nlib.ARP_NTCNT]
            if crnt_cnt == 1:    # arp 対象
                crnt_note = ana[nlib.NOTE][0]

            # 条件の確認と、ana への情報追加
            if option == 'para':
                ana.append(['para'])
            elif last_note <= 127 and \
               last_cnt == 1 and \
               crnt_note <= 127 and \
               crnt_cnt == 1: # 過去＆現在：単音、ノート適正
                ana.append(['arp', crnt_note-last_note])
            else:
                ana.append(['com'])
            last_cnt = crnt_cnt
            last_note = crnt_note

        print('analysed:', beat_analysis)
        return beat_analysis


    def _analyse_plain_data(generated, exps):
        option = ''
        for exp in exps:
            if exp == 'para':
                option = 'para'
                break
        beat_analysis = PhraseDataStock._basic_analysis(generated)
        return PhraseDataStock._arp_translation(beat_analysis, option)


    def set_raw(self, text):
        # 1. raw
        self.raw = text

        # 2.complement data
        cmpl, self.base_note = tx.TextParse.complement_data(text)   # リスト [3] = [note[],dur[],exp]
        print('complement:',cmpl)
        if cmpl != None:
            self.complement = cmpl
        else:
            return False

        # 3-5.recombined data
        self.set_recombined()

        return True

    def set_recombined(self):
        # 3.recombined data
        self.whole_tick, self.generated, self.exps = \
            tx.TextParse.recombine_to_internal_format( \
                self.complement, self.part.keynote, self.seq.stock_tick_for_onemsr[0], self.base_note)
        print('recombined:',self.generated)

        # 4.analysed data
        self.analysed = PhraseDataStock._analyse_plain_data(self.generated, self.exps)

        # 5.humanized data
        ### Add Filters
        self.generated = efb.BeatFilter().filtering(self.generated, self.seq.bpm, self.seq.tick_for_onemsr)
        ### 

        print('humanized:',self.generated)
        self.part.update_phrase()


    def get_final(self):
        if self.generated == None: return 0,None,None

        # 6. randomized data
        ## temporary method
        self.randomized = []
        for dt in self.generated:
            dtx = copy.deepcopy(dt)
            vel = dt[nlib.VEL] + int(nlib.gauss_rnd10())
            if vel > 127: vel = 127
            elif vel < 1: vel = 1
            dtx[nlib.VEL] = vel
            self.randomized.append(dtx)

        return self.whole_tick, self.randomized, self.analysed


class DamperPartStock:

    def __init__(self, objs, seq):
        self.seq = seq
        self.part = objs
        self.part.set_seqdt_part(self)
        self.part.update_phrase()    # always

    def set_raw(self, text):
        return True

    def set_recombined(self):
        pass

    def get_final(self):
        return 1920, [['damper',40,1870,127]], None

#------------------------------------------------------------------------------
#   Composition の入力テキストの変換
class CompositionPartStock:

    def __init__(self, objs, seq):
        self.seq = seq
        self.part = objs
        self.part.set_seqdt_part(self)

        self.raw = []
        self.complement = []
        self.generated = ['chord',0,'thru']
        self.exp = []

        self.whole_tick = 0

    def set_raw(self, text):
        # 1. raw
        self.raw = text

        # 2.complement data
        cmpl, exp = tx.TextParse.complement_brace(text)
        if cmpl != None:
            self.complement = cmpl
            self.exp = exp
        else:
            return False
        self.part.update_phrase()

        # 3. recombined data
        self.set_recombined()
        return True


    def set_recombined(self):
        # 3. recombined
        self.generated = []
        self.whole_tick = 0
        for cd in self.complement:
            self.generated.append(['chord', self.whole_tick, cd])
            self.whole_tick += 1920

    def get_final(self):
        return self.whole_tick, self.generated, self.exp

#------------------------------------------------------------------------------
#   入力テキストデータの変換処理を集約するクラス
class SeqDataAllStock:

    def __init__(self, seq):
        self.composition_part = []
        self.part_data = []
        self.seq = seq

        # Composition Part
        for i in range(nlib.MAX_NORMAL_PART):
            pdt = CompositionPartStock(seq.get_part(i+nlib.FIRST_COMPOSITION_PART), seq)
            self.composition_part.append(pdt)

        # Normal Part
        for i in range(nlib.MAX_NORMAL_PART):
            pdt = PhraseDataStock(seq.get_part(i+nlib.FIRST_NORMAL_PART), seq)
            self.part_data.append(pdt)

        # Damper Pedal Part
        self.damper_part = DamperPartStock(seq.get_part(nlib.DAMPER_PEDAL_PART), seq)


    def set_raw_phrase(self, part, text):
        if part >= nlib.MAX_NORMAL_PART: return False
        return self.part_data[part].set_raw(text)

    def set_raw_composition(self, part, text):
        if part >= nlib.MAX_COMPOSITION_PART: return False
        return self.composition_part[part].set_raw(text)

    def set_recombined(self):
        self.composition_part.set_recombined()
        self.damper_part.set_recombined()
        for part in self.part_data:
            part.set_recombined()
