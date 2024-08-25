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
        display_name="Diluted sample volume for Qbit",
        description="Amount of 10x diluted sample volume",
        default=2,
        minimum=1,
        maximum=10,
        unit="uL"
    )
    parameters.add_int(
        variable_name='ncolumns1', 
        display_name="Number of columns in stack 1",
        description="How many columns in stack 1",
        default=6,
        minimum=1,
        maximum=6,
        unit="columns"
    )
    parameters.add_int(
        variable_name='ncolumns2', 
        display_name="Number of columns in stack 2",
        description="How many columns in stack 2",
        default=6,
        minimum=0,
        maximum=6,
        unit="columns"
    )
    parameters.add_bool(
        variable_name = 'prep_plate',
        display_name = 'Prepare run plate',
        description = 'Pipet strips (1, 3, 5 ...) to final plate (1, 2, 3 ...)',
        default = True
    )
    parameters.add_bool(
        variable_name = 'prep_qbit',
        display_name = 'Perform qbit',
        description = 'Dilute 10x and add 2 ul to qbit reagent',
        default = True
    )
    parameters.add_str(
        variable_name="qbit_reservoir",
        display_name="Reservoir for beads",
        description="Select the type reservoir for qbit reagent",
        choices=[
            {"display_name": "Axygen 1 Well Reservoir 90 mL", "value": "axygen_1_reservoir_90ml"},
            {"display_name": "NEST 4 Well Reservoir 40 ml", "value": "nest_4_reservoir_40ml"},
            {"display_name": "NEST 12 Well Reservoir 15 mL", "value": "nest_12_reservoir_15ml"},  
        ],
        default="nest_12_reservoir_15ml",
    )
    
def run(ctx: protocol_api.ProtocolContext):
    
    samplevol = ctx.params.sample_vol
    ncols1 = ctx.params.ncolumns1
    ncols2 = ctx.params.ncolumns2

    # tips and pipette
    full_positions = ['B3', 'C3']
    rack_full_1, rack_full_2 = [
        ctx.load_labware(
            load_name="opentrons_flex_96_filtertiprack_50ul", 
            location=loc, adapter="opentrons_flex_96_tiprack_adapter"
            ) for loc in full_positions
    ]
    partial1000 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_1000ul", location='C4')
    partial50 = ctx.load_labware(load_name="opentrons_flex_96_filtertiprack_50ul", location='B4')
    pip = ctx.load_instrument("flex_96channel_1000")
    
    #labware
    start_stack1 = ctx.load_labware("stack_plate_biorad96well", "D2")
    start_stack2 = ctx.load_labware("stack_plate_biorad96well", "C2")
    qbit_stack1 = ctx.load_labware("stack_plate_biorad96well", "B2")
    qbit_stack2 = ctx.load_labware("stack_plate_biorad96well", "A2")

    res = ctx.load_labware(ctx.params.qbit_reservoir, "D1")
    dil_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "C1")
    waterlid = ctx.load_labware("axygen_1_reservoir_90ml", "B1")

    final_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "A1")
    
    trash = ctx.load_waste_chute()
    qbit_pos = 'A1'
    totalcols = ncols1 + ncols2

    # helper functions
    def pip_config(type, rack):
        if type == 'partial':
            pip.configure_nozzle_layout(
                style=COLUMN,
                start="A12",
                tip_racks=[rack]
            )
        elif type == 'full':
            pip.configure_nozzle_layout(
                style = ALL, 
                tip_racks=[rack]
            )
    if ctx.params.prep_qbit:
        # distribute qbit rgnt
        ########################################################################
        pip_config('partial', partial1000)
        ########################################################################
    
        if ncols2 > 0:
            qbit_cols = qbit_stack1.columns()[::2][:ncols1] + qbit_stack2.columns()[::2][:ncols2]
        else:
            qbit_cols = qbit_stack1.columns()[::2][:ncols1]
        comment(ctx, "Adding qbit reagent to " + str(ncols1 + ncols2) + " columns")
    
        ctx.move_labware(partial1000, 'A3', use_gripper=True)
        # 15 ml are enough for 9 columns
        
        pip.well_bottom_clearance.dispense = 15
        pip.distribute(
            200 - samplevol, 
            res[qbit_pos], 
            qbit_cols, 
            touch_tip=False
        )
        pip.well_bottom_clearance.dispense = 1
        ctx.move_labware(partial1000, 'C4', use_gripper=True)

        ########################################################################
        pip_config('full', rack_full_1)
        ########################################################################

        pip.pick_up_tip(rack_full_1['A1'])
    
        pip.aspirate(18, waterlid['A1'],rate = 0.1)
        pip.air_gap(3)
        pip.aspirate(2, start_stack1['A1'], rate = 0.1)
        pip.dispense(location = dil_plate['A1'])
        pip.well_bottom_clearance.aspirate = 3
        pip.well_bottom_clearance.dispense = 3
        pip.mix(10, 15)
        pip.well_bottom_clearance.aspirate = 1
        pip.well_bottom_clearance.dispense = 1

        pip.aspirate(samplevol, dil_plate['A1'], rate = 0.1)
        pip.air_gap(3)
        pip.dispense(location = qbit_stack1['A1'])
        pip.well_bottom_clearance.aspirate = 3
        pip.well_bottom_clearance.dispense = 3
        pip.mix(10, 50)
        pip.well_bottom_clearance.aspirate = 1
        pip.well_bottom_clearance.dispense = 1
        pip.drop_tip()

        if ncols2 > 0:
            pip.pick_up_tip(rack_full_2['A1'])
    
            pip.aspirate(18, waterlid['A1'],rate = 0.1)
            pip.air_gap(3)
            pip.aspirate(2, start_stack2['A1'], rate = 0.1)
            pip.dispense(location = dil_plate['A2'])
            pip.well_bottom_clearance.aspirate = 3
            pip.well_bottom_clearance.dispense = 3
            pip.mix(10, 15)
            pip.well_bottom_clearance.aspirate = 1
            pip.well_bottom_clearance.dispense = 1
    
            pip.aspirate(samplevol, dil_plate['A2'], rate = 0.1)
            pip.air_gap(3)
            pip.dispense(location = qbit_stack2['A1'])
            pip.well_bottom_clearance.aspirate = 3
            pip.well_bottom_clearance.dispense = 3
            pip.mix(10, 50)
            pip.well_bottom_clearance.aspirate = 1
            pip.well_bottom_clearance.dispense = 1
            pip.drop_tip()

    if ctx.params.prep_plate:
        ########################################################################
        pip_config('partial', partial50)
        ########################################################################
        
        ctx.move_labware(partial50, 'A3', use_gripper=True)

        if ncols2 > 0:
            final_cols = start_stack1.columns()[::2][:ncols1] + start_stack2.columns()[::2][:ncols2]
        else:
            final_cols = start_stack1.columns()[::2][:ncols1]
        
        pip.flow_rate.aspirate = pip.flow_rate.aspirate / 4
        pip.flow_rate.dispense = pip.flow_rate.dispense / 4
        pip.transfer(25, final_cols, final_plate.columns()[:ncols1 + ncols2], new_tip = 'always')
        ctx.move_labware(partial50, 'B4', use_gripper = True)
