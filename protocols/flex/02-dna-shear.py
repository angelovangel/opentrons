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
speed_aspirate = 500
speed_dispence = 500
################################


def run(ctx: protocol_api.ProtocolContext):
    ctx.load_trash_bin("A3")
    rack1000 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_1000ul", location="B3")
    plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B1')
    pip = ctx.load_instrument("flex_96channel_1000")

    pip.flow_rate.aspirate = speed_aspirate
    pip.flow_rate.dispense = speed_dispence

    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack1000]
    )
    mydict = {75: ['A1', 'A5', 'A9'], 150: ['A2', 'A6', 'A10'], 300: ['A3', 'A7', 'A11'], 450: ['A4', 'A8', 'A12']}
    for i, (k, v) in enumerate( mydict.items() ):
        #print(k, v)
        for well in v:
            pip.pick_up_tip()
            pip.mix(repetitions=k, volume=290, location=plate.wells_by_name()[well])
            pip.drop_tip()