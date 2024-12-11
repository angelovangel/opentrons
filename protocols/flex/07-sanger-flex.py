from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL


metadata = {
    "protocolName": "Sanger Flex Protocol",
    "description": """Transfer sample from plate or strips, add BigDye, variable number of columns""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {"robotType": "Flex", "apiLevel": "2.21"}
    
def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")


### Parameters ###
def add_parameters(parameters):
    parameters.add_int(
        variable_name="rxn_vol",
        display_name="Sample volume",
        description="Sanger sample volume",
        default=15,
        minimum=10,
        maximum=15,
        unit="uL"
    )

    parameters.add_str(
        variable_name="source_type",
        display_name="Source type",
        description="Start reaction labware type",
        choices=[
            {"display_name": "Biorad plate", "value": "biorad_96_wellplate_200ul_pcr"},
            {"display_name": "Stack of strips in Biorad plate", "value": "stack_plate_biorad96well"},
        ],
        default="stack_plate_biorad96well",
    )

    parameters.add_int(
        variable_name='ncolumns', 
        display_name="Number of columns to process",
        description="Number of columns to process",
        default=12,
        minimum=1,
        maximum=12,
        unit="columns"
    )
    


def run(ctx: protocol_api.ProtocolContext):
    
    samplevol = ctx.params.rxn_vol
    ncols = ctx.params.ncolumns

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
    start_stack = ctx.load_labware("stack_plate_biorad96well", "C2")
    start_plate = ctx.load_labware("stack_plate_biorad96well", "C1")
    res = ctx.load_labware("nest_12_reservoir_15ml", "D2")

    rxn_stack = ctx.load_labware("stack_plate_biorad96well", "D1")
    
    trash = ctx.load_waste_chute()
    mm_pos = 'A1'

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
    
    # distribute MM to rxn_stack
    ########################################################################
    pip_config('partial', partial1000)
    ########################################################################
    ctx.move_labware(partial1000, 'A3', use_gripper=True)
    pip.well_bottom_clearance.dispense = 1

    pip.distribute(10 ,res[mm_pos], rxn_stack.columns()[:ncols])

    # if ctx.params.prep_qbit:
    #     # distribute qbit rgnt
    #     ########################################################################
    #     pip_config('partial', partial1000)
    #     ########################################################################
    
    #     if ncols2 > 0:
    #         qbit_cols = qbit_stack1.columns()[::2][:ncols1] + qbit_stack2.columns()[::2][:ncols2]
    #     else:
    #         qbit_cols = qbit_stack1.columns()[::2][:ncols1]
    #     comment(ctx, "Adding qbit reagent to " + str(ncols1 + ncols2) + " columns")
    
    #     ctx.move_labware(partial1000, 'A3', use_gripper=True)
    #     # 15 ml are enough for 9 columns
        
    #     pip.well_bottom_clearance.dispense = 15
    #     pip.distribute(
    #         200 - samplevol, 
    #         res[qbit_pos], 
    #         qbit_cols, 
    #         touch_tip=False
    #     )
    #     pip.well_bottom_clearance.dispense = 1
    #     ctx.move_labware(partial1000, 'C4', use_gripper=True)

    #     ########################################################################
    #     pip_config('full', rack_full_1)
    #     ########################################################################

    #     pip.pick_up_tip(rack_full_1['A1'])
    
    #     pip.aspirate(18, waterlid['A1'],rate = 0.1)
    #     pip.air_gap(3)
    #     pip.aspirate(2, start_stack1['A1'], rate = 0.1)
    #     pip.dispense(location = dil_plate['A1'])
    #     pip.well_bottom_clearance.aspirate = 3
    #     pip.well_bottom_clearance.dispense = 3
    #     pip.mix(10, 15)
    #     pip.well_bottom_clearance.aspirate = 1
    #     pip.well_bottom_clearance.dispense = 1

    #     pip.aspirate(samplevol, dil_plate['A1'], rate = 0.1)
    #     pip.air_gap(3)
    #     pip.dispense(location = qbit_stack1['A1'])
    #     pip.well_bottom_clearance.aspirate = 3
    #     pip.well_bottom_clearance.dispense = 3
    #     pip.mix(10, 50)
    #     pip.well_bottom_clearance.aspirate = 1
    #     pip.well_bottom_clearance.dispense = 1
    #     pip.drop_tip()

    #     if ncols2 > 0:
    #         pip.pick_up_tip(rack_full_2['A1'])
    
    #         pip.aspirate(18, waterlid['A1'],rate = 0.1)
    #         pip.air_gap(3)
    #         pip.aspirate(2, start_stack2['A1'], rate = 0.1)
    #         pip.dispense(location = dil_plate['A2'])
    #         pip.well_bottom_clearance.aspirate = 3
    #         pip.well_bottom_clearance.dispense = 3
    #         pip.mix(10, 15)
    #         pip.well_bottom_clearance.aspirate = 1
    #         pip.well_bottom_clearance.dispense = 1
    
    #         pip.aspirate(samplevol, dil_plate['A2'], rate = 0.1)
    #         pip.air_gap(3)
    #         pip.dispense(location = qbit_stack2['A1'])
    #         pip.well_bottom_clearance.aspirate = 3
    #         pip.well_bottom_clearance.dispense = 3
    #         pip.mix(10, 50)
    #         pip.well_bottom_clearance.aspirate = 1
    #         pip.well_bottom_clearance.dispense = 1
    #         pip.drop_tip()

    # if ctx.params.prep_plate:
    #     ########################################################################
    #     pip_config('partial', partial50)
    #     ########################################################################
        
    #     ctx.move_labware(partial50, 'A3', use_gripper=True)

    #     if ncols2 > 0:
    #         final_cols = start_stack1.columns()[::2][:ncols1] + start_stack2.columns()[::2][:ncols2]
    #     else:
    #         final_cols = start_stack1.columns()[::2][:ncols1]
        
    #     pip.flow_rate.aspirate = pip.flow_rate.aspirate / 4
    #     pip.flow_rate.dispense = pip.flow_rate.dispense / 4
    #     pip.transfer(25, final_cols, final_plate.columns()[:ncols1 + ncols2], new_tip = 'always')
    #     ctx.move_labware(partial50, 'B4', use_gripper = True)
