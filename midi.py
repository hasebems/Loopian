# -*- coding: utf-8 -*-
import pygame.midi as pmd
import time

class Midi:
    def __init__(self):
        pmd.init()  # MIDI Init
        self.all_ports = []
        self.midi_port = None
        self.scan_midi_all_port()
        self.set_midi_port(0)
        self.fifo = []

    def scan_midi_all_port(self):
        self.all_ports = []
        devnum = pmd.get_count()
        for i in range(devnum):
            dev = pmd.get_device_info(i)
            if dev[3] == 1: # MIDI Output なら
                name = dev[1].decode()
                self.all_ports.append([i,name,False])
        return self.all_ports

    def set_midi_port(self, idx):
        if idx < len(self.all_ports) and idx >= 0:
            devid = self.all_ports[idx][0]
            self.all_ports[idx][2] = True
        else:
            devid = pmd.get_default_output_id()
            for pt in self.all_ports:
                if devid == pt[0]:
                    pt[2] = True
        try:
            self.midi_port = pmd.Output(devid)
        except:
            devid = -1
        return devid

    def send_midi_note(self, ch, nt, vel):
        if nt > 127 or vel > 127: return
        if vel != 0:
            self.midi_port.note_on(nt, velocity=vel, channel=ch)
        else:
            self.midi_port.note_off(nt, channel=ch)
        #nlib.log.record(str(ch)+'-'+str(nt)+'-'+str(vel))

    def send_control(self, ch, cntnum, value):
        if ch < 16 and cntnum < 128 and value < 128:
            self.midi_port.write_short(0xb0+ch, cntnum, value)

    def send_program(self, ch, pgn):
        if ch < 16 and pgn < 128:
            self.midi_port.set_instrument(pgn, channel=ch)

    def set_fifo(self, sqtime, ev):
        sqtime += 0.05   # 50msec
        self.fifo.append([sqtime, ev])

    def periodic(self):
        crnt_time = time.time()
        while True:
            if len(self.fifo) == 0: break
            if self.fifo[0][0] > crnt_time: break

            md = self.fifo[0][1]
            if md[0] == 'note':
                self.send_midi_note(md[1],md[2],md[3])
            elif md[0] == 'damper':
                self.send_control(md[1],md[2],md[3])
            del self.fifo[0]
