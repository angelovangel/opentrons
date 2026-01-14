import math
from opentrons import protocol_api
from opentrons import types
from opentrons.protocol_api import COLUMN, ALL

metadata = {
    "protocolName": "DNA shear 96 head",
    "description": """This protocol is for performing DNA shearing on Flex with 96 channel pipette""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.18"
    }
    
###     Variables            ###
samples = 2
tips = "opentrons_flex_96_filtertiprack_200ul"
reps = 8
single_col_load = True
################################

cols = math.ceil(samples/8)

def run(ctx: protocol_api.ProtocolContext):
    ctx.load_waste_chute()

    if single_col_load:
        rack200 = ctx.load_labware(load_name=tips, location="B3")
    else:
        rack200 = ctx.load_labware(load_name=tips, location="B3", adapter='opentrons_flex_96_tiprack_adapter')
        
    samples = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B1')
    pip = ctx.load_instrument("flex_96channel_1000", mount='left', tip_racks=[rack200])
    
    if single_col_load:
        pip.configure_nozzle_layout(
            style=COLUMN,
            start="A12",
            tip_racks=[rack200]
        )
    
    

    pip.flow_rate.aspirate=1000
    pip.flow_rate.dispense=1000
    for x in range(cols):
        pip.pick_up_tip()
        for i in range(reps):
            pip.mix(100, 190, samples[x])
        pip.drop_tip()