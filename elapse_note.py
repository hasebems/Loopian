# -*- coding: utf-8 -*-
import elapse as ep
import lpnlib as nlib

#------------------------------------------------------------------------------
#   一音符の ElapseIF Obj.
#   Note On時に生成され、MIDI を出力した後、Note Offを生成して destroy される
class Note(ep.ElapseIF):

    def __init__(self, obj, md, ev, key):
        super().__init__(obj, md, 'Note')
        self.midi_ch = 0
        self.note_num = ev[nlib.NOTE]
        self.velocity = ev[nlib.VEL]
        self.duration = ev[nlib.DUR]
        self.key = key
        self.during_noteon = False
        self.destroy = False
        self.off_msr = 0
        self.off_tick = 0

    def _note_on(self):
        cmp_part = self.sqs.get_part(nlib.COMPOSITION_PART)
        if cmp_part != None and cmp_part.loop_obj != None:
            root, tbl = cmp_part.loop_obj.get_translation_tbl()
            nt = self.note_num
            proper_nt = 0
            i = 0
            while  len(tbl) > i:
                former_nt = proper_nt
                proper_nt = tbl[i]+root+nlib.DEFAULT_NOTE_NUMBER
                if proper_nt >= nt and i > 0:
                    # which is closer, below proper or above proper
                    if nt-former_nt < proper_nt-nt:
                        proper_nt = former_nt
                    break
                i += 1
            self.note_num = proper_nt
        num = self.note_num + self.key - nlib.DEFAULT_NOTE_NUMBER
        self.note_num = nlib.note_limit(num, 0, 127)
        self.md.set_fifo(self.sqs.get_time(), ['note', self.midi_ch, self.note_num, self.velocity])

    def _note_off(self):
        self.destroy = True
        self.during_noteon = False
        # midi note off
        self.md.set_fifo(self.sqs.get_time(), ['note', self.midi_ch, self.note_num, 0])

    def periodic(self,msr,tick):
        if not self.during_noteon:
            self.during_noteon = True
            tk = self.sqs.get_tick_for_onemsr()
            self.off_msr = msr
            self.off_tick = tick + self.duration
            while self.off_tick > tk:
                self.off_tick -= tk
                self.off_msr += 1
            # midi note on
            self._note_on()
        else:
            if msr == self.off_msr and tick > self.off_tick:
                self._note_off()

    def destroy_me(self):
        return self.destroy

    def stop(self):
        if self.during_noteon:
            self._note_off()


#------------------------------------------------------------------------------
#   ペダルの ElapseIF Obj.
#   Pedal On時に生成され、MIDI を出力した後、Pedal Offを生成して destroy される
class Damper(ep.ElapseIF):

    def __init__(self, obj, md, ev):
        super().__init__(obj, md, 'Damper')
        self.midi_ch = 0
        self.cc_num = 64
        self.value = ev[nlib.VAL]
        self.duration = ev[nlib.DUR]
        self.during_pedal = False
        self.destroy = False
        self.off_msr = 0
        self.off_tick = 0

    def _pedal_on(self):
        self.md.set_fifo(self.sqs.get_time(), ['damper', self.midi_ch, self.cc_num, self.value])

    def _pedal_off(self):
        self.destroy = True
        self.during_pedal = False
        # midi damper pedal off
        self.md.set_fifo(self.sqs.get_time(), ['damper', self.midi_ch, self.cc_num, 0])

    def periodic(self,msr,tick):
        if not self.during_pedal:
            self.during_pedal = True
            tk = self.sqs.get_tick_for_onemsr()
            self.off_msr = msr
            self.off_tick = tick + self.duration
            while self.off_tick > tk:
                self.off_tick -= tk
                self.off_msr += 1
            # midi control change on
            self._pedal_on()
        else:
            if msr == self.off_msr and tick > self.off_tick:
                self._pedal_off()

    def destroy_me(self):
        return self.destroy

    def stop(self):
        if self.during_pedal:
            self._pedal_off()
