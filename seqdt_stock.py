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
        self.note_value = 0     # 音価


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
            elif last_note <= 127 and last_cnt == 1 and \
               crnt_note <= 127 and crnt_cnt == 1 and \
               crnt_note-last_note > -10 and crnt_note-last_note < 10:
                # 過去＆現在：単音、ノート適正、差が10半音以内
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


    def set_raw(self, text, imd):
        # 1. raw
        if text[0] == '+' and self.raw != None:
            self.raw += text
        else:
            self.raw = text

        # 2.complement data
        cmpl, self.note_value = tx.TextParse.complement_bracket(self.raw)   # リスト [3] = [note[],dur[],exp]
        print('complement:',cmpl)
        if cmpl != None:
            self.complement = cmpl
        else:
            return False

        # 3-5.recombined data
        self.set_recombined(imd)

        return True

    def set_recombined(self, imd):
        # Next measure information
        next_tick_for_onemsr = self.seq.stock_tick_for_onemsr[0]
        next_bpm = self.seq.bpm_stock

        # 3.recombined data
        self.whole_tick, self.generated, self.exps = \
            tx.TextParse.recombine_to_internal_format( \
                self.complement, self.part.base_note, next_tick_for_onemsr, self.note_value, imd)
        print('recombined:',self.generated)

        # 4.analysed data
        self.analysed = PhraseDataStock._analyse_plain_data(self.generated, self.exps)

        # 5.humanized data
        ### Add Filters
        self.generated = efb.BeatFilter().filtering(self.generated, next_bpm, next_tick_for_onemsr)
        ### 

        print('humanized:',self.generated)
        self.part.update_phrase()


    def get_final(self, msr):
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


