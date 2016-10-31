#!/usr/bin/env python

import os
import mmap
import struct

prescal_map={
    0b0000: 120,
    0b0001: 180,
    0b0010: 240,
    0b0011: 360,
    0b0100: 480,
    0b1000: 12000,
    0b1001: 24000,
    0b1010: 36000,
    0b1011: 48000,
    0b1100: 72000,
    0b1111: 1}

class PWM(object):
    def __init__(self, freq=1000):
        self.is_run=0
        self.calc_params( freq)
        self.mem_config()

    def reset_params(self, freq):
        self.calc_params( freq)
        self.mem_config()
        if self.is_run:
            self.run()

    def calc_params(self, freq):
        self.prescal=-1
        for prsc in prescal_map.keys():
            if (self.prescal<0 or 24000000/prescal_map[prsc]/freq-200<delta) and 24000000/prescal_map[prsc]/freq-200>=0:
                 delta = 24000000/prescal_map[prsc]/freq-200
                 self.prescal=prsc
        if self.prescal==-1:
            self.prescal=15
        self.interval_ticks = 24000000//prescal_map[self.prescal]//freq

    def set_duty(self, duty):
        self.duty_ticks=duty*self.interval_ticks//100
        if self.is_run:
            self.run()
                 
    def mem_config(self):

        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)

        pin_mem = mmap.mmap(f, 0x1000, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=0x01C20000)
        pin_mem.seek(0x800,0)
        data=(struct.unpack('I', pin_mem.read(4))[0])
        data = data | (3 << 20)
        data = data & ~(1 << 22)
        pin_mem.seek(0x800,0)
        pin_mem.write(struct.pack('I', data))        

        pwm_mem = mmap.mmap(f, 0x1000, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=0x01C21000)
        data = 19<<4
        data = data | self.prescal
        pwm_mem.seek(0x400,0)
        pwm_mem.write(struct.pack('I', data))

    def run(self):

        self.is_run=1
        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)

        pwm_mem = mmap.mmap(f, 0x1000, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=0x01C21000)
        pwm_mem.seek(0x400,0)
        data=(struct.unpack('I', pwm_mem.read(4))[0])
        data = data | 1<<6
        pwm_mem.seek(0x400,0)
        pwm_mem.write(struct.pack('I', data))

        pwm_mem.seek(0x404,0)
        cycle_data=self.interval_ticks<<16 | self.duty_ticks
        pwm_mem.write(struct.pack('I', cycle_data))

    def stop(self):

        self.is_run=0
        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)

        pwm_mem = mmap.mmap(f, 0x1000, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=0x01C21000)
        pwm_mem.seek(0x400,0)
        data=(struct.unpack('I', pwm_mem.read(4))[0])
        data = data & ~(1<<6)
        pwm_mem.seek(0x400,0)
        pwm_mem.write(struct.pack('I', data))





test=PWM(2000)
test.set_duty(30)
test.run()