from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL

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
samplevol =  50
beadspos =  'A1'
beadsvol =   50
ebpos =     'A2'
ebvol =      20
etohvol =   200
inctime =     5
speed_factor_aspirate = 2
speed_factor_dispence = 2
################################

if ncols < 1 | ncols > 7:
    quit("ncols must be between 1 and 6")

def run(ctx: protocol_api.ProtocolContext):
    rack50_1 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_50ul", location="D3")
    rack50_2 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_50ul", location="C3")
    rack1000 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_1000ul", location="B3")

    pip = ctx.load_instrument("flex_96channel_1000")
    pip.flow_rate.aspirate = pip.flow_rate.aspirate / speed_factor_aspirate
    pip.flow_rate.dispense = pip.flow_rate.dispense / speed_factor_dispence

    magnet = ctx.load_module("magneticBlockV1", 'C1')

    reservoir = ctx.load_labware("nest_12_reservoir_15ml", "D2")
    etoh = ctx.load_labware("axygen_1_reservoir_90ml", "C2")
    plate1 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "D1")
    plate2 = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "B1")
    trash = ctx.load_trash_bin("A3")
    
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack50_1]
    )
    # Add beads to samples, use single column here to keep beads in A1 of reservoir
    rowA = plate1.rows()[0]

    pip.transfer(
        beadsvol,
        reservoir['A1'],
        rowA[0:ncols], 
        mix_after = (10, samplevol/2), 
        blow_out = True, blowout_location = "destination well",
        trash=True, 
        new_tip = 'always'
    )
    
    ctx.delay(inctime/2)
    
    next_tipload_loc = rack50_1.rows()[0][ncols*2-1]
    #print(rack50.rows()[0][3])

    pip.pick_up_tip(next_tipload_loc)
    pip.mix(repetitions=5, volume=samplevol/2, location=rowA[0], rate=0.5)
    pip.drop_tip()

    ctx.delay(inctime/2)
    
    ########################################################################

    # Move to magnet
    ctx.move_labware(plate1, magnet, use_gripper=True)

    # Aspirate the supernatant
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack1000]
    )
    # EtOH wash 1
    pip.pick_up_tip(rack1000.rows()[0][ncols-1])
    pip.aspirate(etohvol, etoh['A1'])
    pip.dispense(etohvol, rowA[ncols-1])
    ctx.delay(seconds=30)
    pip.aspirate(etohvol + 5, rowA[ncols-1], rate=0.8)
    pip.dispense(etohvol + 5, trash, push_out=5)
    pip.drop_tip()

    # EtOH wash 2
    pip.pick_up_tip(rack1000.rows()[0][ncols*2-1])
    pip.aspirate(etohvol, etoh['A1'])
    pip.dispense(etohvol, rowA[ncols-1])
    ctx.delay(seconds=30)
    pip.aspirate(etohvol + 10, rowA[ncols-1], rate=0.8)
    pip.dispense(etohvol + 10, trash, push_out=5)
    pip.drop_tip()

    #Dry beads
    ctx.delay(seconds=30)

    # Resuspend beads
    ctx.move_labware(plate1, 'D1', use_gripper=True)
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack50_2]
    )
    
    pip.transfer(
        ebvol,
        reservoir['A2'],
        rowA[0:ncols], 
        mix_after = (15, ebvol/2),
        trash=True, 
        new_tip = 'always'
    )

    ctx.delay(minutes=inctime)
    ctx.move_labware(plate1, magnet, use_gripper=True)

    # final aspirate supernatant
    next_tipload_loc = rack50_2.rows()[0][ncols*2-1]
    pip.pick_up_tip(next_tipload_loc)
    pip.aspirate(ebvol+5, plate1['A1'], rate=0.5)
    pip.dispense(ebvol, plate2['A1'], push_out=10)



    

    