#------------------------------------------------------------------------------
#   Damper の入力テキストの変換
class DamperPartStock:

    PDL_MARGIN_TICK = 60
    PDL_OFF = -1
    PDL_ON = 1
    NO_EV = 0

    def __init__(self, pt, seq):
        self.seq = seq
        self.part = pt
        self.part.set_seqdt_part(self)
        self.part.update_phrase()    # always
        self.tick_for_onemsr = nlib.DEFAULT_TICK_FOR_ONE_MEASURE

    def set_raw(self, text):
        return True

    def set_recombined(self):
        return

    def _collect_cmp_part_event(self, pt, msr, btick):
        ped_beat_map = [self.NO_EV for _ in range(int(self.tick_for_onemsr//btick))]

        # Pedal Event とは関係ないパートか？
        if pt.loop_obj == None or \
           (len(pt.loop_obj.cmp) == 1 and 
             (pt.loop_obj.cmp[0][nlib.CHORD] == 'thru' or pt.loop_obj.cmp[0][nlib.CHORD] == '')):
            return ped_beat_map
        if pt.loop_obj.ana != None and 'noped' in pt.loop_obj.ana:
            return ped_beat_map

        cmpdt = pt.loop_obj.cmp
        loopmsr = msr - pt.first_measure_num
        for dt in cmpdt:
            ped = dt[nlib.CHORD]
            tick = dt[nlib.TICK]
            if self.tick_for_onemsr*loopmsr <= tick and tick < self.tick_for_onemsr*(loopmsr+1):
                tick_in_onemsr = tick - self.tick_for_onemsr*loopmsr
                #tick = (tick + self.PDL_MARGIN_TICK)%self.tick_for_onemsr
                if ped == 'thru' or ped == '':
                    ped_beat_map[int(tick_in_onemsr//btick)] = self.PDL_OFF
                else:
                    ped_beat_map[int(tick_in_onemsr//btick)] = self.PDL_ON
        return ped_beat_map


    def get_final(self, msr):
        def pedal_ev(ont,dur):
            return ['damper', ont*btick+self.PDL_MARGIN_TICK, dur*btick-self.PDL_MARGIN_TICK, 127]

        self.tick_for_onemsr = self.seq.get_tick_for_onemsr()
        beat_cnt = self.seq.beat[0]
        btick = self.tick_for_onemsr//beat_cnt

        # 全 Composition Part の Chord 情報を収集、マージする
        # 拍数のリストを作り、PedalイベントのMapを作る
        ped_beat_map = [self.NO_EV for _ in range(beat_cnt)] # -1:off, 0:none, 1:on
        for i in range(nlib.FIRST_COMPOSITION_PART,
                       nlib.FIRST_COMPOSITION_PART+nlib.MAX_COMPOSITION_PART):
            pt = self.seq.get_part(i)
            pbm = self._collect_cmp_part_event(pt, msr, btick)
            for j in range(beat_cnt):
                if pbm[j] == self.PDL_ON:
                    ped_beat_map[j] = self.PDL_ON
                elif pbm[j] == self.PDL_OFF:
                    if ped_beat_map[j] == 0: ped_beat_map[j] = self.PDL_OFF
                else: pass # pbm[j] == 0 のときは、ped_beat_map はそのまま
        print('Pdl Map:',ped_beat_map)

        # Chord 変化情報から Pedal Seq.を生成
        gendt = []                         
        ontmg = -1
        for bc in range(beat_cnt):
            if ped_beat_map[bc] == self.PDL_ON:
                if ontmg >= 0:
                    gendt.append(pedal_ev(ontmg,bc-ontmg))
                ontmg = bc                    
            elif ped_beat_map[bc] == self.PDL_OFF:
                if ontmg >= 0:
                    gendt.append(pedal_ev(ontmg,bc-ontmg))
                    ontmg = -1 # Event Reset
            if bc == beat_cnt-1: # 最後の拍の場合
                if ontmg == bc: gendt.append(pedal_ev(ontmg,1))
                elif ontmg >= 0: gendt.append(pedal_ev(ontmg,beat_cnt-ontmg))
        print('Pedal:',gendt)

        return self.tick_for_onemsr, gendt, None

#------------------------------------------------------------------------------
#   Composition の入力テキストの変換
class CompositionPartStock:

    def __init__(self, objs, seq):
        self.seq = seq
        self.part = objs
        self.part.set_seqdt_part(self)

        self.raw = []
        self.complement = []
        self.generated = [nlib.NO_CHORD]
        self.exp = []

        self.whole_tick = 0

    def set_raw(self, text):
        # 1. raw
        if text[0] == '+' and self.raw != None:
            self.raw += text
        else:
            self.raw = text

        # 2.complement data
        cmpl, exp = tx.TextParse.complement_brace(self.raw)
        print('complement:',cmpl)
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
        # Next measure information
        tick_for_onemsr = self.seq.stock_tick_for_onemsr[0]
        tick_for_onebeat = tick_for_onemsr//self.seq.stock_tick_for_onemsr[1]

        # 3. recombined
        self.whole_tick, self.generated = \
            tx.TextParse.recombine_to_chord_loop(self.complement, tick_for_onemsr, tick_for_onebeat)
        print('recombined:',self.generated)

    def get_final(self, msr):
        return self.whole_tick, self.generated, self.exp

#------------------------------------------------------------------------------
#   入力テキストデータの変換処理を集約するクラス
class SeqDataAllStock:

    def __init__(self, seq):
        self.composition_part_data = []
        self.phrase_part_data = []
        self.input_mode = nlib.INPUT_CLOSER
        self.seq = seq

        # Composition Part
        for i in range(nlib.MAX_COMPOSITION_PART):
            pdt = CompositionPartStock(seq.get_part(i+nlib.FIRST_COMPOSITION_PART), seq)
            self.composition_part_data.append(pdt)

        # Phrase Part
        for i in range(nlib.MAX_NORMAL_PART):
            pdt = PhraseDataStock(seq.get_part(i+nlib.FIRST_NORMAL_PART), seq)
            self.phrase_part_data.append(pdt)

        # Damper Pedal Part
        self.damper_part_data = DamperPartStock(seq.get_part(nlib.DAMPER_PEDAL_PART), seq)

    def set_input_mode(self, md):
        self.input_mode = md

    def set_raw_phrase(self, part, text):
        if part >= nlib.MAX_NORMAL_PART: return False
        return self.phrase_part_data[part].set_raw(text, self.input_mode)

    def set_raw_composition(self, part, text):
        if part >= nlib.MAX_COMPOSITION_PART: return False
        return self.composition_part_data[part].set_raw(text)

    def set_recombined(self):
        for cpart in self.composition_part_data:
            cpart.set_recombined()
        for part in self.phrase_part_data:
            part.set_recombined(self.input_mode)
        self.damper_part_data.set_recombined()