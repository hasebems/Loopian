# -*- coding: utf-8 -*-
import lpnlib as nlib

####
#   ElapseIF Obj. の Interface
#   <Elapse> とは、再生用コマンドや、音楽の時間を扱う IF を持ったオブジェクト
class ElapseIF:

    def __init__(self, obj, md, type='None'):
        self.parent = obj
        self.md = md
        self.type = type

    # ElapseIF thread内でコール
    def start(self):    # User による start/play 時にコールされる
        pass

    def stop(self):     # User による stop 時にコールされる
        pass

    def fine(self):     # User による fine があった次の小節先頭でコールされる
        pass

    def msrtop(self,msr):           # 小節先頭でコールされる
        pass

    def periodic(self,msr,tick):    # 再生中、繰り返しコールされる
        pass

    def destroy_me(self):   # 自クラスが役割を終えた時に True を返す
        return False


####
#   １行分の Phrase/Pattern を生成するための ElapseIF Obj.
#   １周期が終わったら、destroy され、また新しいオブジェクトが Part によって作られる
#   Loop 内のデータに基づき、Note Obj. を生成する
class Loop(ElapseIF):

    # example
    LOOP_LENGTH = 3

    def __init__(self, obj, md, type, msr):
        super().__init__(obj, md, type)
        self.first_measure_num = msr
        self.whole_tick = 0
        self.destroy = False
        self.tick_for_one_measure = self.parent.get_tick_for_onemsr()

    def _set_note(self,ev): 
        if ev[nlib.TYPE] == 'damper':# ev: ['damper', tick, value, duration]
            self.parent.add_obj(Damper(self.parent, self.md, ev))
        elif ev[nlib.TYPE] == 'note':# ev: ['note', tick, note, velocity, duration]
            self.parent.add_obj(Note(self.parent, self.md, ev))

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

####
#   一音符の ElapseIF Obj.
#   Note On時に生成され、MIDI を出力した後、Note Offを生成して destroy される
class Note(ElapseIF):

    def __init__(self, obj, md, ev):
        super().__init__(obj, md, 'Note')
        self.midi_ch = 0
        self.note_num = ev[nlib.NOTE]
        self.velocity = ev[nlib.VEL]
        self.duration = ev[nlib.DUR]
        self.during_noteon = False
        self.destroy = False
        self.off_msr = 0
        self.off_tick = 0

    def _note_on(self):
        self.md.send_midi_note(self.midi_ch, self.note_num, self.velocity)

    def _note_off(self):
        self.destroy = True
        self.during_noteon = False
        # midi note off
        self.md.send_midi_note(0, self.note_num, 0)

    def periodic(self,msr,tick):
        if not self.during_noteon:
            self.during_noteon = True
            tk = self.parent.get_tick_for_onemsr()
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

####
#   ペダルの ElapseIF Obj.
#   Pedal On時に生成され、MIDI を出力した後、Pedal Offを生成して destroy される
class Damper(ElapseIF):

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
        self.md.send_control(self.midi_ch, self.cc_num, self.value)

    def _pedal_off(self):
        self.destroy = True
        self.during_pedal = False
        # midi note off
        self.md.send_control(0, 64, 0)

    def periodic(self,msr,tick):
        if not self.during_pedal:
            self.during_pedal = True
            tk = self.parent.get_tick_for_onemsr()
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
