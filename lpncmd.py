# -*- coding: utf-8 -*-
#
#   lpncmd.py   Alpha Version
#
#   from September 10 2022 by M.Hasebe
#
import lpnlib as nlib

T_WATER = '\033[96m'
T_PINK = '\033[95m'
T_WHITE = '\033[97m'
T_END = '\033[0m'

class Parsing:
    #   入力した文字列の解析
    #   一行単位で入力されるたびに生成される
    def __init__(self, sqs, md, dt):
        self.sqs = sqs
        self.md = md
        self.gui = None
        self.input_part = 2 # Normal Part
        self.back_color = 2
        self.gendt = dt

    def set_gui(self, gui):
        self.gui = gui

    def print_dialogue(self, rpy):
        #print(T_PINK + rpy + T_END)    # コマンドプロンプトには出力しない
        self.gui.input_text(rpy)

    @staticmethod
    def get_complete_pattern_string(blk, part):
        ele = blk.part(part).description
        ptn_str = None
        if ele[0] == 'phrase':
            ptn_str = '[' + str(ele[1]) + '][' + str(ele[2]) + '][' + str(ele[3]) + ']'
        elif ele[0] == 'random' or ele[0] == 'arp':
            ptn_str = '{' + str(ele[1]) + '}{' + str(ele[2]) + '}{' + str(ele[3]) + '}'
        return ptn_str

    def change_beat(self, text):
        if '/' in text:
            beat_list = text.strip().split('/')
            btnum = onpu = 0
            btnum_str = beat_list[0].strip()
            if btnum_str.isdecimal():
                btnum = int(btnum_str)
            onpu_str = beat_list[1].strip()
            if onpu_str.isdecimal():
                onpu = int(onpu_str)
            if btnum >= 1 and onpu >= 1:
                self.sqs.change_beat(btnum, onpu)
                self.print_dialogue("Beat has changed!")
                return True
            else:
                self.print_dialogue("what?")
                return False

    def change_key(self, key_text):
        key = 0
        oct = nlib.NO_NOTE
        first_letter = key_text[0]
        if first_letter == 'C':
            key += 0
        elif first_letter == 'D':
            key += 2
        elif first_letter == 'E':
            key += 4
        elif first_letter == 'F':
            key += 5
        elif first_letter == 'G':
            key += 7
        elif first_letter == 'A':
            key += 9
        elif first_letter == 'B':
            key += 11
        else:
            return False
        if len(key_text) > 1:
            octave_letter = key_text[1:]
            if key_text[1] == '#':
                key += 1
                if len(key_text) > 2:
                    octave_letter = key_text[2:]
            elif key_text[1] == 'b':
                key -= 1
                if len(key_text) > 2:
                    octave_letter = key_text[2:]
            if octave_letter.isdecimal():
                oct = int(octave_letter)
        self.sqs.change_key_oct(key, oct, key_text)
        return True

    def change_oct(self, text, all):
        def generate_oct_number(text):
            octave_letter = text
            pm = 1
            if len(text) > 1:
                if text[0] == '+':
                    octave_letter = text[1:]
                elif text[0] == '-':
                    pm = -1
                    octave_letter = text[1:]
            if octave_letter.isdecimal():
                return int(octave_letter) * pm
            else:
                return 0

        if type(text) == list:
            for i, letter in enumerate(text):
                if i < nlib.MAX_NORMAL_PART:
                    oct = generate_oct_number(letter)
                    self.sqs.get_part(i+nlib.FIRST_NORMAL_PART).change_oct(oct, True)
        else:
            oct = generate_oct_number(text)
            if all:
                for i in range(nlib.FIRST_NORMAL_PART, nlib.MAX_NORMAL_PART):
                    self.sqs.get_part(i).change_oct(oct, True)
            else:
                self.sqs.get_part(self.input_part+nlib.FIRST_NORMAL_PART).change_oct(oct, True)


    def change_cc(self, cc_num, value):
