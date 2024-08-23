from opentrons import protocol_api
from opentrons import types
from opentrons.protocol_api import COLUMN, ALL
import math

metadata = {
    "protocolName": "Add X-terminator beads to plate",
    "description": """Add X-terminator beads to stack of ABI plate in Biorad""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.18"
    }

### Parameters ###
def add_parameters(parameters):
    # parameters.add_int(
    #     variable_name='ncolumns', 
    #     display_name="Number of columns",
    #     description="How many columns to process",
    #     default=12,
    #     minimum=1,
    #     maximum=12,
    #     unit="columns"
    # )
    parameters.add_int(
        variable_name="beads_volume",
        display_name="Beads volume",
        description="Beads volume",
        default=110,
        minimum=10,
        maximum=160,
        unit="uL"
)
    parameters.add_int(
        variable_name="water_volume",
        display_name="Water volume",
        description="Water volume",
        default=130,
        minimum=10,
        maximum=160,
        unit="uL"
)
    parameters.add_str(
        variable_name="beads_reservoir",
        display_name="Reservoir for beads",
        description="Select the type reservoir for x-term beads",
        choices=[
            {"display_name": "Axygen 1 Well Reservoir 90 mL", "value": "axygen_1_reservoir_90ml"},
            #{"display_name": "NEST 4 Well Reservoir 40 ml", "value": "nest_4_reservoir_40ml"},
            #{"display_name": "NEST 12 Well Reservoir 15 mL", "value": "nest_12_reservoir_15ml"},  
        ],
        default="axygen_1_reservoir_90ml",
    )
    
def run(ctx: protocol_api.ProtocolContext):
    #ncols = ctx.params.ncolumns
    beadsvol = ctx.params.beads_volume
    watervol = ctx.params.water_volume

    # tips and pipette
    full_positions = ['B3', 'C3']
    rack_full_1, rack_full_2 = [
        ctx.load_labware(
            load_name="opentrons_flex_96_filtertiprack_1000ul", 
            location=loc, adapter="opentrons_flex_96_tiprack_adapter"
            ) for loc in full_positions
    ]
    rack_partial = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_1000ul", location='A2')
    pip = ctx.load_instrument("flex_96channel_1000")
    
    #labware
    res = ctx.load_labware(ctx.params.beads_reservoir, "C1")
    plate = ctx.load_labware("stack_plate_biorad96well", "C2")
    trash = ctx.load_waste_chute()
    beadspos = 'A1'
    waterpos = 'A2'

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

    # aspirate, dispence x times at well top (leave 0.1x dispvol in tip), air gap 
    

    ########################################################################
    pip_config('full')
    ########################################################################

    
