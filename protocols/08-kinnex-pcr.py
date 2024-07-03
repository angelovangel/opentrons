# Kinnex PCR protocol for OT2
# doing only the Kinnex step for PacBio 16S (103-072-100), full-length RNA (103-072-000) or single-cell RNA (103-072-200)
# Kinnex segments - 16S = 12X, full-length RNA = 8X, single-cell RNA = 16X
# max 6 samples
# empty 1.5 ml tubes in A5..B6 of rack to collect pools after PCR 
# the Kinnex primer mixes go in A1..D4 of 2 ml aluminium block

from opentrons import protocol_api

metadata = {
    'protocolName': 'PacBio Kinnex\u2122 PCR',
    'author': 'Angel Angelov <angel.angelov@kaust.edu.sa>',
    'description': 'Perform PacBio Kinnex\u2122 PCR for the PacBio 16S, full-length RNA or single-cell RNA kits',
    'apiLevel': '2.18'
}

def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")

# Runtime params
#================================================================
def add_parameters(parameters):
    parameters.add_str(
        variable_name="protocol",
        display_name="Kinnex\u2122 protocol type",
        description="Select which Kinnex PCR protocol to run",
        choices=[
            {"display_name": "16S amplicons", "value": "16S"},
            {"display_name": "Full-length RNA", "value": "fl_rna"},
            {"display_name": "Single-cell RNA", "value": "sc_rna"}
        ],
        default="16S",
    )
    parameters.add_str(
        variable_name="left_pip",
        display_name="Left mount pipette",
        description="Type of single channel pipette on left mount",
        choices=[
            {"display_name": "P20 single-channel GEN2", "value": "p20_single_gen2"},
            {"display_name": "P300 single-channel GEN2", "value": "p300_single_gen2"}
        ],
        default="p300_single_gen2",
    )
    parameters.add_int(
        variable_name='num_samples', 
        display_name="Number of samples",
        description="How many Kinnex PCR reactions to perform (max 6 are allowed)",
        default=1,
        minimum=1,
        maximum=6,
        unit="rxns"
    )
    parameters.add_int(
        variable_name='num_cycles',
        display_name='Number of Kinnex\u2122 PCR cycles',
        description='Number of Kinnex PCR cycles',
        default=9,
        minimum=9,
        maximum=12
    )
#================================================================

