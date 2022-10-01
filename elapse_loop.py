# -*- coding: utf-8 -*-
import lpnlib as nlib
import elapse as ep
import elapse_note as epn
import lpntxt as tx
import copy

#------------------------------------------------------------------------------
#   １行分の Phrase/Composition を生成するための ElapseIF Obj.
#   １周期が終わったら、destroy され、また新しいオブジェクトが Part によって作られる
#   Loop 内のデータに基づき、Note Obj. を生成する
class Loop(ep.ElapseIF):

    # example
    LOOP_LENGTH = 3

    def __init__(self, obj, md, type, msr):
        super().__init__(obj, md, type)
        self.first_measure_num = msr
        self.whole_tick = 0
        self.destroy = False
        self.tick_for_one_measure = self.sqs.get_tick_for_onemsr()

    def msrtop(self,msr):
        pass

    def periodic(self,msr,tick):
        elapsed_tick = (msr - self.first_measure_num)*self.tick_for_one_measure + tick
        if elapsed_tick >= self.whole_tick:
            self.destroy = True
            return

    def destroy_me(self):
        return self.destroy

    def stop(self):
        self.destroy = True

    def fine(self):
        self.destroy = True


#------------------------------------------------------------------------------
class PhraseLoop(Loop):

    def __init__(self, obj, md, msr, phr, ana, key, wt):
        super().__init__(obj, md, 'PhrLoop', msr)
        self.phr = phr
        self.ana = ana
        self.keynote = key

        self.play_counter = 0
        self.next_tick = 0
        self.last_anaone = None

        # for super's member
        self.whole_tick = wt

    def _judge_arpeggio_diff(self, dt_tick, nt):
        for anaone in self.ana:
            if anaone[nlib.TICK] == dt_tick and nt in anaone[nlib.NOTE]:
                old_anaone = self.last_anaone
                self.last_anaone = anaone
                if old_anaone is not None and \
                    (anaone[nlib.ARP_DT][0] and old_anaone[nlib.ARP_DT][0]):
                    return anaone[nlib.ARP_DT][1]
        return nlib.NO_NOTE


    def _translate_note(self, nt):
        proper_nt = nt
        cmp_part = self.sqs.get_part(nlib.COMPOSITION_PART)
        if cmp_part != None and cmp_part.loop_obj != None:
            root, tbl = cmp_part.loop_obj.get_translation_tbl()
            root += nlib.DEFAULT_NOTE_NUMBER
            oct_adjust = (nt - (root+tbl[0]))//12
            former_nt = 0
            found = False
            for ntx in tbl:
                proper_nt = ntx + root + oct_adjust*12
                if proper_nt == nt:
                    found = True
                    break
                elif proper_nt > nt:
                    if nt-former_nt < proper_nt-nt:
                        # which is closer, below proper or above proper
                        proper_nt = former_nt
                    found = True
                    break
                former_nt = proper_nt
            if not found:   # next octave
                proper_nt = tbl[0] + root + (oct_adjust+1)*12
                if nt-former_nt < proper_nt-nt:
                    # which is closer, below proper or above proper
                    proper_nt = former_nt
        return proper_nt


    def _generate_event(self, tick):
        max_ev = len(self.phr)
        if max_ev == 0:
            # データを持っていない
            return nlib.END_OF_DATA

        if tick == 0:
            self.play_counter = 0
            tick = 1   # start時、最初のイベントを鳴らすため

        trace = self.play_counter
        next_tick = 0
        while True:
            if max_ev <= trace:
                next_tick = nlib.END_OF_DATA   # means sequence finished
                break
            next_tick = self.phr[trace][nlib.TICK]
            if next_tick < tick:
                ev = self.phr[trace]
                if ev[nlib.TYPE] == 'damper':# ev: ['damper', duration, tick, value]
                    self.sqs.add_obj(epn.Damper(self.sqs, self.md, ev))
                elif ev[nlib.TYPE] == 'note':# ev: ['note', tick, duration, note, velocity]
                    #arp_diff = self._judge_arpeggio_diff(next_tick, self.keynote)
                    orgev = copy.deepcopy(ev)
                    orgev[nlib.NOTE] = self._translate_note(ev[nlib.NOTE])
                    self.sqs.add_obj(epn.Note(self.sqs, self.md, orgev, self.keynote))
            else:
                break
            trace += 1

        self.play_counter = trace
        return next_tick

    ## IF Function by ElapseIF Class
    def periodic(self,msr,tick):
        tk_onemsr = self.tick_for_one_measure
        elapsed_tick = (msr - self.first_measure_num)*tk_onemsr + tick
        if elapsed_tick >= self.whole_tick:
            self.destroy = True
            return

        if elapsed_tick >= self.next_tick:
            nt = self._generate_event(elapsed_tick)
            if nt == nlib.END_OF_DATA:
                self.destroy = True
            self.next_tick = nt


#------------------------------------------------------------------------------
class CompositionLoop(Loop):

    def __init__(self, obj, md, msr, cmp, key, wt):
        super().__init__(obj, md, 'ComLoop', msr)
        self.cmp = cmp
        self.keynote = key

        self.play_counter = 0
        self.next_tick = 0
        self.chord = ['chord',0,'thru']
        self.root = 0
        self.translation_tbl = nlib.CHORD_SCALE['thru']

        # for super's member
        self.whole_tick = wt

    def get_chord(self):
        return self.chord[2]

    def get_translation_tbl(self):
        return self.root, self.translation_tbl

    def _prepare_note_translation(self):
        chord_name = self.get_chord()
        print(chord_name)
        if chord_name != '':
            self.root, self.translation_tbl = tx.TextParse.detect_chord_scale(chord_name)

    def _reset_note_tranlation(self):
        self.root = 0
        self.translation_tbl = nlib.CHORD_SCALE['thru']

    def _generate_event(self, tick):
        max_ev = len(self.cmp)
        if max_ev == 0:
            # データを持っていない
            self._reset_note_tranlation()
            return nlib.END_OF_DATA

        if tick == 0:
            self.play_counter = 0
            tick = 1   # start時、最初のイベントを鳴らすため

        trace = self.play_counter
        next_tick = 0
        while True:
            if max_ev <= trace:
                next_tick = nlib.END_OF_DATA   # means sequence finished
                break
            next_tick = self.cmp[trace][nlib.TICK]
            if next_tick < tick:
                self.chord = self.cmp[trace]
                self._prepare_note_translation()
            else:
                break
            trace += 1

        self.play_counter = trace
        return next_tick

    ## IF Function by ElapseIF Class
    def periodic(self, msr, tick):
        tk_onemsr = self.tick_for_one_measure
        elapsed_tick = (msr - self.first_measure_num)*tk_onemsr + tick
        if elapsed_tick >= self.whole_tick:
            self.destroy = True
            return

        if elapsed_tick >= self.next_tick:
            nt = self._generate_event(elapsed_tick)
            if nt == nlib.END_OF_DATA:
                self.destroy = True
            self.next_tick = nt
