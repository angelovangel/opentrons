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
n_tipboxes = math.ceil((2 + ncols*7)/12)
samplevol =  50
beadspos =  'A1'
beadsvol =   50
ebpos =     'A2'
ebvol =      40
wastepos1 = 'A3'
wastepos2 = 'A4'
etohvol =   150
inctime =     10
speed_factor_aspirate = 1
speed_factor_dispence = 1
DRY_RUN = False
################################

if ncols < 1 | ncols > 7:
    quit("ncols must be between 1 and 6")

def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")


def run(ctx: protocol_api.ProtocolContext):
    rack_partial = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location='A1')
    rack_full_1 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location='B3', adapter="opentrons_flex_96_tiprack_adapter")
    rack_full_2 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location='C3', adapter="opentrons_flex_96_tiprack_adapter")
    rack_full_3 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location='D3', adapter="opentrons_flex_96_tiprack_adapter")
    rack_full_4 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location='A2', adapter="opentrons_flex_96_tiprack_adapter")

    #rack50_2 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_50ul", location="C3")
    #tips = [ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location=pos) for pos in tipspositions[:n_tipboxes]]

    pip = ctx.load_instrument("flex_96channel_1000")
    original_flow_rate_aspirate = pip.flow_rate.aspirate
    
    magnet = ctx.load_module("magneticBlockV1", 'C1')

    reservoir = ctx.load_labware("nest_12_reservoir_15ml", "D2")
    etoh = ctx.load_labware("axygen_1_reservoir_90ml", "C2")
    plate1 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "D1")
    plate2 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "B1")
    #block = ctx.load_labware("nest_96_wellplate_2ml_deep", "")
    waste = ctx.load_labware("axygen_1_reservoir_90ml", "B2")
    trash = ctx.load_trash_bin("A3")
    
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack_partial]
    )

    pip.flow_rate.aspirate = original_flow_rate_aspirate / speed_factor_aspirate
    pip.flow_rate.dispense = pip.flow_rate.dispense / speed_factor_dispence
    
    # Custom function to aspirate supernatant
    def supernatant_removal(vol, src, dest):
        pip.flow_rate.aspirate = 20
        asp_ctr = 0
        while vol > 150:
            pip.aspirate(
                150, src.bottom().move(types.Point(x=0, y=0, z=1.0)))
            pip.dispense(
                150, dest.top().move(types.Point(x=0, y=0, z=2)), push_out=5)
            pip.aspirate(5, dest.top().move(types.Point(0,0,2))) # air gap
            vol -= 150
            asp_ctr += 1
        pip.aspirate(
            vol, src.bottom().move(types.Point(x=0, y=0, z=0.5)))
        dvol = 5*asp_ctr + vol
        pip.dispense(dvol, dest.top().move(types.Point(x=0, y=0, z=2)))
        pip.aspirate(5, dest.top().move(types.Point(0, 0, 2)))
        pip.flow_rate.aspirate = original_flow_rate_aspirate / speed_factor_aspirate

    # Add beads to samples, use single column here to keep beads in A1 of reservoir
    rowA_start = plate1.rows()[0]
    #rowA_end = plate2.rows()[0]

    comment(ctx, "Adding beads to columns " + str(rowA_start[:ncols]))
    
    # single column loading
    pip.transfer(
        beadsvol,
        reservoir[beadspos],
        rowA_start[0:ncols],
        mix_before = (10, beadsvol * 0.8), 
        mix_after = (15, (samplevol + beadsvol) * 0.8), 
        blow_out = True, blowout_location = "destination well",
        new_tip = 'always'
    )
    
    
    # Mixing beads during inc
    # full head loading ################################################################
    pip.configure_nozzle_layout(style = ALL, tip_racks= [rack_full_1])
    # full head loading ################################################################
    comment(ctx, "Mixing sample + beads during inc")
    for _ in range(2):
        if not DRY_RUN:
            ctx.delay(minutes = inctime/3)
        pip.pick_up_tip(rack_full_1['A1'])
        pip.mix(repetitions=10, volume=(samplevol + beadsvol) * 0.8, location=plate1['A1'], rate=0.8)
        pip.return_tip()
    
    ########################################################################

    # Move to magnet
    ctx.move_labware(plate1, magnet, use_gripper=True)
    if not DRY_RUN:
        ctx.delay(minutes=3)
    
    # Aspirate the supernatant
    # use same tips as for mixing before
    comment(ctx, 'Supernatant removal')
    pip.pick_up_tip(rack_full_1['A1'])
    supernatant_removal((samplevol + beadsvol) * 1.1, plate1['A1'], waste['A1'])
    pip.drop_tip()

    # EtOH washes - racks 2 and 3
    comment(ctx, "EtOH washes")
    for i in [rack_full_2, rack_full_3]:
        pip.pick_up_tip(i['A1'])
        pip.aspirate(etohvol, etoh['A1'], rate=0.8)
        pip.dispense(etohvol, plate1['A1'].top().move(types.Point(0,0,-1)), rate=0.2)
        pip.aspirate(10, plate1['A1'].top().move(types.Point(0,0,1))) # air gap
        if not DRY_RUN:
            ctx.delay(seconds=25)
        supernatant_removal(etohvol * 1.1, plate1['A1'], waste['A1'])
        pip.drop_tip()

    # Move plate back to resuspend beads 
    ctx.move_labware(plate1, 'D1', use_gripper=True)
    
    
    comment(ctx, "Resuspend beads")
    # use tips to mix once on the magnet after resusp
    pip.pick_up_tip(rack_full_4['A1'])
    #pip.aspirate(ebvol, block['A6'])
    # pip.transfer(
    #     ebvol, 
    #     reservoir[ebpos], 
    #     rowA_start[0:ncols], 
    #     mix_after = (15, ebvol * 0.8), 
    #     new_tip = 'always'
    # )

    comment(ctx, 'Incubate ' + str(inctime) + ' minutes')
    if not DRY_RUN:
        ctx.delay(minutes = inctime)

    # Move plate to magnet and final elution
    ctx.move_labware(plate1, magnet, use_gripper=True)
    if not DRY_RUN:
        ctx.delay(minutes=3)
    # for i in range(ncols):
    #     comment(ctx, 'Elution for ' + str(rowA_start[i]))
    #     pip.pick_up_tip()
    #     supernatant_removal(ebvol, rowA_start[i], rowA_end[i])
    #     pip.drop_tip()

    # comment(ctx, 'END')
