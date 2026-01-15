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
tips = "opentrons_flex_96_filtertiprack_200ul"
single_col_load = True
################################

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_bool(
        variable_name="plate_on_magnet",
        display_name="Sample plate on magnet",
        description="Run with sample plate on magnet on A3",
        default=False
    )
    parameters.add_int(
        variable_name="samples",
        display_name="Number of samples",
        description="Number of DNA samples to shear",
        default=8,
        minimum=1,
        maximum=96,
        unit="samples"
    )
    parameters.add_int(
        variable_name="reps",
        display_name="Number of repetitions",
        description="Number of mixing cycles (each rep is 100 cycles)",
        default=8,
        minimum=6,
        maximum=15,
        unit="x100 cycle"
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

def run(ctx: protocol_api.ProtocolContext):
    samples_count = ctx.params.samples
    reps_count = ctx.params.reps
    offset = ctx.params.tip_offset
    cols = math.ceil(samples_count / 8)

    ctx.load_waste_chute()
    
    sampleplate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B1')

    mag_block = ctx.load_module('magneticBlockV1', 'D1')
    sampleplate_mag = mag_block.load_labware('nest_96_wellplate_2ml_deep')

    # 
    if ctx.params.plate_on_magnet:
        sample_wells = sampleplate_mag.rows()[0][:12]
    else:
        sample_wells = sampleplate.rows()[0][:12]

    if single_col_load:
        rack200 = ctx.load_labware(load_name=tips, location="B3")
    else:
        rack200 = ctx.load_labware(load_name=tips, location="B3", adapter='opentrons_flex_96_tiprack_adapter')
    
    
    pip = ctx.load_instrument("flex_96channel_1000", mount='left', tip_racks=[rack200])
    
    if single_col_load:
        pip.configure_nozzle_layout(
            style=COLUMN,
            start="A12",
            tip_racks=[rack200]
        )
    
    pip.flow_rate.aspirate = 1000
    pip.flow_rate.dispense = 1000
    pip.well_bottom_clearance.aspirate = offset
    pip.well_bottom_clearance.dispense = offset
    for x in range(cols):
        pip.pick_up_tip()
        for i in range(reps_count):
            pip.mix(100, 190, sample_wells[x])
        pip.drop_tip()