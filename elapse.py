# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#   ElapseIF Obj. の Interface
#   <Elapse> とは、再生用コマンドや、音楽の時間を扱う IF を持ったオブジェクト
class ElapseIF:

    def __init__(self, est, md, type='None', id=-1):
        self.est = est
        self.md = md
        self.type = type
        self.id = id
        self.next_msr = 0
        self.next_tick = 0

    # ElapseIF thread内でコール
    def who_I_am(self):
        if self.id >= 0:
            return self.type + '-' + str(self.id)
        else:
            return self.type

    def next(self):
        return self.next_msr, self.next_tick

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
