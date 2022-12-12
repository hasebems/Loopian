# -*- coding: utf-8 -*-
import elapse as elp
import lpnlib as nlib

#------------------------------------------------------------------------------
#   一音符の ElapseIF Obj.
#   Note On時に生成され、MIDI を出力した後、Note Offを生成して destroy される
class Note(elp.ElapseIF):

    def __init__(self, est, md, ev, key, txt, crnt_msr_tick):
        super().__init__(est, md, elp.PRI_NOTE)
        self.midi_ch = 0
        self.note_num = ev[nlib.NOTE]
        self.velocity = ev[nlib.VEL]
        self.duration = ev[nlib.DUR]
        self.txt = txt
        self.keynote = key
        self.noteon_started = False
        self.noteoff_enable = True
        self.destroy = False
        self.next_msr = crnt_msr_tick[0]     # for Note On
        self.next_tick = crnt_msr_tick[1]    # for Note On

    def _cancel_same_noteoff(self, note_num):
        snts = self.est.same_note(note_num)
        if len(snts) == 0: return
        for snt in snts:
            if snt != self:
                snt.cancel_noteoff()

    def _note_on(self):
        num = self.note_num + self.keynote
        self.note_num = nlib.note_limit(num, 0, 127)
        if self.est.pianoteq_mode:
            self._cancel_same_noteoff(self.note_num)
        self.md.set_fifo(self.est.get_time(), ['note', self.midi_ch, self.note_num, self.velocity])
        print('Note:', self.note_num, self.velocity, self.txt)

    def _note_off(self):
        self.destroy = True
        self.next_msr = nlib.FULL
        # midi note off
        if self.noteoff_enable:
            self.md.set_fifo(self.est.get_time(), ['note', self.midi_ch, self.note_num, 0])

    def cancel_noteoff(self):
        self.noteoff_enable = False

    def process(self, msr, tick):
        if (msr == self.next_msr and tick >= self.next_tick) or msr > self.next_msr:
            if not self.noteon_started:
                self.noteon_started = True
                # midi note on
                self._note_on()

                tk = self.tick_for_one_measure
                msrcnt = 0
                off_tick = self.next_tick + self.duration
                while off_tick >= tk:
                    off_tick -= tk
                    msrcnt += 1
                self.next_msr += msrcnt
                self.next_tick = off_tick
            else:
                self._note_off()

    def destroy_me(self):
        return self.destroy

    def stop(self):
        if self.noteon_started:
            self._note_off()

    def fine(self):
        if self.noteon_started:
            self._note_off()

#------------------------------------------------------------------------------
#   ペダルの ElapseIF Obj.
#   Pedal On時に生成され、MIDI を出力した後、Pedal Offを生成して destroy される
class Damper(elp.ElapseIF):

    def __init__(self, est, md, ev, next_real):
        super().__init__(est, md, elp.PRI_DMPR)
        self.midi_ch = 0
        self.cc_num = 64
        self.value = ev[nlib.VAL]
        self.duration = ev[nlib.DUR]
        self.pedal_started = False
        self.destroy = False
        self.next_msr = next_real[0]
        self.next_tick = next_real[1]

    def _pedal_on(self, tick, off_tick):
        self.md.set_fifo(self.est.get_time(), ['damper', self.midi_ch, self.cc_num, self.value])
        print('Pedal:', self.value, int(tick), int(off_tick))

    def _pedal_off(self):
        self.destroy = True
        self.next_msr = nlib.FULL
        # midi damper pedal off
        self.md.set_fifo(self.est.get_time(), ['damper', self.midi_ch, self.cc_num, 0])

    def process(self, msr, tick):
        if (msr == self.next_msr and tick >= self.next_tick) or msr > self.next_msr:
            if not self.pedal_started:
                self.pedal_started = True
                tk = self.tick_for_one_measure
                msrcnt = 0
                off_tick = self.next_tick + self.duration
                while off_tick >= tk:
                    off_tick -= tk
                    msrcnt += 1
                # midi control change on
                self._pedal_on(self.next_tick, off_tick)
                self.next_msr += msrcnt
                self.next_tick = off_tick
            else:
                self._pedal_off()

    def destroy_me(self):
        return self.destroy

    def stop(self):
        if self.pedal_started:
            self._pedal_off()

    def fine(self):
        if self.pedal_started:
            self._pedal_off()
