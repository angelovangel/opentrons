from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL


metadata = {
    "protocolName": "Sanger Flex Protocol full plate",
    "description": """ Add BigDye (variable number of columns), transfer sample from plate or strips""",
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
        variable_name="sample_vol",
        display_name="Sample volume",
        description="Sample volume to transfer (ul)",
        default=15,
        minimum=5,
        maximum=15,
        unit="uL"
    )
    parameters.add_int(
        variable_name="mm_vol",
        display_name="Mastermix volume",
        description="BigDye mastermix volume to transfer (ul)",
        default=10,
        minimum=5,
        maximum=10,
        unit="uL"
    )

    parameters.add_str(
        variable_name="source_type",
        display_name="Source type",
        description="Source plate/strip labware type",
        choices=[
            {"display_name": "Biorad plate", "value": "biorad_96_wellplate_200ul_pcr"},
            {"display_name": "Stack in Biorad plate", "value": "stack_plate_biorad96well"},
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

    parameters.add_int(
        variable_name="aspirate_offset",
        display_name="Aspirate offset",
        description="Aspirate offset from the bottom of the well",
        default=2,
        minimum=0,
        maximum=5,
        unit="mm"   
    )

    parameters.add_int(
        variable_name="dispense_offset",
        display_name="Dispense offset",
        description="Dispense offset from the bottom of the well",
        default=3,
        minimum=0,
        maximum=5,
        unit="mm"
    )
    parameters.add_bool(
        variable_name="return_tips",
        display_name="Return tips to tip box",
        description="Select this to return tips to tip box (discard in waste bin otherwise)",
        default=False
    )
    


def run(ctx: protocol_api.ProtocolContext):
    
    samplevol = ctx.params.sample_vol
    mmvol = ctx.params.mm_vol
    ncols = ctx.params.ncolumns
    trashtips = not ctx.params.return_tips

    # tips and pipette
    
    full50 = ctx.load_labware(
        load_name="opentrons_flex_96_filtertiprack_50ul", 
        location='A3', 
        adapter="opentrons_flex_96_tiprack_adapter"
            ) 

    partial200 = ctx.load_labware(
        load_name="opentrons_flex_96_filtertiprack_200ul", 
        location='C3'
    )
    
    pip = ctx.load_instrument("flex_96channel_1000")
    
    #labware
    start_plate = ctx.load_labware(ctx.params.source_type, "C2")
    res = ctx.load_labware("nest_12_reservoir_15ml", "D2")
    rxn_stack = ctx.load_labware("stack_plate_biorad96well", "C1")
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
    pip_config('partial', partial200)
    ########################################################################
    pip.well_bottom_clearance.aspirate = ctx.params.aspirate_offset
    pip.well_bottom_clearance.dispense = ctx.params.dispense_offset

    pip.flow_rate.aspirate = 10
    pip.flow_rate.dispense = 30
    pip.distribute(10 ,res[mm_pos], rxn_stack.rows()[0][:ncols], disposal_volume = 10, touch_tip=False)
    

    # transfer reactions
    ########################################################################
    pip_config('full', full50)
    ########################################################################
    pip.well_bottom_clearance.aspirate = ctx.params.aspirate_offset
    pip.well_bottom_clearance.dispense = ctx.params.dispense_offset

    pip.transfer(
        samplevol, 
        start_plate['A1'], 
        rxn_stack['A1'], 
        mix_after = (6, 10), 
        touch_tip = True, 
        trash = trashtips
    )
    