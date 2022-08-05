# playground to implement pipetting with liquid level monitoring

from opentrons import protocol_api

metadata = {
    'protocolName': 'Liquid level tracking',
    'author': '<angel.angelov@kaust.edu.sa>',
    'apiLevel': '2.8'
}

# class VolumeTrack:
#         def __init__(self, type, location, volume):
#             self.location = location
#             self.volume = volume
#             #self.height = height
        
#         def update_vol(self, vol):
#             self.volume = self.volume - vol
#             print(f'Current volume is {self.volume} ul')

def run(ctx: protocol_api.ProtocolContext):

    epitubes = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5', 'Epi tubes')
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1']]
    s20 = ctx.load_instrument('p20_single_gen2', 'left', tip_racks=tips20_single)

    def mytransfer(vol, srctype, srcwell, desttype, destwell):

        s20.pick_up_tip()
        s20.aspirate(vol, srctype.wells_by_name()[srcwell])
        s20.dispense(vol, desttype.wells_by_name()[destwell])
        s20.drop_tip()
    
    def track_volumes(labware, init_vol):
        wells = dict(labware.wells_by_name())
        for i in wells:
            wells[i] = init_vol
        return wells
    
    sourcewells=["A1", "C1", "A1"]
    destwells=["A1","A3", "B2"]
    volumes=[10.00, 6.00, 5.00]
    
    # initialise to track these
    epiwells = track_volumes(epitubes, 100)
        
    for i, v in enumerate(sourcewells):
        
        mytransfer(volumes[i], epitubes, sourcewells[i], epitubes, destwells[i])
        epiwells[v] = epiwells[v] - volumes[i]
        
    print(epiwells)

    for i in range(10):
        s20.transfer(i, epitubes['C1'], epitubes['D1'])
        epiwells['C1'] = epiwells['C1'] - i
        print(epiwells['C1'])


