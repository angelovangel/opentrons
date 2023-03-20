# reformat 384 plate to 4x 96 plates

from opentrons import protocol_api

metadata = {
    'protocolName': 'reformat-384-96.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Reformat one 384-well to four 96-well plates',
    'apiLevel': '2.8'
}


def run(ctx: protocol_api.ProtocolContext): 
    ctx.comment('Starting reformat')

    source = ctx.load_labware('biorad_384_wellplate_50ul', '9', '384 plate')
    dest1 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '4', 'plate A')
    dest2 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '5', 'plate B')
    dest3 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '6', 'plate C')
    dest4 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '1', 'plate D')

    tips20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['7', '8', '10', '11']]
    m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20)

    # 
    
    
    m20.transfer(
        12, 
        source.rows_by_name()['A'][:12], 
        dest1.columns(), 
        new_tip = 'always'
    )
   
    m20.transfer(
        12,
        source.rows_by_name()['A'][-12:],
        dest2.columns(),
        new_tip = 'always'
    )
    m20.transfer(
        12, 
        source.rows_by_name()['B'][:12], 
        dest3.columns(),
        new_tip = 'always'
    )
    m20.transfer(
        12, 
        source.rows_by_name()['B'][-12:], 
        dest4.columns(),
        new_tip = 'always'
    )