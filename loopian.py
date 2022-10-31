# -*- coding: utf-8 -*-
#
#   loopian.py   Alpha Version
#
#   from September 2 2022 by M.Hasebe
#
import threading
import lpngui
import seqdt_stock as stk
import lpncmd as ps
import elapse_stack as sqs
import lpnlib as nlib
import midi

class Loop:
    running = True

def midi_periodic(loop, midi):
    while True:
        midi.periodic()
        if not loop.running:
            break

def generate_ev(loop, fl, seq, prs):
    while True:
        seq.periodic()
#        if fl.auto_stop:   # check end of chain loading
#            fl.auto_stop = False
#            chain_load_auto_stop(seq, prs)
        if not loop.running:
            if seq.during_play:
                seq.stop()
            break

def main():
    lp = Loop()
    log = nlib.Log()
    md = midi.Midi()
    seq = sqs.SeqStack(md)
    gendt = stk.SeqDataAllStock(seq)
    prs = ps.Parsing(seq, md, gendt)
    gui = lpngui.LpnGui(lp, prs, log)

    md_job = threading.Thread(target=midi_periodic, args=(lp, md))
    md_job.start()
    ev_job = threading.Thread(target=generate_ev, args=(lp, None, seq, prs))
    ev_job.start()

    prs.midi_setting(prs.CONFIRM_MIDI_OUT_ID)
    gui.loop(seq)
    log.save_file()

    ev_job.join()
    md_job.join()

if __name__ == '__main__':
    main()
