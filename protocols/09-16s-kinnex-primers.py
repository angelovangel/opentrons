# Prepare 16S (Kinnex) PCR primers in plates from original tubes
# Conc in tubes is 100 pM, final conc is

from opentrons import protocol_api

metadata = {
    'protocolName': '09-16s-kinnex-primers.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Prepare 16S (Kinnex) PCR primers in plates from original tubes',
    'apiLevel': '2.15'
}

def run(ctx: protocol_api.ProtocolContext):
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1', '2', '3']]
    #tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3']]
    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
    #m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)

    rack1 = ctx.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '4', 'Primer rack 1') # for primers and water at D6
    rack2 = ctx.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '5', 'Primer rack 2') # original stocks at 100 uM
    mixplate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '6', 'Primer mix plate') # mixing plate at 10 uM each
    primerplate1 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '9', 'Primerplate 2')

    odtc = ctx.load_module(module_name='thermocyclerModuleV2') # not used here
    # # add water water in mixing plate
    # s300.distribute(
    #     80,
    #     rack1['D6'],
    #     mixplate.wells()
    # )

    # distribute forward primers
    forprimers = list(rack1.wells_by_name().keys())[:12]
    for i,v in enumerate(forprimers):
        s20.transfer(
            10,
            rack1[v],
            mixplate.columns()[i],
            new_tip = 'always', 
            air_gap = 1
        )
    
    # transfer rev primers
    revprimers = list(rack2.wells_by_name().keys())[:8]
    for i,v in enumerate(revprimers):
        s20.transfer(
            10,
            rack2[v],
            mixplate.rows()[i],
            new_tip = 'always',
            air_gap = 1
        )   
    