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
    "apiLevel": "2.16"
    }
    
###     Variables            ###
ncols = 2
tips = "opentrons_flex_96_filtertiprack_1000ul"
mixvol = 290
reps = 3
speed_aspirate = 716
speed_dispence = 716
single_col_load = False
################################

cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

def run(ctx: protocol_api.ProtocolContext):
    ctx.load_trash_bin("A3")
    if single_col_load:
        rack1000 = ctx.load_labware(load_name=tips, location="B3")
    else:
        rack1000 = ctx.load_labware(load_name=tips, location="B3", adapter='opentrons_flex_96_tiprack_adapter')
        
    sampleplate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B1')
    pip = ctx.load_instrument("flex_96channel_1000", mount='left', tip_racks=[rack1000])
    
    if single_col_load:
        pip.configure_nozzle_layout(
            style=COLUMN,
            start="A12",
            tip_racks=[rack1000]
        )
    pip.flow_rate.aspirate = speed_aspirate
    pip.flow_rate.dispense = speed_dispence
    


    # currently only one column loading is supported by the API, but this will change
    # for i in cols[:ncols]:
    #     mymix(reps)
    pip.pick_up_tip()
    pip.mix(reps, mixvol, sampleplate['A1'])
    pip.drop_tip()

    mydict = {1: ['A1', 'A5', 'A9'], 2: ['A2', 'A6', 'A10'], 3: ['A3', 'A7', 'A11'], 4: ['A4', 'A8', 'A12']}
    if single_col_load:
        for _, (k, v) in enumerate( mydict.items() ):
            print(k, v)
            for well in v:
                pip.pick_up_tip()
                pip.mix(repetitions=k, volume=mixvol, location=sampleplate[well])
                pip.drop_tip()
                #mymix(mixvol, well, k, return_tip=False)
