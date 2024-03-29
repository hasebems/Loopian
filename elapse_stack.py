# -*- coding: utf-8 -*-
import time
import lpnlib as nlib
import elapse as elp
import elapse_part as elpp

#------------------------------------------------------------------------------
# Tempo 生成の考え方
#   1. Tempo 変化時の絶対時間とその時点の tick を記録
#   2. 次に Tempo が変わるまで、その時間との差から、現在の tick を算出する
#   また、本 class 内に rit. 機構を持つ
#
class TickGenerator:

    def __init__(self, tick_for_onemsr, bpm):
        self.tick_for_onemsr = tick_for_onemsr
        self.bpm = bpm
        self.beat = [4,4]

        self.origin_time = 0        # start 時の絶対時間
        self.bpm_start_time = 0     # tempo/beat が変わった時点の絶対時間、tick 計測の開始時間
        self.bpm_start_tick = 0     # tempo が変わった時点の tick, beat が変わったとき0clear
        self.beat_start_msr = 0     # beat が変わった時点の経過小節数
        self.crnt_measure = -1      # start からの小節数（最初の小節からイベントを出すため、-1初期化)
        self.crnt_tick_inmsr = 0    # 現在の小節内の tick 数
        self.crnt_time = 0          # 現在の時刻

        self.rit_state = False
        self.minus_bpm_for_gui = 0
        self.last_addup_tick = 0
        self.last_addup_time = 0

    def get_tick(self): # for GUI
        tick_for_beat = nlib.DEFAULT_TICK_FOR_ONE_MEASURE/self.beat[1]  # 一拍のtick数
        tick_inmsr = self.crnt_tick_inmsr
        count = self.tick_for_onemsr//tick_for_beat
        beat = tick_inmsr//tick_for_beat
        tick = tick_inmsr%tick_for_beat
        return int(self.crnt_measure),int(beat),int(tick),int(count)

    #==== rit. ======================
    def _calc_current_tick_rit(self, crnt_time):
        MINIMUM_TEMPO = 20
        start_time = crnt_time - self.bpm_start_time
        time_to0 = self.t0_time - start_time
        self.minus_bpm_for_gui = self.delta_tps*start_time/8
        if self.bpm - self.minus_bpm_for_gui > MINIMUM_TEMPO:
            addup_tick = self.t0_addup_tick - time_to0*time_to0*self.delta_tps/2    # 積算Tickの算出
            self.last_addup_tick = addup_tick
            self.last_addup_time = crnt_time
        else:
            self.minus_bpm_for_gui = self.bpm - MINIMUM_TEMPO
            addup_tick = self.last_addup_tick + (8*MINIMUM_TEMPO*(crnt_time-self.last_addup_time))
        return addup_tick + self.bpm_start_tick

    def calc_tick_rit(self, crnt_time):
        tick_from_rit_starts = self._calc_current_tick_rit(crnt_time)
        if self.tick_for_onemsr < tick_from_rit_starts:
            # End rit
            self.rit_state = False
            self.crnt_measure = self.beat_start_msr + 1
            self.crnt_tick_inmsr = 0

            self.beat_start_msr = self.crnt_measure
            self.bpm_start_time = crnt_time
            self.bpm_start_tick = 0
        else:
            self.crnt_tick_inmsr = tick_from_rit_starts

    def rit_evt(self, start_time, ratio):
        # ratio  0:   tempo 停止
        #        50:  1secで tempo を 50%(1/2)
        #        100: 何もしない
        if ratio >= 100 or self.rit_state: return
        else: self.delta_tps = ((100 - ratio)/100)*8*self.bpm
        self.t0_time = self.bpm*8/self.delta_tps # tempo0 time
        self.t0_addup_tick = (self.delta_tps/2)*self.t0_time*self.t0_time  # tempo0積算Tick

        self.rit_state = True
        self.beat_start_msr = self.crnt_measure
        self.bpm_start_time = start_time
        self.bpm_start_tick = self.crnt_tick_inmsr
    #=================================

    def _calc_current_tick(self, crnt_time):
        diff_time = crnt_time - self.bpm_start_time
        elapsed_tick = (480*self.bpm*diff_time)/60
        return elapsed_tick + self.bpm_start_tick

    def change_beat_event(self, tick_for_onemsr, beat):
        self.rit_state = False
        self.tick_for_onemsr = tick_for_onemsr
        self.beat = beat
        self.beat_start_msr = self.crnt_measure
        self.bpm_start_time = self.crnt_time
        self.bpm_start_tick = 0

    def change_bpm_event(self, bpm):
        self.rit_state = False
        self.bpm_start_tick = self._calc_current_tick(self.crnt_time)
        self.bpm_start_time = self.crnt_time  # Get current time
        self.bpm = bpm

    def calc_tick(self, crnt_time):
        self.crnt_time = crnt_time
        if self.rit_state:
            self.calc_tick_rit(crnt_time)
        else:
            tick_from_beat_starts = self._calc_current_tick(self.crnt_time)
            self.crnt_measure = tick_from_beat_starts//self.tick_for_onemsr + self.beat_start_msr
            self.crnt_tick_inmsr = tick_from_beat_starts%self.tick_for_onemsr

    def play(self, crnt_time):
        self.rit_state = False
        self.bpm_start_time = self.origin_time = crnt_time  # Get current time
        self.bpm_start_tick = 0
        self.beat_start_msr = 0

    def get_crnt_msr_tick(self):
        return self.crnt_measure, self.crnt_tick_inmsr

    def get_tick_for_onemsr(self):
        return self.tick_for_onemsr

    def get_bpm(self):
        if self.rit_state:
            return self.bpm - self.minus_bpm_for_gui
        else: return self.bpm

    def get_beat(self):
        return self.beat


