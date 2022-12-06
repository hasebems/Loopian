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
import elapse_stack as elp
import lpnlib as nlib
import midi

class Loop:
    running = True

def midi_periodic(loop, midi):  # midi thread
    while True:
        midi.periodic()
        if not loop.running:
            break

def generate_ev(loop, est): # seqplay thread
    while True:
        est.periodic()
        if not loop.running:
            if est.during_play:
                est.stop()
            break

def main(): # main thread
    lp = Loop()
    log = nlib.Log()
    md = midi.Midi()
    est = elp.ElapseStack(md)
    gendt = stk.SeqDataAllStock(est)
    prs = ps.Parsing(est, md, gendt)
    gui = lpngui.LpnGui(lp, prs, log)

    md_job = threading.Thread(target=midi_periodic, args=(lp, md))
    md_job.start()
    ev_job = threading.Thread(target=generate_ev, args=(lp, est))
    ev_job.start()

    prs.midi_setting(prs.CONFIRM_MIDI_OUT_ID)
    gui.loop(est)
    log.save_file()

    ev_job.join()
    md_job.join()

if __name__ == '__main__':
    main()
