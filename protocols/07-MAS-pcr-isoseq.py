# MAS seq Iso-Seq PacBio
# doing only the MAS PCR step

from opentrons import protocol_api

metadata = {
    'protocolName': 'MAS-seq-IsoSeq.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Perform MAS-PCR from the MAS-Seq for 10x Single Cell 3 kit',
    'apiLevel': '2.13'
}

nsamples = 1
ncycles = 9
RM2well = 'D6'

if nsamples > 6:
    exit('Please use up to 6 samples')

def run(ctx: protocol_api.ProtocolContext):
    ctx.comment('Running MAS-PCR from the MAS-Seq for 10x Single Cell 3 kit')
    
    odtc = ctx.load_module(module_name='thermocyclerModuleV2')
    startblock = ctx.load_labware('opentrons_24_aluminumblock_nest_0.5ml_screwcap', '5', 'Alu block')
    pcrplate = odtc.load_labware('biorad_96_wellplate_200ul_pcr') # IMPORTANT - use biorad plates!!!

    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1']]
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['2', '3']]
    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
    m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)

    # set s20 flow rates globally, default is 7.56 
    s20.flow_rate.aspirate = 5
    s20.flow_rate.dispense = 4

    # setup ODTC
    odtc.open_lid()
    odtc.set_block_temperature(temperature = 15)
    odtc.set_lid_temperature(100)

    # distribute RM2, 2 columns per sample
    s20.distribute(
        1,
        startblock.wells_by_name()[RM2well],
        [pcrplate.columns()[v] for v in range(nsamples * 2)]
    )
