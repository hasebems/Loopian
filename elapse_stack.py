# -*- coding: utf-8 -*-
import time
import lpnlib as nlib
import elapse as elp
import elapse_part as elpp
import copy

#------------------------------------------------------------------------------
# Tempo 生成の考え方
#   1. Tempo 変化時の絶対時間とその時点の tick を記録
#   2. 次に Tempo が変わるまで、その時間との差から、現在の tick を算出する
#   また、本 class 内に rit. 機構を持つ
#
class ElapseStack:
    #   開始時に生成され、periodic() がコマンド入力とは別スレッドで、定期的に呼ばれる。
    #   そのため、change_tempo, play, stop 受信時はフラグのみを立て、periodic()
    #   で実処理を行う。
    def __init__(self, md):
        self.md = md

        self.origin_time = 0        # start 時の絶対時間
        self.bpm_start_time = 0     # tempo/beat が変わった時点の絶対時間、tick 計測の開始時間
        self.bpm_start_tick = 0     # tempo が変わった時点の tick, beat が変わったとき0clear
        self.beat_start_msr = 0     # beat が変わった時点の経過小節数
        self.elapsed_time = 0       # start からの経過時間
        self.crnt_measure = -1      # start からの小節数（最初の小節からイベントを出すため、-1初期化)
        self.crnt_tick_inmsr = 0    # 現在の小節内の tick 数
        self.crnt_time = 0       # 現在の時刻

        self.bpm = 120
        self.bpm_stock = 120
        self.beat = [4,4]
        self.tick_for_onemsr = nlib.DEFAULT_TICK_FOR_ONE_MEASURE # 1920
        self.stock_tick_for_onemsr = [nlib.DEFAULT_TICK_FOR_ONE_MEASURE,4,4]
        self.key_text = 'C'

        self.during_play = False
        self.play_for_periodic = False
        self.stop_for_periodic = False
        self.fine_for_periodic = False

        self.sqobjs = []
        for i in range(nlib.MAX_PART_COUNT): # Part は、常に存在
            obj = elpp.Part(self,md,i)
            self.sqobjs.append(obj)

    def add_obj(self, obj):
        self.sqobjs.append(obj)
        #print(len(self.sqobjs))

    def del_obj(self, del_obj):
        if del_obj in self.sqobjs:
            self.sqobjs.remove(del_obj)

    def add_obj_in_front(self, obj):    # Part の直後に挿入
        self.sqobjs.insert(nlib.MAX_PART_COUNT, obj)

    def get_time(self):
        return self.crnt_time

    def get_sqobj_count(self, pri):
        count = 0
        for obj in self.sqobjs:
            if obj.pri == pri: count += 1
        return count

    def get_tick_for_onemsr(self):
        return self.tick_for_onemsr

    def get_part(self, number):
        if number < nlib.MAX_PART_COUNT:
            return self.sqobjs[number]
        else:
            return None

    def get_note(self, part_num):
        nt = []
        for obj in self.sqobjs:
            if obj.pri == elp.PRI_NOTE and obj.midi_ch == part_num:
                nt.append(obj)
        return nt

    def get_tick(self): # for GUI
        tick_for_beat = nlib.DEFAULT_TICK_FOR_ONE_MEASURE/self.beat[1]  # 一拍のtick数
        tick_inmsr = self.crnt_tick_inmsr
        count = self.tick_for_onemsr//tick_for_beat
        beat = tick_inmsr//tick_for_beat
        tick = tick_inmsr%tick_for_beat
        return int(self.crnt_measure),int(beat),int(tick),int(count)

    def _calc_current_tick(self, crnt_time):
        diff_time = crnt_time - self.bpm_start_time
        elapsed_tick = (480*self.bpm*diff_time)/60
        return elapsed_tick + self.bpm_start_tick

    def _play(self):
        self.bpm_start_time = self.origin_time = time.time()  # Get current time
        self.bpm_start_tick = 0
        self.beat_start_msr = 0
        self.elapsed_time = 0

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

    def _change_beat_event(self):
        # change beat event があった
        self.beat_start_msr = self.crnt_measure
        self.bpm_start_time = self.crnt_time
        self.bpm_start_tick = 0
        self.tick_for_onemsr = self.stock_tick_for_onemsr[0]
        self.beat = self.stock_tick_for_onemsr[1:3]

    def _change_bpm_event(self):
        self.bpm_start_tick = self._calc_current_tick(self.crnt_time)
        self.bpm_start_time = self.crnt_time  # Get current time
        self.bpm = self.bpm_stock


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
        ## check flags
        if self.play_for_periodic and not self.during_play:
            self.play_for_periodic = False
            self._play()
            self.during_play = True
            for sqobj in self.sqobjs:
                sqobj.start()

        if self.stop_for_periodic:
            self.stop_for_periodic = False
            self.during_play = False
            for sqobj in self.sqobjs:
                sqobj.stop()
            self._destroy_ended_obj()

        if not self.during_play:
            #self.block.no_running()
            return

        ## detect tick and measure
        self.crnt_time = time.time()
        tick_beat_starts = self._calc_current_tick(self.crnt_time)
        self.elapsed_time = self.crnt_time - self.origin_time
        former_msr = self.crnt_measure
        self.crnt_measure = tick_beat_starts//self.tick_for_onemsr + self.beat_start_msr
        self.crnt_tick_inmsr = tick_beat_starts%self.tick_for_onemsr

        ## new measure or not
        if former_msr != self.crnt_measure:
            # 小節を跨いだ場合
            if self.stock_tick_for_onemsr[0] is not self.tick_for_onemsr:
                self._change_beat_event()

            if self.bpm != self.bpm_stock:
                self._change_bpm_event()

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
            play_sqobjs = self._pick_out_play_obj(self.crnt_measure, self.crnt_tick_inmsr)
            if len(play_sqobjs) == 0:
                break
            for obj in play_sqobjs:
                obj.periodic(self.crnt_measure, self.crnt_tick_inmsr)
            unfinish_counter += 1
            if unfinish_counter > 100:
                print("Error! Unable to finish obj. exist! No.: ", play_sqobjs[0].priority)
                self._debug_disp()
                while True: pass    # 無限ループ

        ## remove ended obj
        self._destroy_ended_obj()


    def change_tempo(self, tempo):     # command thread
        self.bpm_stock = tempo

    def change_beat(self, btnum, onpu):    # beat: number of ticks of one measure
        # [1小節内のtick, 1小節内の拍数, 一拍の音価(2/4/8/16...)]
        beat = ((nlib.DEFAULT_TICK_FOR_ONE_MEASURE/onpu)*btnum, btnum, onpu)
        self.stock_tick_for_onemsr = beat

    def change_key_oct(self, key, oct, text):     # command thread
        self.key_text = text
        for i in range(nlib.MAX_PART_COUNT):
            pt = self.get_part(i)
            pt.change_key(key)
            pt.change_oct(oct, False)

    def start(self):     # command thread
        self.play_for_periodic = True
        if self.during_play:
            return False
        else:
            return True

    def stop(self):     # command thread
        self.stop_for_periodic = True

    def fine(self):     # command thread
        self.fine_for_periodic = True
