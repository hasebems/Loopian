# -*- coding: utf-8 -*-
import expfilter as ef

class BeatFilter(ef.ExpfilterIF):

    def __init__(self):
        pass

    def filtering(self, inputs, bpm, tick_for_onemsr):
        if bpm < 70:
            return inputs

        outputs = []
        if bpm > 180: bpm = 180
        base_bpm = (bpm-70)//10
        if tick_for_onemsr == 1920:
            for dt in inputs:
                tm = (dt[0] % 1920)/480
                if tm == 0.0:
                    dt[2] += base_bpm
                elif tm == 1.0 or tm == 3.0:
                    dt[2] += base_bpm//4
                elif tm == 2.0:
                    dt[2] += base_bpm//2
                outputs.append(dt)
        elif tick_for_onemsr == 1440:
            for dt in inputs:
                tm = (dt[0] % 1440)/480
                if tm == 0.0:
                    dt[2] += base_bpm
                elif tm == 1.0:
                    dt[2] += base_bpm//2
                elif tm == 2.0:
                    dt[2] += base_bpm//4
                outputs.append(dt)
        return outputs
