# playground to implement pipetting with liquid level monitoring

from opentrons import protocol_api

metadata = {
    'protocolName': 'Liquid level tracking',
    'author': '<angel.angelov@kaust.edu.sa>',
    'apiLevel': '2.8'
}

class VolumeTrack:
        def __init__(self, type, well, volume, height):
            self.type = type
            self.well = well
            self.volume = volume
            self.height = height
        
        def update_vol(self, vol):
            self.volume = self.volume - vol
            print(f'Current volume is {self.volume} ul')

def run(ctx: protocol_api.ProtocolContext):

    epitubes = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5', 'Epi tubes')
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1']]
    s20 = ctx.load_instrument('p20_single_gen2', 'left', tip_racks=tips20_single)

    def mytransfer(vol, src, dest):
        if vol <= 0: return
        s20.pick_up_tip()
        s20.aspirate()

