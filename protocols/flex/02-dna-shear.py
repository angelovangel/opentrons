from opentrons import protocol_api
from opentrons import types
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
ncols = 2
tips = "opentrons_flex_96_filtertiprack_1000ul"
mixvol = 290
reps = 3
speed_aspirate = 700
speed_dispence = 700
################################

cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

def run(ctx: protocol_api.ProtocolContext):
    ctx.load_trash_bin("A3")
    rack1000 = ctx.load_labware(load_name=tips, location="B3")
    sampleplate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B1')
    pip = ctx.load_instrument("flex_96channel_1000")

    pip.flow_rate.aspirate = speed_aspirate
    pip.flow_rate.dispense = speed_dispence
    
    pip.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=[rack1000]
    )
    

    def mymix(vol, position, repeats, return_tip = False):
        pip.pick_up_tip()
        for _ in range(repeats):
            loc1 = sampleplate[position].bottom(z = 1)
            loc2 = loc1.move(types.Point(x=-2, y=0, z=5))
            pip.aspirate(vol, loc1)
            pip.dispense(vol, loc2)
        if return_tip:
            pip.return_tip()
        else:
            pip.drop_tip()

    # currently only one column loading is supported by the API, but this will change
    # for i in cols[:ncols]:
    #     mymix(reps)

    mydict = {1: ['A1', 'A5', 'A9'], 2: ['A2', 'A6', 'A10'], 3: ['A3', 'A7', 'A11'], 4: ['A4', 'A8', 'A12']}
    for _, (k, v) in enumerate( mydict.items() ):
        #print(k, v)
        for well in v:
            mymix(mixvol, well, k, return_tip=False)
