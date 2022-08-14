# playground to implement custom mixing beads
# includes transfers and mixing

from opentrons import protocol_api

metadata = {
    'protocolName': 'Mixing beads',
    'author': '<angel.angelov@kaust.edu.sa>',
    'apiLevel': '2.8'
}

def run(ctx: protocol_api.ProtocolContext):
    #pcrstrip = ctx.load_labware('')
    biorad_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '1')
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['7', '8']]
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['10']]
    m20 = ctx.load_instrument('p20_multi_gen2', 'right', tip_racks=tips20_multi)

    # for e.g. elution
    def mix_beads(vol, src_type, src_well,  dest_type, dest_well, mixvol, times = 3, zoffset = 2):
        m20.pick_up_tip()
        m20.aspirate(vol, src_type.wells_by_name()[src_well])
        m20.dispense(vol, dest_type.wells_by_name()[dest_well])

        m20.move_to(dest_type.wells_by_name()[dest_well].top(), force_direct=True)
        ctx.delay(5)
        m20.move_to(dest_type.wells_by_name()[dest_well].bottom(), force_direct=True)

        for i in range(times):
            m20.aspirate(mixvol, rate=0.5)
            m20.move_to(dest_type.wells_by_name()[dest_well].bottom(zoffset), force_direct = True)
            m20.dispense(mixvol)
            m20.move_to(dest_type.wells_by_name()[dest_well].bottom(), force_direct = True)
        m20.move_to(dest_type.wells_by_name()[dest_well].top())
        m20.drop_tip()

    mix_beads(10, biorad_plate, 'A1', biorad_plate, 'A2', 5)

