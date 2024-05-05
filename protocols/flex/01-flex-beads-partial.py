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

tipspositions = ['B3', 'C3', 'D3', 'A2']
###     Variables            ###
ncols =       1
# tip cols needed  = 1 + ncols*6
n_tipboxes = math.ceil((1 + ncols*6)/12)
samplevol =  50
beadspos =  'A1'
beadsvol =   50
ebpos =     'A2'
ebvol =      20
wastepos1 = 'A3'
wastepos2 = 'A4'
etohvol =   180
inctime =     5
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
    #rack50_1 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_50ul", location="D3")
    #rack50_2 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_50ul", location="C3")
    tips = [ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_200ul", location=pos) for pos in tipspositions[:n_tipboxes]]

    pip = ctx.load_instrument("flex_96channel_1000")
    flowrate_asp_orig = pip.flow_rate.aspirate
    flowrate_disp_orig = pip.flow_rate.dispense

    magnet = ctx.load_module("magneticBlockV1", 'C1')

    reservoir = ctx.load_labware("nest_12_reservoir_15ml", "D2")
    etoh = ctx.load_labware("axygen_1_reservoir_90ml", "C2")
    plate1 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "D1")
    plate2 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "B1")
    trash = ctx.load_trash_bin("A3")
    
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=tips
    )
    pip.flow_rate.aspirate = flowrate_asp_orig / speed_factor_aspirate
    pip.flow_rate.dispense = flowrate_disp_orig / speed_factor_dispence
    
    # Custom function to aspirate supernatant
    def supernatant_removal(vol, src, dest):
        pip.flow_rate.aspirate = 20
        asp_ctr = 0
        while vol > 180:
            pip.aspirate(
                180, src.bottom().move(types.Point(x=0, y=0, z=0.5)))
            pip.dispense(180, dest)
            pip.aspirate(10, dest)
            vol -= 180
            asp_ctr += 1
        pip.aspirate(
            vol, src.bottom().move(types.Point(x=0, y=0, z=0.5)))
        dvol = 10*asp_ctr + vol
        pip.dispense(dvol, dest)
        pip.flow_rate.aspirate = flowrate_asp_orig

    # Add beads to samples, use single column here to keep beads in A1 of reservoir
    rowA_start = plate1.rows()[0]
    rowA_end = plate2.rows()[0]

    comment(ctx, "Adding beads to columns " + str(rowA_start[:ncols]))
    
    pip.transfer(
        beadsvol,
        reservoir[beadspos],
        rowA_start[0:ncols], 
        mix_after = (10, (samplevol + beadsvol) * 0.8), 
        blow_out = True, blowout_location = "destination well",
        new_tip = 'always'
    )
    if not DRY_RUN:
        ctx.delay(minutes = inctime/2)
    
    # next_tipload_loc = rack50_1.rows()[0][ncols*2-1]
    #print(rack50.rows()[0][3])
    #pip.pick_up_tip(next_tipload_loc)
    for i in range(ncols):
        comment(ctx, "Mixing column " + str(rowA_start[i]))
        pip.pick_up_tip()
        pip.mix(repetitions=5, volume=(samplevol + beadsvol) * 0.8, location=rowA_start[i], rate=0.8)
        pip.drop_tip()
    
    if not DRY_RUN:
        ctx.delay(minutes=inctime/2)
    
    ########################################################################

    # Move to magnet
    ctx.move_labware(plate1, magnet, use_gripper=True)
    if not DRY_RUN:
        ctx.delay(minutes=2)
    
    # Aspirate the supernatant

    for i in range(ncols):
        comment(ctx, "Supernatant removal column " + str(rowA_start[i]))
        pip.pick_up_tip()
        supernatant_removal((samplevol + beadsvol)*1.1, rowA_start[i], reservoir[wastepos1])
        pip.drop_tip()

    # EtOH washes
    # add EtOH, no tip change   
    for k in range(2):
        comment(ctx, "EtOH addition " + str(k + 1))
        pip.pick_up_tip()
        for i in range(ncols):
            pip.aspirate(etohvol, etoh['A1'], rate = 0.8)
            pip.dispense(etohvol, rowA_start[i].top().move(types.Point(0, 0, -2)), rate = 0.2) #dispense from the top of the well
        pip.drop_tip()
        
        ctx.delay(seconds=30)
    # EtOH remove, tip with change    
        for i in range(ncols):
            comment(ctx, "EtOH remove  " + str(k + 1) + " for column " + str(rowA_start[i]))
            pip.pick_up_tip()
            supernatant_removal(etohvol*1.1, rowA_start[i], reservoir[wastepos2])
            pip.drop_tip()

    # Move plate back to resuspend beads
    ctx.move_labware(plate1, 'D1', use_gripper=True)
    comment(ctx, "Resuspend beads")
    for i in range(ncols):
        pip.transfer(
            ebvol, 
            reservoir[ebpos], 
            rowA_start[i],
            mix_after = (12, ebvol*0.8), 
            new_tip = 'always'
        )
    comment(ctx, 'Incubate ' + str(inctime) + ' minutes')
    if not DRY_RUN:
        ctx.delay(minutes = inctime)

    # Move plate to magnet and final elution
    ctx.move_labware(plate1, magnet, use_gripper=True)
    if not DRY_RUN:
        ctx.delay(minutes=2)
    for i in range(ncols):
        comment(ctx, 'Elution for ' + str(rowA_start[i]))
        pip.pick_up_tip()
        supernatant_removal(ebvol, rowA_start[i], rowA_end[i])
        pip.drop_tip()

    comment(ctx, 'END')
