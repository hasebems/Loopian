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
        self.loop_measure = 0   # whole_tick と同時生成
        self.lp_elapsed_msr = 0    # loop 内の経過小節数 for GUI
        self.whole_tick = 0     # loop_measure と同時生成
        self.sync_next_msr_flag = False
        self.state_reserve = False
        self.seqdt_part = None

    def set_seqdt_part(self, gendt):
        self.seqdt_part = gendt

    def _generate_loop(self, msr):
        self.whole_tick, elm, ana = self.seqdt_part.get_final(msr)

        # その時の beat 情報で、whole_tick を loop_measure に換算
        tick_for_onemsr = self.est.get_tick_for_onemsr()
        self.loop_measure = int(self.whole_tick//tick_for_onemsr + \
            (0 if self.whole_tick%tick_for_onemsr == 0 else 1))

        self.next_msr = self.loop_measure + msr if self.loop_measure != 0 else msr+1
        self.next_tick = 0
        if self.whole_tick == 0:
            self.state_reserve = True # 次小節冒頭で呼ばれるように
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


    def periodic(self, msr, tick):
        def new_loop(msr):
            # 新たに Loop Obj.を生成
            self.first_measure_num = msr    # 計測開始の更新
            self._generate_loop(msr)
            self.lp_elapsed_msr = 1

        if self.next_msr < msr or \
            (self.next_msr == msr and self.next_tick <= tick):
            pass
        else:
            return

        #elapsed_msr = self.first_measure_num
        if self.state_reserve:
            # 前小節にて phrase/pattern 指定された時
            if msr == 0:
                # 今回 start したとき
                self.state_reserve = False
                new_loop(msr)

            elif self.loop_measure == 0:
                # データのない状態で start し、今回初めて指定された時
                self.state_reserve = False
                new_loop(msr)

            elif self.loop_measure != 0 and \
                (msr - self.first_measure_num)%self.loop_measure == 0:
                # 前小節にて Loop Obj が終了した時
                self.state_reserve = False
                new_loop(msr)

            elif self.loop_measure != 0 and self.sync_next_msr_flag:
                # sync コマンドによる強制リセット
                self.state_reserve = False
                self.sync_next_msr_flag = False
                self.est.del_obj(self.loop_obj)
                new_loop(msr)

            else:
                # 現在の Loop Obj が終了していない時
                pass

        if self.loop_measure != 0:
            if (msr - self.first_measure_num)%self.loop_measure == 0:
                # 同じ Loop.Obj を生成する
                self.first_measure_num = msr
                self._generate_loop(msr)
                self.lp_elapsed_msr = 1
            else:
                self.lp_elapsed_msr += 1


    def destroy_me(self):
        return False    # 最後まで削除されない

    #def stop(self):
    #    pass

    #def fine(self):
    #    self.stop()

    ## GUI thread内でコール
    def get_loop_info(self):
        return self.lp_elapsed_msr, self.loop_measure

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
