# -*- coding: utf-8 -*-

# Timing Priority(pri)
PRI_NONE = 1000
PRI_PART = 100
PRI_LOOP = 200
PRI_CHORD = 300
PRI_NOTE = 400
PRI_DMPR = 500

#------------------------------------------------------------------------------
#   ElapseIF Obj. の Interface
#   <Elapse> とは、再生用コマンドや、音楽の時間を扱う IF を持ったオブジェクト
class ElapseIF:

    def __init__(self, est, md, pri=PRI_NONE, id=-1):
        self.est = est
        self.md = md
        self.priority = pri
        self.id = id
        self.next_msr = 0
        self.next_tick = 0

    # ElapseIF thread内でコール
    def who_I_am(self):
        if self.id >= 0:
            return self.priority + self.id
        else:
            return self.priority

    def next(self):
        return self.next_msr, self.next_tick

    def start(self):    # User による start/play 時にコールされる
        pass

    def stop(self):     # User による stop 時にコールされる
        pass

    def fine(self):     # User による fine があった次の小節先頭でコールされる
        pass

    def periodic(self,msr,tick):    # 再生中、繰り返しコールされる
        pass

    def destroy_me(self):   # 自クラスが役割を終えた時に True を返す
        return False