#    def change_cc(self, cc_num, cc_list):
#        if len(cc_list) > nlib.MAX_NORMAL_PART:
#            del cc_list[nlib.MAX_NORMAL_PART:]
#        for i, vol in enumerate(cc_list):
#            self.sqs.get_part(i+nlib.FIRST_NORMAL_PART).change_cc(cc_num, int(vol))
        self.md.send_control(0, cc_num, value)

    CONFIRM_MIDI_OUT_ID = -1

    def midi_setting(self, num):
        if num == self.CONFIRM_MIDI_OUT_ID:
            ports = self.md.all_ports
        else:
            ports = self.md.scan_midi_all_port()
        self.print_dialogue("==MIDI OUT LIST==")
        for i, pt in enumerate(ports):
            self.print_dialogue(str(i) + ": " + str(pt[1]) + '(' + str(pt[0]) + ')')

        self.print_dialogue("==SELECTED MIDI OUT==")
        if num == self.CONFIRM_MIDI_OUT_ID:  # 設定せず、設定内容をみたい場合
            for pt in ports:
                if pt[2]:
                    self.print_dialogue(pt[1] + '(' + str(pt[0]) + ')')
        else:
            real_id = self.md.set_midi_port(num)
            if real_id != -1:
                for pt in ports:
                    if pt[0] == real_id:
                        break
                self.print_dialogue(pt[1] + '(' + str(pt[0]) + ')')
            else:
                self.print_dialogue("MIDI setting is something wrong!")

    def parse_set_command(self, input_text):
        prm_text = input_text.strip()
        if '=' in prm_text:
            tx = prm_text.split('=',2)
        else:
            return

        command = tx[0].strip()
        if command == 'key':
            key_list = tx[1].strip().split()
            if self.change_key(key_list[0]):
                self.gendt.set_recombined()
                self.print_dialogue("Key has changed!")
            else:
                self.print_dialogue("what?")
        elif command == 'oct':
            if ',' in tx[1]:
                oct_list = tx[1].strip().split(',')
                self.change_oct(oct_list, True)
            else:
                oct_list = tx[1].strip().split()
                self.change_oct(oct_list[0], 'all' in prm_text)
            self.gendt.set_recombined()
            self.print_dialogue("Octave has changed!")
        elif command == 'beat':
            beat_list = tx[1].strip().split()
            if self.change_beat(beat_list[0]):
                self.gendt.set_recombined()
            else:
                self.print_dialogue("what?")
        elif command == 'bpm':
            bpmnumlist = tx[1].strip().split()
            if bpmnumlist[0].isdecimal():
                self.sqs.change_tempo(int(bpmnumlist[0]))
                self.gendt.set_recombined()
                self.print_dialogue("BPM has changed!")
            else:
                self.print_dialogue("what?")
        else:
            self.print_dialogue("what?")

#        elif command == 'balance' or command == 'volume':
#            bl_list = tx[1].strip().split(',')
#            cc_list = [88 for _ in range(5)] # default: 7
#            for i, var in enumerate(bl_list):
#                if var.isdecimal():
#                    cc_list[i] = int(int(var)*12.7)
#            self.change_cc(7, cc_list)
#            self.print_dialogue("Balance has changed!")
#        elif command == 'pan':
#            bl_list = tx[1].strip().split(',')
#            cc_list = [64 for _ in range(5)] # default: C
#            for i, var in enumerate(bl_list):
#                try:
#                    pan = int(PAN_TRANS_TBL.index(var) * 6.4)
#                    cc_list[i] = pan if pan <= 127 else 127
#                except ValueError as error:
#                    continue
#            self.change_cc(10, cc_list)
#            self.print_dialogue("Pan has changed!")

    def parse_sync_command(self, input_text):
        prm_text = input_text.strip()
        if prm_text == '':
            self.sqs.get_part(self.input_part+nlib.FIRST_COMPOSITION_PART).sync()
            self.sqs.get_part(self.input_part+nlib.FIRST_NORMAL_PART).sync()
            self.print_dialogue("Synchronized!")
        elif prm_text == 'all':
            for i in range(nlib.MAX_PART_COUNT):
                self.sqs.get_part(i).sync()
            self.print_dialogue("All Part Synchronized!")
        elif prm_text == 'right':
            for i in range(nlib.MAX_LEFT_PART, nlib.MAX_LEFT_PART+nlib.MAX_RIGHT_PART):
                self.sqs.get_part(nlib.FIRST_COMPOSITION_PART+i).sync()
                self.sqs.get_part(nlib.FIRST_NORMAL_PART+i).sync()
            self.print_dialogue("Right Part Synchronized!")
        elif prm_text == 'left':
            for i in range(0, nlib.MAX_LEFT_PART):
                self.sqs.get_part(nlib.FIRST_COMPOSITION_PART+i).sync()
                self.sqs.get_part(nlib.FIRST_NORMAL_PART+i).sync()
            self.print_dialogue("Left Part Synchronized!")
        else:
            self.print_dialogue("what?")
            return

    def letterA(self, input_text):
        if input_text[0:3] == "all":
            self.input_part = nlib.ALL_PART
            self.gui.change_part(self.input_part)
            self.print_dialogue('Changed current part to all')
        else:
            self.print_dialogue("what?")

    def letterB(self, input_text):
        self.print_dialogue("what?")

    def letterP(self, input_text):
        if input_text[0:4] == 'play':
            arg = input_text.split()
            if len(arg) == 1:
                well_done = self.sqs.start()
                if well_done:
                    self.print_dialogue("Phrase has started!")
                else:
                    self.print_dialogue("Unable to start!")
        elif input_text[0:5] == 'panic':
            #for i in range(nlib.FIRST_NORMAL_PART, nlib.MAX_NORMAL_PART):
            self.change_cc(120, 0)
        else:
            self.print_dialogue("what?")

    def letterS(self, input_text):
        if input_text[0:5] == 'start':
            well_done = self.sqs.start()
            if well_done:
                self.print_dialogue("Phrase has started!")
            else:
                self.print_dialogue("Unable to start!")
        elif input_text[0:4] == 'stop':
            self.sqs.stop()
            self.print_dialogue("Stopped!")
        elif input_text[0:3] == 'set':
            self.parse_set_command(input_text[3:])
        elif input_text[0:4] == 'sync':
            self.parse_sync_command(input_text[4:])
        else:
            self.print_dialogue("what?")

    def letterI(self, input_text):
        self.print_dialogue("what?")

    def letterC(self, input_text):
        if input_text[0:6] == 'copyto':
            tx = input_text[7:].replace(' ', '')
            if tx.isdecimal():
                part = int(tx)
                if 0 < part <= nlib.MAX_NORMAL_PART:
