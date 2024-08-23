from opentrons import protocol_api
from opentrons import types
from opentrons.protocol_api import COLUMN, ALL
import math

metadata = {
    "protocolName": "Qbit assay in strips",
    "description": """Qbit assay in strips, transfer DNA in plate""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.18"
    }
def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")

### Parameters ###
def add_parameters(parameters):
    parameters.add_int(
        variable_name="sample_vol",
        display_name="sample volume for Qbit",
        description="Amount of 10x diluted sample volume",
        default=2,
        minimum=1,
        maximum=10,
        unit="uL"
    )
    parameters.add_int(
        variable_name='ncolumns', 
        display_name="Number of columns",
        description="How many columns to process",
        default=6,
        minimum=1,
        maximum=12,
        unit="columns"
    )
    parameters.add_str(
        variable_name="beads_reservoir",
        display_name="Reservoir for beads",
        description="Select the type reservoir for x-term beads",
        choices=[
            {"display_name": "Axygen 1 Well Reservoir 90 mL", "value": "axygen_1_reservoir_90ml"},
            {"display_name": "NEST 4 Well Reservoir 40 ml", "value": "nest_4_reservoir_40ml"},
            {"display_name": "NEST 12 Well Reservoir 15 mL", "value": "nest_12_reservoir_15ml"},  
        ],
        default="nest_12_reservoir_15ml",
    )
    
def run(ctx: protocol_api.ProtocolContext):
    
    samplevol = ctx.params.sample_vol
    ncols = ctx.params.ncolumns

    # tips and pipette
    full_positions = ['B3', 'C3']
    rack_full_1, rack_full_2 = [
        ctx.load_labware(
            load_name="opentrons_flex_96_filtertiprack_50ul", 
            location=loc, adapter="opentrons_flex_96_tiprack_adapter"
            ) for loc in full_positions
    ]
    rack_partial = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_1000ul", location='A2')
    pip = ctx.load_instrument("flex_96channel_1000")
    
    #labware
    start_stack = ctx.load_labware("stack_plate_biorad96well", "D1")
    dil_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "C1")
    qbit_stack = ctx.load_labware("stack_plate_biorad96well", "B1")

    res = ctx.load_labware(ctx.params.beads_reservoir, "D2")
    waterlid = ctx.load_labware("axygen_1_reservoir_90ml", "C2")
    trash = ctx.load_waste_chute()
    qbit_pos = 'A1'

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

    # distribute qbit rgnt
    ########################################################################
    pip_config('partial')
    ########################################################################
    rowA_start = start_stack.rows()[0]
    comment(ctx, "Adding qbit reagent to columns " + str(rowA_start[:ncols]))
    pip.distribute(198, res[qbit_pos], qbit_stack.columns()[:ncols])

    ########################################################################
    pip_config('full')
    ########################################################################

    
