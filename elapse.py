# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#   ElapseIF Obj. の Interface
#   <Elapse> とは、再生用コマンドや、音楽の時間を扱う IF を持ったオブジェクト
class ElapseIF:

    def __init__(self, obj, md, type='None'):
        self.sqs = obj
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
