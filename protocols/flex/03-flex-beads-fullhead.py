from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL
from opentrons import types
import math

metadata = {
    "protocolName": "Beads cleanup Flex 96-channel, full head loading",
    "description": """Perform bead cleanup with variable number of columns (1 to 12)""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.18"
    }

### Parameters ###
def add_parameters(parameters):
    parameters.add_int(
        variable_name='ncolumns', 
        display_name="Number of columns",
        description="How many columns to process",
        default=2,
        minimum=1,
        maximum=12,
        unit="columns"
    )

    parameters.add_int(
        variable_name="sample_volume",
        display_name="Sample volume",
        description="Sample volume",
        default=50,
        minimum=20,
        maximum=90,
        unit="uL"
)
    parameters.add_int(
        variable_name="beads_volume",
        display_name="Beads volume",
        description="Beads volume",
        default=50,
        minimum=20,
        maximum=90,
        unit="uL"
)
    parameters.add_int(
        variable_name="eb_volume",
        display_name="EB volume",
        description="Elution buffer volume",
        default=40,
        minimum=15,
        maximum=90,
        unit="uL"
)
    parameters.add_int(
        variable_name="inc_time",
        display_name="Incubation time",
        description="Binding/elution incubation time (minutes)",
        default=10,
        minimum=3,
        maximum=20,
        unit="min"
)
    parameters.add_bool(
        variable_name="dry_run",
        display_name="Dry Run",
        description="Skip incubation delays.",
        default=False
)
### Parameters ###

###     Variables            ###
# use no spacing around '=' to discriminate the replacements made by the shiny app from the assignments of runtime params
ncols=7
samplevol=50
beadspos =  'A1'
beadsvol=50
ebpos =     'A2'
ebvol=40
etohvol =   150
etohpos =   ['A3', 'A4', 'A5'] # one pos for every 4 columns, can accomodate 200 ul EtOH per well
inctime=10
speed_factor_aspirate = 1
DRY_RUN=False
BEADSMIX = False
################################

# if ncols < 1 | ncols > 7:
#     quit("ncols must be between 1 and 6")

def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")


def run(ctx: protocol_api.ProtocolContext):
    # use params supplied at runtime
    ncols = ctx.params.ncolumns
    samplevol = ctx.params.sample_volume
    beadsvol = ctx.params.beads_volume
    ebvol = ctx.params.eb_volume
    inctime = ctx.params.inc_time
    DRY_RUN = ctx.params.dry_run
    # use params supplied at runtime
    
    rack_partial = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_1000ul", location='A2')
    fullpositions = ['B3', 'C3', 'B2', 'C2']
    rack_full_1, rack_full_2, rack_full_3, rack_full_4 = [
        ctx.load_labware(
            load_name="opentrons_flex_96_filtertiprack_200ul", 
            location=loc, adapter="opentrons_flex_96_tiprack_adapter"
            ) for loc in fullpositions
    ]
    
    pip = ctx.load_instrument("flex_96channel_1000")
    original_flow_rate_aspirate = pip.flow_rate.aspirate
    original_flow_rate_dispense = pip.flow_rate.dispense
    
    # ----------------------------------------------
    # modules
    magnet = ctx.load_module("magneticBlockV1", 'C1')
    # ----------------------------------------------
    # labware
    reservoir = ctx.load_labware("nest_12_reservoir_15ml", "D2")
    #etoh = ctx.load_labware("axygen_1_reservoir_90ml", "C2")
    plate1 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "D1")
    plate2 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "B1")
    trash = ctx.load_trash_bin("A3")

    #-----------------------------------------------
    # helper functions
    def pip_config(type):
        if type == 'partial':
            pip.configure_nozzle_layout(
            style=COLUMN,
            start="A12",
            tip_racks=[rack_partial]
            )
        elif type == 'full':
            pip.configure_nozzle_layout(style = ALL)

    def slow_tip_withdrawal(pipette, well):
        factor_slow = 40
        pipette.default_speed /= factor_slow
        pipette.move_to(well.top(-3))
        pipette.default_speed *= factor_slow

    # aspirate, dispence x times at well top (leave 0.1x dispvol in tip), air gap 
    def distribute_custom(aspvol, aspmixtimes, source, dispvol, dest = [], disprate = 1, airgap = True, mixbefore = False):
        ndisp = math.floor(aspvol / dispvol)
        aspvol = aspvol + dispvol * 0.3
        if dispvol + dispvol * 0.3 > aspvol:
            raise ValueError("Wrong volumes are used")
        if aspvol > pip.max_volume:
            raise ValueError("Asp vol exceeds max volume")
        if ndisp != len(dest):
            raise ValueError("Check dest list")
        if mixbefore:
            pip.mix(aspmixtimes, aspvol*0.8, source)
        pip.aspirate(aspvol, source)
        if airgap:
            pip.aspirate(10, source.top()) # air gap
        for i in dest:
            pip.dispense(dispvol, i.top().move(types.Point(0,0,0)), rate = disprate)
            pip.move_to(i.top().move(types.Point(-2,0,0))) # touch tip
            pip.move_to(i.top().move(types.Point(2,0,0))) # touch tip
        pip.aspirate(20, dest[-1].top().move(types.Point(0,0,1)))
    
    def remove(removal_vol, source, dest, type):
        # type - 'etoh' or 'eb'
        extra_vol = 20
        if removal_vol < 5 or removal_vol > source.max_volume:
            raise ValueError("A wrong volume is used")
        if removal_vol + extra_vol*2 > source.max_volume:
            extra_vol = (source.max_volume - removal_vol) / 2

        ctx.comment("--- Removing supernatant")
        ctx.comment("Extra vol = " + str(extra_vol))
        if type == 'eb':
            pip.aspirate(removal_vol * 0.9, source.bottom().move(types.Point(0, 0, 1)), rate = 0.1)
            disp_vol = removal_vol
        else:
            for i in (5, 2, 0.7): #stepwise removal
                pip.aspirate(removal_vol/3, source.bottom().move(types.Point(0, 0, i)), rate = 0.1)
            pip.aspirate(extra_vol, source.bottom().move(types.Point(0, 0, 0.5)), rate = 0.05)
            disp_vol = removal_vol + extra_vol
        slow_tip_withdrawal(pip, source)
        pip.dispense(None, dest, push_out=0)
        ctx.comment("------------------------")

    ########################################################################
    pip_config('partial')
    ########################################################################
    pip.flow_rate.aspirate = original_flow_rate_aspirate / speed_factor_aspirate
    
    # Add beads to samples, use single column here to keep beads in A1 of reservoir
    rowA_start = plate1.rows()[0]
    #rowA_end = plate2.rows()[0]

    comment(ctx, "Adding beads to columns " + str(rowA_start[:ncols]))
    pip.pick_up_tip()
    distribute_custom(beadsvol * ncols, 10, reservoir[beadspos], beadsvol, rowA_start[:ncols], disprate= 0.2, airgap = False, mixbefore = True)
    pip.drop_tip()
    
    # Mixing beads during inc
    # full head loading ################################################################
    pip_config('full')
    # full head loading ################################################################

    comment(ctx, "Mixing sample + beads")
    pip.pick_up_tip(rack_full_1['A1'])
    pip.mix(repetitions=10, volume=(samplevol + beadsvol) * 0.8, location=plate1['A1'], rate=0.8)
    pip.return_tip()
    if not DRY_RUN:
        ctx.delay(minutes = inctime)

    ########################################################################

    # Move to magnet
    ctx.move_labware(plate1, magnet, use_gripper=True)
    if BEADSMIX:
        pip.pick_up_tip(rack_full_1['A1'])
        pip.mix(2, (samplevol + beadsvol) * 0.8, plate1['A1'], rate=0.8)
        pip.return_tip()
    if not DRY_RUN:
        ctx.delay(minutes=2)
    
    
    # Aspirate the supernatant
    # use same tips as for mixing before
    comment(ctx, 'Supernatant removal')
    pip.pick_up_tip(rack_full_1['A1'])
    remove(samplevol + beadsvol, plate1['A1'], trash, type = 'etoh')
    pip.drop_tip()

    # EtOH washes - distribute from reservoir, use rack2 for etoh removal
    comment(ctx, "EtOH washes")
    # determine which reservoir pos to aspirate from
    for i in range(2):
        i += 1
        ########################################################################
        pip_config('partial')
        ########################################################################
        # split ETOH distribution in batches of 4 columns
        batches = math.ceil(ncols / 4)
        pip.pick_up_tip()
        for j in range(batches):
            batch = j + 1
            if ncols >= batch * 4: 
                colsinbatch = 4 
            else: 
                colsinbatch =  4 - (batch * 4 - ncols)  #  how many columns in this batch? 
            batchstart = batch * 4 - 4
            batchend = batchstart + colsinbatch
            #print(batch, colsinbatch, batchstart, batchend)
            comment(ctx, "EtOH wash " + str(i) + " : distribute batch " + str(batch) + " with " + str(colsinbatch) + " columns")
            distribute_custom(
                etohvol * colsinbatch, 
                0, 
                reservoir[etohpos[j]], 
                etohvol,
                rowA_start[batchstart:batchend], 
                disprate=0.2,
                airgap = True,
                mixbefore = False
            )
            
            #distribute_custom(etohvol * 6, 0, reservoir[etohpos[0]], etohvol,rowA_start[0:6], disprate=0.2)
            #distribute_custom(etohvol * (ncols - 6), 0, reservoir[etohpos[1]], etohvol,rowA_start[6:ncols], disprate=0.2)
        
        pip.drop_tip()
        pip.flow_rate.dispense = original_flow_rate_dispense

        pip_config('full')
        pip.pick_up_tip(rack_full_2['A1'])
        remove(etohvol, plate1['A1'], trash, type = 'etoh')
        if i < 2:
            pip.return_tip()
        else:
            pip.drop_tip()


    # Move plate back to resuspend beads - column loading
    ctx.move_labware(plate1, 'D1', use_gripper=True)

    ########################################################################
    pip_config('partial')
    ########################################################################
    
    comment(ctx, "Resuspend beads")
    pip.pick_up_tip()
    distribute_custom(
        ebvol * ncols, 0, reservoir[ebpos], ebvol, rowA_start[0:ncols], airgap = False, mixbefore = False
    )
    pip.drop_tip()
    # pip.distribute(
    #     ebvol, 
    #     reservoir[ebpos], 
    #     [i.top().move(types.Point(0,0,1)) for i in rowA_start[0:ncols]], # dispense from above
    #     new_tip = 'always', 
    #     disposal_volume = ebvol * 0.5
    # )

    # full head loading ################################################################
    pip_config('full')
    # full head loading ################################################################

    comment(ctx, 'Incubate ' + str(inctime) + ' minutes')
    
    
    pip.pick_up_tip(rack_full_3['A1'])
    for _ in range(15):
        pip.aspirate(ebvol * 0.8, plate1['A1'].bottom().move(types.Point(0,0,1)), rate=1)
        pip.dispense(ebvol * 0.8, plate1['A1'].bottom().move(types.Point(0,0,5)), rate = 0.8)
    # pip.mix(
    #     repetitions=15, 
    #     volume= ebvol * 0.8, 
    #     location=plate1['A1'].bottom().move(type.Point(0, 0, 3)), 
    #     rate=0.8
    # )
    if BEADSMIX:
        pip.return_tip()
    else:
        pip.drop_tip()
    if not DRY_RUN:
        ctx.delay(minutes = inctime)

    # Move plate to magnet and final elution
    # use tips to mix once on the magnet after resusp
    ctx.move_labware(plate1, magnet, use_gripper=True)
    
    if BEADSMIX:
        pip.pick_up_tip(rack_full_3['A1'])
        pip.mix(2, ebvol * 0.8, plate1['A1'])
        pip.drop_tip()

    if not DRY_RUN:
        ctx.delay(minutes=2)
    
    comment(ctx, 'Final elution')
    pip.pick_up_tip(rack_full_4['A1'])
    remove(ebvol, plate1['A1'], plate2['A1'], type = 'eb')
    pip.drop_tip()
    
    comment(ctx, 'END')
