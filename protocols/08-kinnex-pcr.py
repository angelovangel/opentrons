# Kinnex PCR protocol
# doing only the Kinnex step for PacBio 16S (103-072-100), full-length RNA (103-072-000) or single-cell RNA (103-072-200)
# Kinnex arrays - 16S = 12X, full-length RNA = 8X, single-cell RNA = 16X
# max 6 samples
# empty 1.5 ml tubes in A5..B6 of rack to collect pools after PCR 
# the Kinnex primer mixes go in A1..D4 of 2 ml aluminium block

from opentrons import protocol_api

metadata = {
    'protocolName': '08-kinnex-pcr.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Perform Kinnex-PCR for the PacBio 16S, full-length RNA or single-cell RNA kits',
    'apiLevel': '2.13'
}
#================================================================
ncycles = 9
primervol = 2.5
MMvol = 22.5
MMwells = ['A1', 'B1', 'C1'] # on rack
#MMwells = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2'] # on rack
poolwells = ['A5', 'B5', 'C5'] # on rack
nsamples = len(MMwells)
primerwells = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2', 'A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4'] # on block
# for building the wells to distribute to, based on MMwell index and plex
# works for any plex number
plex = 12
rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


pcrprofile = [
    {'temperature':98, 'hold_time_seconds':20},
    {'temperature':68, 'hold_time_seconds':30},
    {'temperature':72, 'hold_time_seconds':240}
    ]
#================================================================

if nsamples > 6 | nsamples < 1:
    exit('Please use up to 6 samples')
if len(MMwells) != len(poolwells):
    exit('Sample and pool wells do not match!')

def run(ctx: protocol_api.ProtocolContext):
    ctx.comment('Running Kinnex PCR')
    ctx.comment('--------------------------------')
    ctx.comment('Total number of samples: ' + str(nsamples) + ' in wells ' + str(MMwells))
    ctx.comment('--------------------------------')
    
    odtc = ctx.load_module(module_name='thermocyclerModuleV2')
    primerblock = ctx.load_labware('opentrons_24_aluminumblock_nest_0.5ml_screwcap', '5', 'Alu block')
    int_primerplate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '4','Intermediate primer plate')
    rack = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '9', 'MM tube rack')
    pcrplate = odtc.load_labware('biorad_96_wellplate_200ul_pcr') # IMPORTANT - use biorad plates!!!

    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1', '2']]
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3']]
    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
    m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)

    # set s20 flow rates globally, default is 7.56 
    # s20.flow_rate.aspirate = 5
    # s20.flow_rate.dispense = 4

    # setup ODTC
    odtc.open_lid()
    odtc.set_block_temperature(temperature = 15)
    odtc.set_lid_temperature(100)

    
    # distribute MM
    for i, v in enumerate(MMwells):
        distribute_wells =  [ j + str(i*2 + 1) for j in rows ] + [ j + str(i*2 + 2) for j in rows ]
        ctx.comment('Distributing sample ' + str(MMwells[i]) + ' in PCR plate wells:')
        ctx.comment(str(distribute_wells[:plex]))
        ctx.comment("--------------------------------------")
        s20.distribute(
            MMvol,
            rack.wells_by_name()[v],
            [pcrplate.wells_by_name()[well] for well in distribute_wells[:plex]], 
            air_gap = 1, 
            disposal_volume = 0
            #blow_out = False, 
            #blowout_location = 'destination well' # blowout is required in distribute
        )

    # Transfer primers from block to intermediate plate
    ctx.comment("Transfer primers from block to intermediate plate")
    ctx.comment("--------------------------------------")
    thisvolume = primervol * nsamples * 1.1
    s20.transfer(
        thisvolume,
        [primerblock[well] for well in primerwells[:plex]],
        int_primerplate.wells()[:plex], 
        mix_before = (3, thisvolume/2), 
        new_tip = 'always'
    )
    ctx.comment("--------------------------------------")

    # Add primers with multichannel
    for i in range(nsamples):
        samplecols = 'A' + str(i*2 + 1)
        ctx.comment('Add primers to PCR plate for sample ' + MMwells[i])
        ctx.comment('--------------------------------------')
        m20.transfer(
            primervol,
            int_primerplate['A1'],
            pcrplate.wells_by_name()[samplecols],
            mix_before = (1, primervol),
            mix_after = (3, (MMvol + primervol)/2),
            blow_out = True,
            blowout_location = 'destination well'
        )
        if plex > 8:
            samplecols = 'A' + str(i*2 + 2)
            m20.transfer(
                primervol,
                int_primerplate['A2'],
                pcrplate.wells_by_name()[samplecols],
                mix_before = (1, primervol),
                mix_after = (3, (MMvol + primervol)/2),
                blow_out = True,
                blowout_location = 'destination well'
            )
        ctx.comment('--------------------------------------')


    # # Primer mix addition
    # for i in range(nsamples):
    #     distribute_wells =  [ j + str(i*2 + 1) for j in rows ] + [ j + str(i*2 + 2) for j in rows ]
    #     if len(distribute_wells[:plex]) != len(primerwells[:plex]):
    #         exit('Primer and PCR plate wells do not match!')
    #     ctx.comment('Adding primers to wells:')
    #     ctx.comment(str(distribute_wells[:plex]))
    #     ctx.comment("--------------------------------------")
    #     s20.transfer(
    #         primervol,
    #         [primerblock[well] for well in primerwells[:plex]],
    #         [pcrplate[well] for well in distribute_wells[:plex]], 
    #         new_tip = 'always', 
    #         air_gap = 1,
    #         mix_after = (3, 15), 
    #         blow_out = False
    #         )

    # PCR
    ctx.pause("Optional pause to cover plate with aluminum foil") 
    odtc.close_lid()
    odtc.set_block_temperature(temperature=98, hold_time_minutes=3)
    odtc.execute_profile(steps=pcrprofile, repetitions=ncycles, block_max_volume=20)
    odtc.set_block_temperature(temperature=72, hold_time_minutes=5)
    odtc.set_block_temperature(10)
    odtc.open_lid()
    odtc.deactivate_lid()
    ctx.comment("--------------------------------------")

    # # Consolidate PCRs
    for i, v in enumerate(poolwells):
        distribute_wells =  [ j + str(i*2 + 1) for j in rows ] + [ j + str(i*2 + 2) for j in rows ]
        ctx.comment("Consolidating PCR wells " + str(distribute_wells[:plex]) + ' into pool well ' + v)
        ctx.comment("--------------------------------------")
        s20.consolidate(
            MMvol+primervol, 
            [pcrplate[well] for well in distribute_wells[:plex]], 
            rack.wells_by_name()[v]
        )
        ctx.comment("--------------------------------------")

    ctx.comment('--------------------------------')
    ctx.comment('Kinnex-PCR done! PCR will stay at 10˚C, turn it off manually')
    ctx.comment('--------------------------------')