class ElapseStack:
    #   開始時に生成され、process() がコマンド入力とは別スレッドで、定期的に呼ばれる。
    #   そのため、change_tempo, play, stop 受信時はフラグのみを立て、process()
    #   で実処理を行う。
    def __init__(self, md):
        self.md = md
        self.bpm_stock = 120
        self.stock_tick_for_onemsr = [nlib.DEFAULT_TICK_FOR_ONE_MEASURE,4,4]
        self.key_text = 'C'

        self.during_play = False
        self.play_for_periodic = False
        self.stop_for_periodic = False
        self.fine_for_periodic = False
        self.pianoteq_mode = True
        self.ritacl_evt = False
        self.ritacl_stock = 0

        self.tick_gen = TickGenerator(nlib.DEFAULT_TICK_FOR_ONE_MEASURE, self.bpm_stock)
        self.sqobjs = []
        for i in range(nlib.MAX_PART_COUNT): # Part は、常に存在
            obj = elpp.Part(self,md,i)
            self.sqobjs.append(obj)

    def add_obj(self, obj):
        self.sqobjs.append(obj)

    def del_obj(self, del_obj):
        if del_obj in self.sqobjs:
            self.sqobjs.remove(del_obj)

    def add_obj_in_front(self, obj):    # Part の直後に挿入
        self.sqobjs.insert(nlib.MAX_PART_COUNT, obj)

    def get_time(self): # for Note
        return self.tick_gen.crnt_time

    def get_tick(self): # for GUI
        return self.tick_gen.get_tick()

    def get_sqobj_count(self, pri):
        count = 0
        for obj in self.sqobjs:
            if obj.pri == pri: count += 1
        return count

    def get_tick_for_onemsr(self):
        return self.tick_gen.get_tick_for_onemsr()

    def get_bpm(self):
        return self.tick_gen.get_bpm()

    def get_beat(self):
        return self.tick_gen.get_beat()

    def get_part(self, number):
        if number < nlib.MAX_PART_COUNT:
            return self.sqobjs[number]
        else:
            return None

    def same_note(self, num):
        nt = []
        for obj in self.sqobjs:
            if obj.priority == elp.PRI_NOTE and obj.note_num == num:
                nt.append(obj)
        return nt

    def _play(self, crnt_time):
        self.tick_gen.play(crnt_time)

    def _destroy_ended_obj(self):
        maxsq = len(self.sqobjs)
        removed_num = -1
        while removed_num < maxsq:
            removed_num = -1
            for i in range(maxsq):
                if self.sqobjs[i].destroy_me():
                    self.sqobjs.pop(i)
                    removed_num = i
                    break
            if removed_num == -1: break
            maxsq = len(self.sqobjs)
            #print('Destroyed!')

    def _insert_proper_locate(self, elapsed, sqobj):
        msr, tick = sqobj.next()
        for i in range(len(elapsed)):
            msrx, tickx = elapsed[i].next()
            if (msr == msrx and \
                ((tick == tickx and elapsed[i].priority > sqobj.priority) or \
                  tick < tickx)) or \
                (msr < msrx):
                elapsed.insert(i, sqobj)
                return

    def _pick_out_play_obj(self, crnt_msr, crnt_tick):
        elapsed = []
        for sqobj in self.sqobjs:
            msr, tick = sqobj.next()
            if (msr == crnt_msr and tick <= crnt_tick) or msr < crnt_msr:
                # 現在のタイミングより前のイベントがあれば
                if len(elapsed) == 0:
                    elapsed.append(sqobj)
                else:
                    self._insert_proper_locate(elapsed, sqobj)
        return elapsed

    def _debug_disp(self):
        elapse_obj = 'ElapseObj: '                # for debug
        for sqobj in self.sqobjs:
            elapse_obj += str(sqobj.who_I_am()) + ',' # for debug
        print(elapse_obj)                        # for debug

    def periodic(self):     # seqplay thread
        crnt_time = time.time()

        ## check flags
        if self.play_for_periodic and not self.during_play:
            self.play_for_periodic = False
            self._play(crnt_time)
            self.during_play = True
            for sqobj in self.sqobjs:
                sqobj.start()

        if self.stop_for_periodic:
            self.stop_for_periodic = False
            self.during_play = False
            self.ritacl_evt = False
            for sqobj in self.sqobjs:
                sqobj.stop()
            self._destroy_ended_obj()

        if not self.during_play:
            #self.block.no_running()
            return

        # rit. or accel. event
        if self.ritacl_evt:
            self.ritacl_evt = False
            self.tick_gen.rit_evt(crnt_time, self.ritacl_stock)

        ## detect tick and measure
        former_msr, former_tick = self.tick_gen.get_crnt_msr_tick()
        self.tick_gen.calc_tick(crnt_time)
        crnt_measure, crnt_tick_inmsr = self.tick_gen.get_crnt_msr_tick()

        ## new measure or not
        if former_msr != crnt_measure:
            # 小節を跨いだ場合
            if self.stock_tick_for_onemsr[0] is not self.tick_gen.get_tick_for_onemsr():
                self.tick_gen.change_beat_event(self.stock_tick_for_onemsr[0], self.stock_tick_for_onemsr[1:3])

            if self.tick_gen.get_bpm() != self.bpm_stock:
                self.tick_gen.change_bpm_event(self.bpm_stock)

            if self.fine_for_periodic:
                # fine event
                self.fine_for_periodic = False
                self.during_play = False
                for sqobj in self.sqobjs:
                    sqobj.fine()
                self._destroy_ended_obj()
                return
            self._debug_disp()
        

        unfinish_counter = 0
        while True:
            # 現measure/tick より前のイベントを持つ obj を拾い出し、リストに入れて返す
            play_sqobjs = self._pick_out_play_obj(crnt_measure, crnt_tick_inmsr)
            if len(play_sqobjs) == 0:
                break
            # 再生 obj. をリスト順にコール
            for obj in play_sqobjs:
                obj.process(crnt_measure, crnt_tick_inmsr)
            unfinish_counter += 1
            if unfinish_counter > 100:
                print("Error! Unable to finish obj. exist! No.: ", play_sqobjs[0].priority)
                self._debug_disp()
                while True: pass    # 無限ループ

        ## remove ended obj
        self._destroy_ended_obj()

    def change_tempo(self, tempo):     # main thread
        self.bpm_stock = tempo

    def change_beat(self, btnum, onpu):    # beat: number of ticks of one measure
        # [1小節内のtick, 1小節内の拍数, 一拍の音価(2/4/8/16...)]
        beat = ((nlib.DEFAULT_TICK_FOR_ONE_MEASURE/onpu)*btnum, btnum, onpu)
        self.stock_tick_for_onemsr = beat

    def change_key_oct(self, key, oct, text):     # main thread
        self.key_text = text
        for i in range(nlib.MAX_PART_COUNT):
            pt = self.get_part(i)
            pt.change_key(key)
            pt.change_oct(oct, False)

    def set_pianoteq_mode(self, md):
        self.pianoteq_mode = md

    def start(self):     # main thread
        self.play_for_periodic = True
        if self.during_play:
            return False
        else:
            return True

    def ritacl(self, strength, next_tempo):   # main thread
        # strength: 0/1/2,  next_tempo: -1(fine)/0/tempo
        ratio_tbl = [90, 75, 60]
        if strength > 2: strength = 1
        self.ritacl_stock = ratio_tbl[strength]
        if next_tempo == 0:
            self.bpm_stock = self.tick_gen.get_bpm()
        elif next_tempo == -1:
            self.bpm_stock = 0
        else:
            self.bpm_stock = next_tempo
        self.ritacl_evt = True

    def stop(self):     # main thread
        self.stop_for_periodic = True

    def fine(self):     # main thread
        self.fine_for_periodic = True
