# -*- coding: utf-8 -*-
import lpnlib as nlib
import elapse as sqp
import elapse_phrase as phrlp

####
#   起動時から存在し、決して destroy されない ElapseIF Obj.
class Part(sqp.ElapseIF):

    def __init__(self, obj, md, fl, num):
        super().__init__(obj, md, 'Part')
        self.part_num = num
        self.first_measure_num = 0 # 新しい Phrase/Pattern が始まった絶対小節数

        self.fl = fl
        self.loop_obj = None
        self.keynote = nlib.DEFAULT_NOTE_NUMBER
        self.description = [None for _ in range(3)]
        self.loop_measure = 0   # whole_tick と同時生成
        self.lp_elapsed_msr = 0    # loop 内の経過小節数
        self.whole_tick = 0     # loop_measure と同時生成
        self.state_reserve = False

    def _generate_loop(self,msr):
        tick_for_onemsr = self.parent.get_tick_for_onemsr()
        self.whole_tick, elm = self.parent.gendt.get_final(self.part_num)

        # その時の beat 情報で、whle_tick を loop_measure に換算
        self.loop_measure = self.whole_tick//tick_for_onemsr + \
            (0 if self.whole_tick%tick_for_onemsr == 0 else 1)

        self.loop_obj = phrlp.PhraseLoop(self.parent, self.md, msr, elm,  \
            self.keynote, self.part_num, self.whole_tick)
        self.parent.add_obj(self.loop_obj)

##    def _set_chain_loading(self, msr, elapsed_msr):
##        if msr == 0:
##            noteinfo = self.fl.read_first_chain_loading(self.part_num)
##            self.description = noteinfo
##            return True
##        else:
            # 次回が overlap 対象か？
##            ol = self.fl.get_overlap(self.part_num)
            # あるいは、ひとつ前のデータに中身が無ければ
            # 1小節前になったか？ overlap の場合２小節前になったか？
##            condition = \
##                (self.loop_measure == 0) or \
##                ((self.loop_measure == elapsed_msr) and not ol) or \
##                ((self.loop_measure-1 == elapsed_msr) and ol)
##            if condition:
                # wait_for_looptop 期間中に次の Description をセットする
##                noteinfo = self.fl.read_next_chain_loading(self.part_num)
##                self.description = noteinfo
##                return True
##            return False

    ## Seqplay thread内でコール
    def start(self):
        self.first_measure_num = 0

    def msrtop(self,msr):
        def new_loop(msr):
            # 新たに Loop Obj.を生成
            self._generate_loop(msr)
            self.first_measure_num = msr    # 計測開始の更新
            self.lp_elapsed_msr = 1

        elapsed_msr = msr - self.first_measure_num
##        if self.fl.chain_loading_state:
            # Chain Loading
##            if self._set_chain_loading(msr, elapsed_msr):
##                new_loop(msr)

##        elif self.state_reserve:
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

    def change_cc(self, cc_num, val):
        if val >= 0 and val < 128:
            self.volume = val
            self.md.send_control(0, cc_num, val)

    def change_pgn(self, pgn):
        self.md.send_program(0, pgn)

    def update_phrase(self):
        self.state_reserve = True
