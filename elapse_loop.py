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

    def __init__(self, est, md, type, msr):
        super().__init__(est, md, type)
        self.first_measure_num = msr
        self.whole_tick = 0
        self.destroy = False
        self.tick_for_one_measure = self.est.get_tick_for_onemsr()

    def msrtop(self,msr):
        pass

    def periodic(self,msr,tick):
        elapsed_tick = (msr - self.first_measure_num)*self.tick_for_one_measure + tick
        if elapsed_tick >= self.whole_tick:
            self.destroy = True

    def destroy_me(self):
        return self.destroy

    def stop(self):
        self.destroy = True

    def fine(self):
        self.destroy = True


#------------------------------------------------------------------------------
class PhraseLoop(Loop):

    def __init__(self, obj, md, msr, phr, ana, key, wt, pnum):
        super().__init__(obj, md, 'PhrLoop', msr)
        self.phr = copy.deepcopy(phr)
        self.ana = copy.deepcopy(ana)
        self.keynote = key
        self.part_num = pnum    # 親パートの番号

        self.play_counter = 0
        self.next_tick = 0
        self.last_anaone = None
        self.last_note = nlib.NO_NOTE

        # for super's member
        self.whole_tick = wt

    def _identify_trans_option(self, dt_tick, nt):
        for anaone in self.ana:
            if anaone[nlib.TICK] == dt_tick and nt in anaone[nlib.NOTE]:
                return anaone[nlib.ARP_DT]
        return nlib.NO_NOTE


    def _translate_note_arp(self, root, tbl, arp_diff):
        arp_nt = self.last_note + arp_diff
        nty = nlib.DEFAULT_NOTE_NUMBER
        if arp_diff == 0:
            return arp_nt
        elif arp_diff > 0:
            ntx = self.last_note + 1
            ntx = nlib.search_scale_nt_just_above(root, tbl, ntx)
            if ntx >= arp_nt:
                return ntx
            while nty < 128:
                nty = ntx + 1
                nty = nlib.search_scale_nt_just_above(root, tbl, nty)
                if nty >= arp_nt:
                    if nty-arp_nt >= arp_nt-ntx:
                        nty = ntx
                    break
                ntx = nty
            return nty
        else:
            ntx = self.last_note - 1
            ntx = nlib.search_scale_nt_just_below(root, tbl, ntx)
            if ntx <= arp_nt:
                return ntx
            while nty >= 0:
                nty = ntx - 1
                nty = nlib.search_scale_nt_just_below(root, tbl, nty)
                if nty <= arp_nt:
                    if arp_nt-nty >= ntx-arp_nt:
                        nty = ntx
                    break
                ntx = nty
            return nty


    def _translate_note_com(self, root, tbl, nt):
        proper_nt = nt
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


    def _note_event(self, ev, next_tick):
        crntev = copy.deepcopy(ev)
        cmp_part = self.est.get_part(nlib.FIRST_COMPOSITION_PART+self.part_num-nlib.FIRST_NORMAL_PART)
        deb_txt = 'non'
        if cmp_part != None and cmp_part.loop_obj != None:
            root, tbl = cmp_part.loop_obj.get_translation_tbl()
            ana = cmp_part.loop_obj.get_ana()
            option = self._identify_trans_option(next_tick, ev[nlib.NOTE])
            if ana == 'para':
                tgt_nt = ev[nlib.NOTE]+root
                if root > 5: tgt_nt -= 12
                self.last_note = self._translate_note_com(root, tbl, tgt_nt)
                deb_txt = 'para:' + str(root)
            elif cmp_part.loop_obj.get_chord() != 'thru' and option[0] == 'arp':
                self.last_note = self._translate_note_arp(root, tbl, option[1])
                deb_txt = 'arp:' + str(root)
            else:   # option[0] == com
                self.last_note = self._translate_note_com(root, tbl, ev[nlib.NOTE])
                deb_txt = 'com:' + str(root)
            crntev[nlib.NOTE] = self.last_note
        self.est.add_obj(epn.Note(self.est, self.md, crntev, self.keynote, deb_txt))


    def _generate_event(self, tick):
        max_ev = len(self.phr)
        if max_ev == 0:
            # データを持っていない
            return nlib.END_OF_DATA

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
                    self.est.add_obj(epn.Damper(self.est, self.md, ev))
                elif ev[nlib.TYPE] == 'note':# ev: ['note', tick, duration, note, velocity]
                    self._note_event(ev, next_tick)
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

    def __init__(self, obj, md, msr, cmp, ana, key, wt):
        super().__init__(obj, md, 'ComLoop', msr)
        self.cmp = copy.deepcopy(cmp)
        self.ana = copy.deepcopy(ana)
        self.keynote = key

        self.play_counter = 0
        self.elapsed_tick = 0
        self.next_tick = 0
        self.seqdt = ['chord',0,'thru']
        self.chord_name = self.seqdt[2]
        self.root = 0
        self.translation_tbl = nlib.CHORD_SCALE['thru']

        # for super's member
        self.whole_tick = wt

    def get_ana(self):
        return self.ana

    def get_chord(self):
        return self.seqdt[2]

    def get_translation_tbl(self):
        return self.root, self.translation_tbl

    def _prepare_note_translation(self):
        self.chord_name = self.get_chord()
        if self.chord_name != '':
            self.root, self.translation_tbl = tx.TextParse.detect_chord_scale(self.chord_name)
        print(self.chord_name)

    def _reset_note_tranlation(self):
        self.root = 0
        self.translation_tbl = nlib.CHORD_SCALE['thru']

    def _generate_event(self, tick):
        max_ev = len(self.cmp)
        if max_ev == 0:
            # データを持っていない
            self._reset_note_tranlation()
            return nlib.END_OF_DATA

        trace = self.play_counter
        next_tick = 0
        while True:
            if max_ev <= trace:
                next_tick = nlib.END_OF_DATA   # means sequence finished
                break
            next_tick = self.cmp[trace][nlib.TICK]
            if next_tick < tick:
                self.seqdt = self.cmp[trace]
                self._prepare_note_translation()
            else:
                break
            trace += 1

        self.play_counter = trace
        return next_tick

    ## IF Function by ElapseIF Class
    def periodic(self, msr, tick):
        tk_onemsr = self.tick_for_one_measure
        self.elapsed_tick = (msr - self.first_measure_num)*tk_onemsr + tick
        if self.elapsed_tick >= self.whole_tick:
            self.destroy = True
            return

        if self.elapsed_tick >= self.next_tick:
            nt = self._generate_event(self.elapsed_tick)
            if nt == nlib.END_OF_DATA:
                self.destroy = True
            self.next_tick = nt
