import math
from opentrons import protocol_api
from opentrons import types
from opentrons.protocol_api import COLUMN, ALL

metadata = {
    "protocolName": "DNA shear 8-channel head",
    "description": """This protocol is for performing DNA shearing on Flex with 8-channel pipette""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.18"
    }
    
###     Variables            ###
tips = "opentrons_flex_96_filtertiprack_200ul"
# single_col_load = True
################################

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="ncols",
        display_name="Number of columns",
        description="Number of columns to shear",
        default=1,
        minimum=1,
        maximum=12,
        unit="columns"
    )
    parameters.add_int(
        variable_name="start_col",
        display_name="Start column",
        description="Column to start from",
        default=1,
        minimum=1,
        maximum=12,
    )
    parameters.add_int(
        variable_name="reps",
        display_name="Number of repetitions",
        description="Number of mixing cycles (each rep is 5 cycles)",
        default=2,
        minimum=1,
        maximum=1000,
        unit="reps"
    )
    parameters.add_int(
        variable_name="cycles_per_rep",
        display_name="Cycles per repetition",
        description="Number of cycles per repetition",
        default=5,
        minimum=1,
        maximum=100,
        unit="cycles"
    )
    parameters.add_int(
        variable_name="volume",
        display_name="Volume",
        description="Volume of DNA to shear",
        default=190,
        minimum=30,
        maximum=190,
        unit="ul"
    )
    parameters.add_float(
        variable_name="tip_offset",
        display_name="Tip offset from bottom",
        description="Tip offset from the bottom of the well in mm",
        default=2.0,
        minimum=0.5,
        maximum=10.0,
        unit="mm"
    )
    parameters.add_str(
        variable_name="plate_type",
        display_name="Sample plate type",
        description="Choose the sample plate type",
        choices=[
            {"display_name": "Bio-Rad 96 Well PCR 200µL", "value": "biorad_96_wellplate_200ul_pcr"},
            {"display_name": "NEST 96 Deep Well 2mL", "value": "nest_96_wellplate_2ml_deep"}
        ],
        default="nest_96_wellplate_2ml_deep"
    )

def run(ctx: protocol_api.ProtocolContext):
    if ctx.params.start_col + ctx.params.ncols - 1 > 12:
        raise ValueError("Start column and number of columns exceed 12")

    reps_count = ctx.params.reps
    offset = ctx.params.tip_offset
    plate_type = ctx.params.plate_type

    ctx.load_waste_chute()
    
    sampleplate = ctx.load_labware(plate_type, 'B1')    
    sample_wells = sampleplate.rows()[0][:12]

    rack200 = ctx.load_labware(load_name=tips, location="B3")
    pip = ctx.load_instrument("flex_8channel_1000", mount='right', tip_racks=[rack200])
    
    pip.flow_rate.aspirate = 1000
    pip.flow_rate.dispense = 1000
    pip.well_bottom_clearance.aspirate = offset
    pip.well_bottom_clearance.dispense = offset
    
    for x in range(ctx.params.start_col - 1, ctx.params.start_col - 1 + ctx.params.ncols):
        pip.pick_up_tip()
        for i in range(reps_count):
            pip.mix(ctx.params.cycles_per_rep, ctx.params.volume, sample_wells[x])
        pip.drop_tip()