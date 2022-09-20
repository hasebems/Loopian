# -*- coding: utf-8 -*-
import expfilter as ef

class BeatFilter(ef.ExpfilterIF):

    EFFECT = 10     # bigger(1..100), stronger
    MIN_VEL = 70

    def __init__(self):
        pass

    def filtering(self, inputs, bpm, tick_for_onemsr):
        if bpm < self.MIN_VEL:
            return inputs

        # 純粋な四拍子、三拍子のみ救う
        outputs = []
        base_bpm = (bpm-self.MIN_VEL)*self.EFFECT/100
        if tick_for_onemsr == 1920:
            for dt in inputs:
                tm = (dt[0] % 1920)/480
                if tm == 0.0:
                    dt[2] += int(base_bpm)
                #elif tm == 1.0 or tm == 3.0:
                #    pass
                elif tm == 2.0:
                    dt[2] += int(base_bpm/4)
                else:
                    dt[2] -= int(base_bpm/4)
                outputs.append(dt)
        elif tick_for_onemsr == 1440:
            for dt in inputs:
                tm = (dt[0] % 1440)/480
                if tm == 0.0:
                    dt[2] += int(base_bpm)
                elif tm == 1.0:
                    dt[2] += int(base_bpm/4)
                #elif tm == 2.0:
                #    pass
                else:
                    dt[2] -= int(base_bpm/4)
                outputs.append(dt)
        return outputs
