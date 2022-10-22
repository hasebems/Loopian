# -*- coding: utf-8 -*-
import datetime
import random

REST = 1000
NO_NOTE = 1001
DEFAULT_TICK_FOR_ONE_MEASURE = 1920  # 480 * 4
END_OF_DATA = -1
ALL_PART = -1

MIDI_OUTPUT_PORT_NAME = 'IAC Driver WebMIDI'
DEFAULT_BPM = 100
DEFAULT_NOTE_NUMBER = 60    # C4

MAX_LEFT_PART = 2
MAX_RIGHT_PART = 2
MAX_PART = MAX_LEFT_PART+MAX_RIGHT_PART

FIRST_COMPOSITION_PART = 0
MAX_COMPOSITION_PART = MAX_PART     # Normal と対応する同数のパート

FIRST_NORMAL_PART = MAX_COMPOSITION_PART
MAX_NORMAL_PART = MAX_PART          # Composition と対応

DAMPER_PEDAL_PART = MAX_COMPOSITION_PART+MAX_NORMAL_PART
MAX_PART_COUNT = MAX_COMPOSITION_PART+MAX_NORMAL_PART+1

DEFAULT_VEL = 100


#=====================
# seq data index (seqdt)
#=====================
TYPE = 0
TICK = 1
DUR = 2
# for 'note' : ['note', $TICK, $DUR, $NOTE, $VEL]
NOTE = 3
VEL = 4
# for 'damper' : ['damper', $TICK, $DUR, $VAL]
VAL = 3
# for 'chord' : ['chord', $TICK, $CHORD ]
CHORD = 2

# for analised
ARP_NTCNT = 0
ARP_DT = 4

#=====================
# Chord Text Table
#=====================
ROOT_NAME = ('I','II','III','IV','V','VI','VII')
CHORD_SCALE = {  # ±2オクターブ分
    'thru':     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    '_':        [0, 4, 7],
    '_m':       [0, 3, 7],
    '_7':       [0, 4, 7, 10],
    '_6':       [0, 4, 7, 9],
    '_m7':      [0, 3, 7, 10],
    '_M7':      [0, 4, 7, 11],
    '_maj7':    [0, 4, 7, 11],
    '_add9':    [0, 2, 4, 7],
    '_9':       [0, 2, 4, 7, 10],
    '_m9':      [0, 2, 3, 7, 10],
    '_M9':      [0, 2, 4, 7, 11],
    '_maj9':    [0, 2, 4, 7, 11],
    '_+5':      [0, 4, 8],
    '_aug':     [0, 4, 8],
    '_7+5':     [0, 4, 8],
    '_aug7':    [0, 4, 8],
    '_7-9':     [0, 1, 4, 7, 10],
    '_7+9':     [0, 3, 4, 7, 10],
    '_dim':     [0, 3, 6, 9],
    '_m7-5':    [0, 3, 6, 10],
    '_sus4':    [0, 5, 7],
    '_7sus4':   [0, 5, 7, 10],
    'diatonic': [0, 2, 4, 5, 7, 9, 11],
    'dorian':   [0, 2, 3, 5, 7, 9, 10],
    'lydian':   [0, 2, 4, 6, 7, 9, 11],
    'mixolydian':[0, 2, 4, 5, 7, 9, 10],
    'aeolian':  [0, 2, 3, 5, 7, 8, 10],
    'comdim':   [0, 2, 3, 5, 6, 8, 9, 11],
    'pentatonic':[0, 2, 4, 7, 9],
    'none': [1000, 1001]  # if more than 127, no sound by limit
}


def search_scale_nt_just_above(root, tbl, nt):
    # nt の音程より上にある(nt含む)、一番近い root/tbl の音程を探す
    scale_nt = 0
    octave = -1
    while nt > scale_nt:    # Octave 判定
        octave += 1
        scale_nt = root + octave*12

    scale_nt = 0
    octave -= 1
    cnt = -1
    while nt > scale_nt:    # Table index 判定
        cnt += 1
        if cnt >= len(tbl):
            octave += 1
            cnt = 0
        scale_nt = root + tbl[cnt] + octave*12
    return scale_nt 


def search_scale_nt_just_below(root, tbl, nt):
    # nt の音程から下にある(nt含む)、一番近い root/tbl の音程を探す    
    scale_nt = 0
    octave = -1
    while nt > scale_nt:    # Octave 判定
        octave += 1
        scale_nt = root + octave*12

    scale_nt = 127
    octave -= 1
    cnt = len(tbl)
    while nt < scale_nt:    # Table index 判定
        cnt -= 1
        if cnt < 0:
            octave -= 1
            cnt = len(tbl)-1
        scale_nt = root + tbl[cnt] + octave*12
    return scale_nt


def gauss_rnd10():
    rnd = random.gauss(0,1)
    return rnd*3

def convert_doremi(doremi_str):
    if doremi_str == '': return 0

    # 最初に +/-/++/-- がある場合、オクターブ(+12/-12/+24/-24)とみなす
    # +/- を抜いた文字列の最初の一文字、あるいは二文字が移動ドなら、その音程を返す
    base_pitch = 0
    pm_sign = doremi_str[0]
    nx = doremi_str
    if pm_sign == '+':  # octave up
        if doremi_str[1] == '+':
            nx = doremi_str[2:]
            base_pitch += 24
        else:
            nx = doremi_str[1:]
            base_pitch += 12
    elif pm_sign == '-':  # octave down
        if doremi_str[1] == '-':
            nx = doremi_str[2:]
            base_pitch -= 24
        else:
            nx = doremi_str[1:]
            base_pitch -= 12
    else:
        pass

    if len(nx) > 1:
        l2 = nx[1]
    else:
        l2 = None
    if l2 is None or (l2 != 'i' and l2 != 'a' and l2 != 'o'):
        l1 = nx[0]
        if l1 == 'x':
            base_pitch = REST
        elif l1 == 'd':
            base_pitch += 0
        elif l1 == 'r':
            base_pitch += 2
        elif l1 == 'm':
            base_pitch += 4
        elif l1 == 'f':
            base_pitch += 5
        elif l1 == 's':
            base_pitch += 7
        elif l1 == 'l':
            base_pitch += 9
        elif l1 == 't':
            base_pitch += 11
    else:
        l12 = nx[0:2]
        if l12 == 'di' or l12 == 'ra':
            base_pitch += 1
        elif l12 == 'ri' or l12 == 'ma':
            base_pitch += 3
        elif l12 == 'fi' or l12 == 'sa':
            base_pitch += 6
        elif l12 == 'si' or l12 == 'lo':
            base_pitch += 8
        elif l12 == 'li' or l12 == 'ta':
            base_pitch += 10

    return base_pitch


def limit(num, min_value, max_value):
    if num > max_value:
        num = max_value
    elif num < min_value:
        num = min_value
    return num


def note_limit(num, min_value, max_value):
    while num > max_value:
        num -= 12
    while num < min_value:
        num += 12
    return num


class Log:

    def __init__(self):
        self.log_text = ['Start Log\n']

    def record(self, log_str):
        date = datetime.datetime.now()
        add_str = str(date) + ' : ' + log_str + '\n'
        self.log_text.append(add_str)
        while len(self.log_text) > 200:
            del self.log_text[0]

    def save_file(self):
        self.log_text.append('End Log')
        with open("log.txt", mode='w') as lf:
            for lstr in self.log_text:
                lf.write(lstr)
