# -*- coding: utf-8 -*-
import lpnlib as nlib
import elapse as sqp
import elapse_loop as phrlp

####
#   起動時から存在し、決して destroy されない ElapseIF Obj.
class Part(sqp.ElapseIF):

    def __init__(self, obj, md, num):
        super().__init__(obj, md, 'Part')
        self.part_num = num
        self.first_measure_num = 0 # 新しい Phrase/Pattern が始まった絶対小節数

        self.loop_obj = None
        self.keynote = nlib.DEFAULT_NOTE_NUMBER
        self.loop_measure = 0   # whole_tick と同時生成
        self.lp_elapsed_msr = 0    # loop 内の経過小節数
        self.whole_tick = 0     # loop_measure と同時生成
        self.state_reserve = False
        self.seqdt_part = None

    def set_seqdt_part(self, gendt):
        self.seqdt_part = gendt

    def _generate_loop(self,msr):
        tick_for_onemsr = self.sqs.get_tick_for_onemsr()
        self.whole_tick, elm = self.seqdt_part.get_final()

        # その時の beat 情報で、whle_tick を loop_measure に換算
        self.loop_measure = self.whole_tick//tick_for_onemsr + \
            (0 if self.whole_tick%tick_for_onemsr == 0 else 1)

        self.loop_obj = phrlp.PhraseLoop(self.sqs, self.md, msr, elm,  \
            self.keynote, self.part_num, self.whole_tick)
        self.sqs.add_obj(self.loop_obj)

    ## Seqplay thread内でコール
    def start(self):
        self.first_measure_num = 0
        self.md.send_control(0,7,100)  # dummy send

    def msrtop(self,msr):
        def new_loop(msr):
            # 新たに Loop Obj.を生成
            self._generate_loop(msr)
            self.first_measure_num = msr    # 計測開始の更新
            self.lp_elapsed_msr = 1

        elapsed_msr = msr - self.first_measure_num
        if self.state_reserve:
            self.state_reserve = False
            # 前小節にて phrase/pattern 指定された時
            if msr == 0:
                # 今回 start したとき
                new_loop(msr)

            elif self.loop_measure == 0:
                # データのない状態で start し、今回初めて指定された時
                new_loop(msr)

            elif self.loop_measure != 0 and elapsed_msr%self.loop_measure == 0:
                # 前小節にて Loop Obj が終了した時
                new_loop(msr)

            else:
                # 現在の Loop Obj が終了していない時
                pass

        elif self.whole_tick != 0:
            if self.loop_measure != 0 and elapsed_msr%self.loop_measure == 0:
                # 同じ Loop.Obj を生成する
                self._generate_loop(msr)
                self.lp_elapsed_msr = 1
            else:
                self.lp_elapsed_msr += 1

        else:
            # Loop 途中で何も起きないとき
            pass

    #def periodic(self,msr,tick):
    #    pass

    def destroy_me(self):
        return False    # 最後まで削除されない

    #def stop(self):
    #    pass

    #def fine(self):
    #    self.stop()

    ## GUI thread内でコール
    def get_loop_info(self):
        return self.lp_elapsed_msr, self.loop_measure

    def change_keynote(self, nt):
        self.keynote = nt
        self.state_reserve = True

    def update_phrase(self):
        self.state_reserve = True
