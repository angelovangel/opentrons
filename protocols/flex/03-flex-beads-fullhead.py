from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL
from opentrons import types
import math

metadata = {
    "protocolName": "Beads cleanup Flex 96-channel, partial loading",
    "description": """This protocol is for performing bead cleanup with variable number of columns (1 to 6)""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.16"
    }

###     Variables            ###
ncols =       2
# tip cols needed  = 2 + ncols*7
#n_tipboxes = math.ceil((2 + ncols*7)/12)
samplevol =  50
beadspos =  'A1'
beadsvol =   50
ebpos =     'A2'
ebvol =      40
etohvol =   150
inctime =     10
speed_factor_aspirate = 1
#speed_factor_dispence = 1
DRY_RUN = False
BEADSMIX = False
################################

if ncols < 1 | ncols > 7:
    quit("ncols must be between 1 and 6")

def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")


def run(ctx: protocol_api.ProtocolContext):
    rack_partial = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location='A1')
    fullpositions = ['B3', 'C3', 'D3', 'A2', 'B2']
    rack_full_1, rack_full_2, rack_full_3, rack_full_4, rack_full_5 = [
        ctx.load_labware(
            load_name="opentrons_flex_96_filtertiprack_200ul", 
            location=loc, adapter="opentrons_flex_96_tiprack_adapter"
            ) for loc in fullpositions
    ]
    
    pip = ctx.load_instrument("flex_96channel_1000")
    original_flow_rate_aspirate = pip.flow_rate.aspirate
    
    # ----------------------------------------------
    # modules
    magnet = ctx.load_module("magneticBlockV1", 'C1')
    # ----------------------------------------------
    # labware
    reservoir = ctx.load_labware("nest_12_reservoir_15ml", "D2")
    etoh = ctx.load_labware("axygen_1_reservoir_90ml", "C2")
    plate1 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "D1")
    plate2 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "B1")
    trash = ctx.load_trash_bin("A3")

    #-----------------------------------------------
    # helper functions
    def slow_tip_withdrawal(pipette, well):
        factor_slow = 40
        pipette.default_speed /= factor_slow
        pipette.move_to(well.top(-3))
        pipette.default_speed *= factor_slow
    
    def remove(removal_vol, source, dest, type):
        # type - 'full' or 'partial'
        extra_vol = 20
        if removal_vol < 5 or removal_vol > source.max_volume:
            raise ValueError("A wrong volume is used")
        if removal_vol + extra_vol*2 > source.max_volume:
            extra_vol = (source.max_volume - removal_vol) / 2

        ctx.comment("--- Removing supernatant")
        ctx.comment("Extra vol = " + str(extra_vol))
        if type == 'partial':
            pip.aspirate(removal_vol * 0.9, source, rate = 0.1)
            disp_vol = removal_vol
        else:
            pip.aspirate(removal_vol, source.bottom().move(types.Point(0, 0, 0.7)), rate = 0.1)
            pip.aspirate(extra_vol, source.bottom().move(types.Point(0, 0, 0.5)), rate = 0.05)
            disp_vol = removal_vol + extra_vol
        slow_tip_withdrawal(pip, source)
        pip.dispense(disp_vol, dest, push_out=0)
        ctx.comment("------------------------")
    # def distribute_high(vol, source, times, dest):
    #     if vol * times <= pip.max_volume:
    #         asp = vol * times
    #     else:
    #         asp = pip.max_volume
        


    ########################################################################
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack_partial]
    )
    ########################################################################

    pip.flow_rate.aspirate = original_flow_rate_aspirate / speed_factor_aspirate
    

    # Add beads to samples, use single column here to keep beads in A1 of reservoir
    rowA_start = plate1.rows()[0]
    #rowA_end = plate2.rows()[0]

    comment(ctx, "Adding beads to columns " + str(rowA_start[:ncols]))
    
    # single column loading
    pip.distribute(
        beadsvol,
        reservoir[beadspos],
        [i.top().move(types.Point(0,0,1)) for i in rowA_start[0:ncols]], # dispense from above
        mix_before = (10, beadsvol * 0.8), 
        disposal_volume = beadsvol*0.5
        #mix_after = (10, (samplevol + beadsvol) * 0.8), 
        #blow_out = True, blowout_location = "destination well",
        #new_tip = 'always'
    )
    
    
    # Mixing beads during inc
    # full head loading ################################################################
    pip.configure_nozzle_layout(style = ALL)
    # full head loading ################################################################

    if BEADSMIX:
        comment(ctx, "Mixing sample + beads during inc")
        for _ in range(2):
            pip.pick_up_tip(rack_full_1['A1'])
            pip.mix(repetitions=10, volume=(samplevol + beadsvol) * 0.8, location=plate1['A1'], rate=0.8)
            pip.return_tip()
            if not DRY_RUN:
                ctx.delay(minutes = inctime/2)
    else:
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
    remove(samplevol + beadsvol, plate1['A1'], trash, type = 'full')
    pip.drop_tip()

    # EtOH washes - racks 2 and 3
    comment(ctx, "EtOH washes")
    for i in [rack_full_2, rack_full_3]:
        pip.pick_up_tip(i['A1'])
        pip.aspirate(etohvol, etoh['A1'], rate=0.7)
        pip.aspirate(10, etoh['A1'].top().move(types.Point(0,0,1)))
        pip.dispense(etohvol + 10, plate1['A1'].top().move(types.Point(0,0,-1)), rate=0.2)
        pip.aspirate(10, plate1['A1'].top().move(types.Point(0,0,1))) # air gap
        if not DRY_RUN:
            ctx.delay(seconds=25)
        remove(etohvol, plate1['A1'], trash, type = 'full')
        pip.drop_tip()

    # Move plate back to resuspend beads - column loading
    ctx.move_labware(plate1, 'D1', use_gripper=True)

    ########################################################################
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack_partial]
    )
    ########################################################################
    
    comment(ctx, "Resuspend beads")
    
    pip.distribute(
        ebvol, 
        reservoir[ebpos], 
        [i.top().move(types.Point(0,0,1)) for i in rowA_start[0:ncols]], # dispense from above
        #mix_after = (15, ebvol * 0.8), 
        new_tip = 'always', 
        disposal_volume = ebvol * 0.5
    )

    # full head loading ################################################################
    pip.configure_nozzle_layout(style = ALL)
    # full head loading ################################################################

    comment(ctx, 'Incubate ' + str(inctime) + ' minutes')
    if BEADSMIX:
        for _ in range(2):
            if not DRY_RUN:
                ctx.delay(minutes = inctime/2)
            pip.pick_up_tip(rack_full_4['A1'])
            pip.mix(repetitions=10, volume= ebvol * 0.8, location=plate1['A1'], rate=0.8)
            pip.return_tip()
    else:
        pip.pick_up_tip(rack_full_4['A1'])
        pip.mix(repetitions=10, volume= ebvol * 0.8, location=plate1['A1'], rate=0.8)
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
        pip.pick_up_tip(rack_full_4['A1'])
        pip.mix(2, ebvol * 0.8, plate1['A1'])
        pip.drop_tip()

    if not DRY_RUN:
        ctx.delay(minutes=2)
    
    comment(ctx, 'Final elution')
    pip.pick_up_tip(rack_full_5['A1'])
    remove(ebvol, plate1['A1'], plate2['A1'], type = 'partial')
    pip.drop_tip()
    
    comment(ctx, 'END')
