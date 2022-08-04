# playground to implement pipetting with liquid level monitoring

from opentrons import protocol_api

metadata = {
    'protocolName': 'Liquid level tracking',
    'author': '<angel.angelov@kaust.edu.sa>',
    'apiLevel': '2.8'
}

def run(ctx: protocol_api.ProtocolContext):

    epitubes = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5', 'Epi tubes')
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1']]
    s20 = ctx.load_instrument('p20_single_gen2', 'left', tip_racks=tips20_single)

    class LevelTransfer:
        def __init__(self, volume, height):
            self.volume = volume
            self.height = height
        
        def aspirate(self, vol):
            s20.aspirate
