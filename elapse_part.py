# -*- coding: utf-8 -*-
import lpnlib as nlib
import elapse as elp
import elapse_loop as phrlp

#------------------------------------------------------------------------------
#   起動時から存在し、決して destroy されない ElapseIF Obj.
class Part(elp.ElapseIF):

    def __init__(self, est, md, num):
        super().__init__(est, md, elp.PRI_PART, num)
        self.part_num = num
        self.first_measure_num = 0 # 新しい Phrase/Pattern が始まった絶対小節数

        self.loop_obj = None
        left_part = 1-(num%nlib.FIRST_NORMAL_PART)//nlib.MAX_LEFT_PART # left なら 1, でなければ 0
        self.keynote = 0
        self.base_note = nlib.DEFAULT_NOTE_NUMBER - 12*left_part
        self.max_loop_msr = 0   # whole_tick と同時生成
        self.whole_tick = 0     # max_loop_msr と同時生成
        self.sync_next_msr_flag = False
        self.state_reserve = False
        self.seqdt_part = None
        self.cb_handler = None
        self.handler_owner = None

    def set_seqdt_part(self, gendt):
        self.seqdt_part = gendt

    def set_callback(self, func, gui):
        self.cb_handler = func
        self.handler_owner = gui

    def update_loop_for_gui(self):
        if self.cb_handler != None:
            #print('Update:',self.whole_tick)
            self.cb_handler(self.handler_owner, self.part_num, self.max_loop_msr)    # Callback

    def _generate_loop(self, msr):
        self.whole_tick, elm, ana = self.seqdt_part.get_final(msr)

        # その時の beat 情報で、whole_tick を loop_measure に換算
        tick_for_onemsr = self.est.get_tick_for_onemsr()
        self.max_loop_msr = int(self.whole_tick//tick_for_onemsr + \
            (0 if self.whole_tick%tick_for_onemsr == 0 else 1))

        self.update_loop_for_gui()
        if self.whole_tick == 0:
            self.state_reserve = True # 次小節冒頭で呼ばれるように
            self.loop_obj = None
            return

        if self.part_num >= nlib.FIRST_NORMAL_PART:
            self.loop_obj = phrlp.PhraseLoop(self.est, self.md, msr, elm, ana,  \
                self.keynote, self.whole_tick, self.part_num)
            self.est.add_obj(self.loop_obj)
        else:
            self.loop_obj = phrlp.CompositionLoop(self.est, self.md, msr, elm, ana, \
                self.keynote, self.whole_tick, self.part_num)
            self.est.add_obj_in_front(self.loop_obj)


    ## Seqplay thread内でコール
    def start(self):
        self.first_measure_num = 0
        self.next_msr = 0
        self.next_tick = 0
        self.state_reserve = True
        #self.md.send_control(0,7,100)  # dummy send


    def process(self, msr, tick):
        def new_loop(msr):
            # 新たに Loop Obj.を生成
            self.first_measure_num = msr    # 計測開始の更新
            self._generate_loop(msr)

        if self.state_reserve:
            # 前小節にて phrase/pattern 指定された時
            if msr == 0:
                # 今回 start したとき
                self.state_reserve = False
                new_loop(msr)

            elif self.max_loop_msr == 0:
                # データのない状態で start し、今回初めて指定された時
                self.state_reserve = False
                new_loop(msr)

            elif self.max_loop_msr != 0 and \
                (msr - self.first_measure_num)%self.max_loop_msr == 0:
                # 前小節にて Loop Obj が終了した時
                self.state_reserve = False
                new_loop(msr)

            elif self.max_loop_msr != 0 and self.sync_next_msr_flag:
                # sync コマンドによる強制リセット
                self.state_reserve = False
                self.sync_next_msr_flag = False
                self.est.del_obj(self.loop_obj)
                new_loop(msr)

            else:
                # 現在の Loop Obj が終了していない時
                # state_reserve は持ち越す
                pass

        elif self.max_loop_msr != 0:
            if (msr - self.first_measure_num)%self.max_loop_msr == 0:
                # 同じ Loop.Obj を生成する
                new_loop(msr)

        # 毎小節の頭で process() がコール
        self.next_msr = msr + 1


    def destroy_me(self):
        return False    # 最後まで削除されない

    #def stop(self):
    #    pass

    #def fine(self):
    #    self.stop()

    def change_key(self, key):  # 0-11
        self.keynote = key
        self.state_reserve = True

    def change_oct(self, oct, relative):
        # relative=False,oct=4: center(C4=60)
        # relative=True, oct=0: center(C4=60)
        if oct == nlib.NO_NOTE:
            return
        elif relative:
            newoct = self.base_note//12 + oct
        else:
            newoct = oct + 1
        self.base_note = nlib.note_limit(newoct*12, 0, 127)
        self.state_reserve = True

    def update_phrase(self):
        self.state_reserve = True

    def sync(self):
        self.sync_next_msr_flag = True
        self.state_reserve = True
