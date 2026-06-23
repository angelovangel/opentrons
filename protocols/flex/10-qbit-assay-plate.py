from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL

# qbit assay Flex (left 1-channel 1ml, right 8-channel 1 ml), plate assay
# start with stacked strips in Biorad (every column)

metadata = {
	'protocolName': '10-qbit-assay-plate.py',
	'author': 'BCL <angel.angelov@kaust.edu.sa>',
	'description': 'Qbit assay on Flex, strip/stack to plate'
}

requirements = {
	"robotType": "Flex",
	"apiLevel": "2.18"
}


# Runtime params
def add_parameters(parameters):
	parameters.add_int(
		variable_name='num_columns', 
		display_name="Number of columns",
		description="How many columns to quantify (max 12 are allowed)",
		default=2,
		minimum=1,
		maximum=12,
		unit="columns"
	)
	parameters.add_bool(
		variable_name = 'prep_plate',
		display_name = 'Prepare run plate',
		description = 'Pipet strips to final plate',
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
	ncols = ctx.params.num_columns

	tips50 = [ctx.load_labware("opentrons_flex_96_filtertiprack_50ul", loc) for loc in ['B3', 'B2']]
	tips1000 = ctx.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A3")
	
	#pip_left = ctx.load_instrument('flex_1channel_1000', 'left')
	pip_right = ctx.load_instrument('flex_8channel_1000', 'right', tip_racks = [tips1000])

	#labware
	start_stack = ctx.load_labware("stack_plate_biorad96well", "D2")
	dil_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "C2")
	qbit_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "C1")
	final_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "B1")
	res = ctx.load_labware(ctx.params.qbit_reservoir, "D1")
	waterlid = ctx.load_labware("axygen_1_reservoir_90ml", "C3")
	trash = ctx.load_waste_chute()

	# distribute qbit reagent
	pip_right.well_bottom_clearance.dispense = 15
	pip_right.distribute(
		195, 
		res['A1'],
		qbit_plate.columns()[:ncols],
	)
	pip_right.well_bottom_clearance.dispense = 1

	# dilute and add samples to qbit plate
	pip_right.configure_nozzle_layout(style = ALL, tip_racks = tips50)
	if ctx.params.prep_qbit:
		for col in range(ncols):
			pip_right.pick_up_tip()
			pip_right.aspirate(18, waterlid['A1'], rate=0.1)
			pip_right.aspirate(2, start_stack.rows()[0][col], rate=0.1)
			pip_right.dispense(20, dil_plate.rows()[0][col])
			pip_right.mix(repetitions = 3, volume = 18, location = dil_plate.rows()[0][col])
			pip_right.drop_tip()
	
	if ctx.params.prep_plate:
		pip_right.flow_rate.aspirate = 50
		pip_right.flow_rate.dispense = 150
		pip_right.transfer(
			20, 
			start_stack.rows()[0][:ncols], 
			final_plate.rows()[0][:ncols], 
			new_tip='always'
		)