# -*- coding: utf-8 -*-
import lpnlib as nlib
import elapse as sqp

class PhraseLoop(sqp.Loop):

    def __init__(self, obj, md, msr, phr, key, wt):
        super().__init__(obj, md, 'PhrLoop', msr)
        self.phr = phr
        self.keynote = key

        self.play_counter = 0
        self.next_tick = 0

        # for super's member
        self.whole_tick = wt

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
                self._set_note(self.phr[trace])
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

    def destroy_me(self):
        return self.destroy

    def stop(self):
        self.destroy = True


class CompositionLoop(sqp.Loop):

    def __init__(self, obj, md, msr, cmp, key, wt):
        super().__init__(obj, md, 'ComLoop', msr)
        self.cmp = cmp
        self.keynote = key

        self.play_counter = 0
        self.next_tick = 0
        self.chord = 'thru'

        # for super's member
        self.whole_tick = wt

    def _generate_event(self, tick):
        max_ev = len(self.cmp)
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
            next_tick = self.cmp[trace][nlib.TICK]
            if next_tick < tick:
                self.chord = self.cmp[trace]
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

    def destroy_me(self):
        return self.destroy

    def stop(self):
        self.destroy = True