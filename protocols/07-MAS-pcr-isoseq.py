# MAS seq Iso-Seq PacBio
# doing only the MAS PCR step
# prepare 1 RM2 for each sample and place in A1..B2 of rack - max 6 samples
# empty 1.5 ml tubes in A5..B6 of rack to collect pools after PCR 
# the 16 primer mixes go in A1..D4 of 2 ml aluminium block

from opentrons import protocol_api

metadata = {
    'protocolName': 'MAS-seq-IsoSeq.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Perform MAS-PCR from the MAS-Seq for 10x Single Cell 3 kit',
    'apiLevel': '2.13'
}
#================================================================
ncycles = 1
primervol = 2
RM2vol = 18
RM2wells = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2'] # on rack
poolwells = ['A5', 'B5', 'C5', 'D5', 'A6', 'B6'] # on rack
nsamples = len(RM2wells)
primerwells = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2', 'A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4'] # on block

pcrprofile = [
    {'temperature':98, 'hold_time_seconds':20},
    {'temperature':68, 'hold_time_seconds':30},
    {'temperature':72, 'hold_time_seconds':240}
    ]
#================================================================

if nsamples > 6 | nsamples < 1:
    exit('Please use up to 6 samples')

def run(ctx: protocol_api.ProtocolContext):
    ctx.comment('Running MAS-PCR from the MAS-Seq for 10x Single Cell 3 kit')
    ctx.comment('--------------------------------')
    ctx.comment('Total number of samples: ' + str(nsamples) + ' in wells ' + str(RM2wells))
    ctx.comment('--------------------------------')
    
    odtc = ctx.load_module(module_name='thermocyclerModuleV2')
    startblock = ctx.load_labware('opentrons_24_aluminumblock_nest_0.5ml_screwcap', '4', 'Alu block')
    rack = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5', 'Tube rack')
    pcrplate = odtc.load_labware('biorad_96_wellplate_200ul_pcr') # IMPORTANT - use biorad plates!!!

    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1', '2']]
    #tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['2', '3']]
    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
    #m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)

    # set s20 flow rates globally, default is 7.56 
    # s20.flow_rate.aspirate = 5
    # s20.flow_rate.dispense = 4

    # setup ODTC
    odtc.open_lid()
    odtc.set_block_temperature(temperature = 15)
    odtc.set_lid_temperature(100)

    # distribute RM2 in 2 subsequent columns per sample
    for i, v in enumerate(RM2wells):
        ctx.comment('Distributing sample ' + str(RM2wells[i]))
        ctx.comment("--------------------------------------")
        s20.distribute(
            RM2vol,
            rack.wells_by_name()[v],
            [pcrplate.columns()[col + i*2] for col in range(2)], 
            blow_out = True, 
            blowout_location = 'source well' # blowout is required in distribute
        )
    # Primer mix addition
    for i in range(nsamples):
        ctx.comment("Adding primermix to pcrplate")
        ctx.comment("--------------------------------------")
        s20.transfer(
            primervol,
            [startblock.wells_by_name()[well] for well in primerwells[:8]],
            pcrplate.columns()[i*2], 
            new_tip = 'always', 
            mix_after = (3, 10), 
            blow_out = False
        )
        s20.transfer(
            primervol,
            [startblock.wells_by_name()[well] for well in primerwells[8:]],
            pcrplate.columns()[i*2 + 1],
            new_tip = 'always',
            mix_after = (3, 10), 
            blow_out = False
        )

    # PCR
    odtc.close_lid()
    odtc.set_block_temperature(temperature=98, hold_time_minutes=3)
    odtc.execute_profile(steps=pcrprofile, repetitions=ncycles, block_max_volume=20)
    odtc.set_block_temperature(temperature=72, hold_time_minutes=5)
    odtc.set_block_temperature(10)
    odtc.open_lid()
    odtc.deactivate_lid()
    ctx.comment("--------------------------------------")

    # Consolidate PCRs
    for i, v in enumerate(poolwells):
        ctx.comment("Consolidating sample " + str(RM2wells[i]) + ' into ' + v)
        ctx.comment("--------------------------------------")
        s20.consolidate(
            RM2vol+primervol, 
            [pcrplate.columns()[col + i*2] for col in range(2)], 
            rack.wells_by_name()[v]
        )
        ctx.comment("--------------------------------------")

    ctx.comment('--------------------------------')
    ctx.comment('MAS-PCR done! PCR will stay at 10˚C, turn it off manually')
    ctx.comment('--------------------------------')