#                    self.sq.blk().copy_phrase(part - 1)
                    self.print_dialogue("Phrase copied to part" + tx + ".")
        elif input_text[0:5] == 'color':
            color = input_text[6:].replace(' ','')
            if color.isdecimal() and int(color) < 3:
                self.back_color = int(color)
                self.print_dialogue("Back color has changed!")
        else:
            self.print_dialogue("what?")

    def letterF(self, input_text):
        if input_text[0:4] == "fine":
            self.sqs.fine()
            self.print_dialogue('Will be ended!')
        else:
            self.print_dialogue("what?")

    def letterR(self, input_text):
        if input_text[0:5] == 'right':
            tx = input_text[5:].replace(' ', '')
            if tx.isdecimal():
                part = int(tx)
                if part == 1 or part == 2:
                    self.print_dialogue("Changed current part to right " + str(part) + ".")
                    self.input_part = part + 1
                    self.gui.change_part(self.input_part)

    def letterQm(self, input_text):
        self.print_dialogue("what?")

    def letterM(self, input_text):
        if input_text[0:4] == "midi":
            picked_txt = input_text[input_text.find('midi') + 4:].strip().split()
            if picked_txt and picked_txt[0].isdecimal():
                self.midi_setting(int(picked_txt[0]))
            else:
                self.midi_setting(self.CONFIRM_MIDI_OUT_ID)

    def letterL(self, input_text):
        if input_text[0:4] == "load":
            self.print_dialogue("what?")

        elif input_text[0:4] == 'left':
            tx = input_text[4:].replace(' ', '')
            if tx.isdecimal():
                part = int(tx)
                if part == 1 or part == 2:
                    self.print_dialogue("Changed current part to left " + str(part) + ".")
                    self.input_part = part - 1
                    self.gui.change_part(self.input_part)

    def letter_plus(self, input_text):
        success = False
        if self.input_part != nlib.ALL_PART:
            tx = input_text.strip()
            if tx[1] == '[':
                success = self.gendt.set_raw_phrase(self.input_part, input_text)
                if success: self.print_dialogue("set Phrase!")
            elif tx[1] == '{':
                success = self.gendt.set_raw_composition(self.input_part, input_text)
                if success: self.print_dialogue("set Composition!")
        if not success:
            self.print_dialogue("what?")

    def letter_bracket(self, input_text):
        success = False
        if self.input_part == nlib.ALL_PART:
            for i in range(nlib.MAX_NORMAL_PART):
                success = self.gendt.set_raw_phrase(i, input_text)
        else:
            success = self.gendt.set_raw_phrase(self.input_part, input_text)
        if success:
            self.print_dialogue("set Phrase!")
        else:
            self.print_dialogue("what?")

    def letter_brace(self, input_text):
        success = False
        if self.input_part == nlib.ALL_PART:
            for i in range(nlib.MAX_COMPOSITION_PART):
                success = self.gendt.set_raw_composition(i, input_text)
        else:
            success = self.gendt.set_raw_composition(self.input_part, input_text)
        if success:
            self.print_dialogue("set Composition!")
        else:
            self.print_dialogue("what?")

    def start_parsing(self, input_text):
        first_letter = input_text[0:1]
        if first_letter == '+':
            self.letter_plus(input_text)
        elif first_letter == '[':
            self.letter_bracket(input_text)
        elif first_letter == '{':
            self.letter_brace(input_text)
        elif first_letter == 'a':
            self.letterA(input_text)
        elif first_letter == 'b':
            self.letterB(input_text)
        elif first_letter == 'c':
            self.letterC(input_text)
        elif first_letter == 'f':
            self.letterF(input_text)
        elif first_letter == 'i':
            self.letterI(input_text)
        elif first_letter == 'l':
            self.letterL(input_text)
        elif first_letter == 'p':
            self.letterP(input_text)
        elif first_letter == 'r':
            self.letterR(input_text)
        elif first_letter == 's':
            self.letterS(input_text)
        elif first_letter == 'm':
            self.letterM(input_text)
        elif first_letter == '?':
            self.letterQm(input_text)
        else:
            self.print_dialogue("what?")