def run(ctx: protocol_api.ProtocolContext):
    # subset according to nsamples
    MMwells = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2'] # on rack
    poolwells = ['A5', 'B5', 'C5', 'D5', 'A6', 'B6'] # on rack
    # subset accordingto plex
    primerwells = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2', 'A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4'] # on block
    
    # Setup runtime and Shiny app varaibles
    nsamples = ctx.params.num_samples
    MMwells = MMwells[:nsamples]
    poolwells = poolwells[:nsamples]

    # Left pipette
    left_pipette = ctx.params.left_pip

    #plex and ext time are determined by protocol
    if ctx.params.protocol == 'fl_rna':
        plex = 8
    elif ctx.params.protocol == '16S':
        plex = 12
    elif ctx.params.protocol == 'sc_rna':
        plex = 16

    if ctx.params.protocol == '16S':
        extensiontime = 90
    else:
        extensiontime = 240
    
    # these can be set optionally 
    ncycles = ctx.params.num_cycles
    primervol = 2.5
    MMvol = 22.5

    # for building the wells to distribute to/consolidate from, based on MMwell index and plex
    # works for any plex number
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    pcrprofile = [
        {'temperature':98, 'hold_time_seconds':20},
        {'temperature':68, 'hold_time_seconds':30},
        {'temperature':72, 'hold_time_seconds':extensiontime}
    ]

    if nsamples > 6 | nsamples < 1:
        exit('Please use up to 6 samples')
    if len(MMwells) != len(poolwells):
        exit('Number of sample and pool wells do not match!')
    
    comment(
        ctx,
        "Preparing Kinnex\u2122 using" + " Kinnex " + str(ctx.params.protocol) + " kit"
    )
    comment(
        ctx, 'Total number of samples: ' + str(nsamples) + ' in wells ' + str(MMwells)
        )
    
    odtc = ctx.load_module(
        module_name='thermocyclerModuleV2'
    )
    primerblock = ctx.load_labware(
        'opentrons_24_aluminumblock_nest_0.5ml_screwcap', '5', 'Alu block'
    )
    int_primerplate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '4','Intermediate primer plate'
    )
    rack = ctx.load_labware(
        'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '9', 'MM tube rack'
    )
    pcrplate = odtc.load_labware(
        'biorad_96_wellplate_200ul_pcr'
    ) # IMPORTANT - use biorad plates!!!

    if left_pipette == 'p20_single_gen2':
        tips_left = [
            ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1', '2']
        ]
    else:
        tips_left = [
            ctx.load_labware('opentrons_96_filtertiprack_200ul', slot) for slot in ['1', '2']
        ]
    tips20_multi = [
        ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3']
    ]
    lp = ctx.load_instrument(
        left_pipette, mount='left', tip_racks=tips_left
    )
    m20 = ctx.load_instrument(
        'p20_multi_gen2', mount='right', tip_racks=tips20_multi
    )
    
    # define liquids
    mastermix_liquid = ctx.define_liquid(
        name = 'Kinnex\u2122 master mix',
        description = 'Kinnex PCR mix 103-107-700',
        display_color = '#6aa84f'
    )
    for loc in rack.wells()[:nsamples]:
        loc.load_liquid(mastermix_liquid, MMvol)
        
    primers_liquid = ctx.define_liquid(
        name = 'Kinnex\u2122 primer mix',
        description = 'Kinnex primer mix',
        display_color = '#ff8234'
    )

    for loc in primerblock.wells()[:plex]:
        loc.load_liquid(primers_liquid, primervol)

    # setup ODTC
    odtc.open_lid()
    odtc.set_block_temperature(temperature = 10)
    odtc.set_lid_temperature(100)

    # distribute MM
    for i, v in enumerate(MMwells):
        distribute_wells =  [ j + str(i*2 + 1) for j in rows ] + [ j + str(i*2 + 2) for j in rows ]
        comment(
            ctx, 
            'Distributing sample ' 
            + str(MMwells[i]) 
            + ' to PCR plate wells: ' 
            + str(distribute_wells[:plex])
        )
        lp.distribute(
            MMvol,
            rack.wells_by_name()[v],
            [pcrplate.wells_by_name()[well] for well in distribute_wells[:plex]], 
            air_gap = 0, 
            disposal_volume = 0 
            #blow_out = False, 
            #blowout_location = 'destination well' # blowout is required in distribute
        )

    # Transfer primers from block to intermediate plate
    comment(
        ctx, 
        "Transfer primers from block to intermediate plate"
    )
    
    # make sure accurate pipetting if P300 is used
    thisvolume = primervol * nsamples * 1.5
    if left_pipette == 'p300_single_gen2' and thisvolume < 10:
        thisvolume = 10
        ctx.pause(
            'Using p300 for pipetting less than 20 ul! Will distribute 10 ul primer mix to intermediate plate, but ' 
            + str(primervol * nsamples * 1.1) 
            + ' will be used'
        )
    # make sure enough primer is available in the intermediate plate even for 1 sample
    if thisvolume < 5:
        thisvolume = 5

    lp.transfer(
        thisvolume,
        [primerblock[well] for well in primerwells[:plex]],
        int_primerplate.wells()[:plex], 
        mix_before = (3, thisvolume/2), 
        new_tip = 'always'
    )

    # Add primers with multichannel
    for i in range(nsamples):
        samplecols = 'A' + str(i*2 + 1)
        comment(
            ctx, 
            'Add primers to PCR plate for sample ' 
            + MMwells[i]
        )
        m20.transfer(
            primervol,
            int_primerplate['A1'],
            pcrplate.wells_by_name()[samplecols],
            mix_before = (1, primervol),
            mix_after = (5, (MMvol + primervol)/2),
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
                mix_after = (5, (MMvol + primervol)/2),
                blow_out = True,
                blowout_location = 'destination well'
            )
    # PCR
    comment(ctx, 'Kinnex\u2122 PCR')
    ctx.pause("Cover plate with aluminum foil") 
    odtc.close_lid()
    odtc.set_block_temperature(temperature=98, hold_time_minutes=3)
    odtc.execute_profile(steps=pcrprofile, repetitions=ncycles, block_max_volume=20)
    odtc.set_block_temperature(temperature=72, hold_time_minutes=5)
    odtc.set_block_temperature(10)
    odtc.open_lid()
    odtc.deactivate_lid()
    odtc.deactivate_block()
    ctx.pause("Uncover plate before pooling")
    
    # # Consolidate PCRs
    for i, v in enumerate(poolwells):
        distribute_wells =  [ j + str(i*2 + 1) for j in rows ] + [ j + str(i*2 + 2) for j in rows ]
        comment(
            ctx, 
            "Consolidating PCR wells " 
            + str(distribute_wells[:plex]) 
            + ' into pool well ' 
            + v
        )
        lp.consolidate(
            MMvol+primervol, 
            [pcrplate[well] for well in distribute_wells[:plex]], 
            rack.wells_by_name()[v]
        )

    comment(ctx, 'Kinnex\u2122 PCR done!')
