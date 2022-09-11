# -*- coding: utf-8 -*-
#
#   loopian.py   Alpha Version
#
#   from September 2 2022 by M.Hasebe
#
import threading
import lpngui
import lpncmd as ps
import stack as sqs
import midi

class Loop:
    running = True

def generate_ev(loop, fl, seq, pas):
    while True:
        seq.periodic()
#        if fl.auto_stop:   # check end of chain loading
#            fl.auto_stop = False
#            chain_load_auto_stop(seq, pas)
        if not loop.running:
            if seq.during_play:
                seq.stop()
            break

def main():
    lp = Loop()
    gui = lpngui.LpnGui(lp)
    md = midi.Midi()
    seq = sqs.SeqStack(None,md)
    prs = ps.Parsing(seq, None, md, gui)
    ev_job = threading.Thread(target=generate_ev, args=(lp, None, seq, prs))
    ev_job.start()
    prs.midi_setting(prs.CONFIRM_MIDI_OUT_ID)

    gui.loop(seq)
    ev_job.join()

if __name__ == '__main__':
    main()
