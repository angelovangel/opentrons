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
		default=3,
		minimum=1,
		maximum=12,
		unit="columns"
	)
	parameters.add_int(
		variable_name='sample_volume',
		display_name="Sample volume",
		description="Volume of sample to be transferred to final plate (ul)",
		default=20,
		minimum=1,
		maximum=100,
		unit="ul"
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
		description = 'Dilute 5x and add 5 ul to qbit reagent (=1 ul sample)',
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
	parameters.add_int(
		variable_name='asp_offset',
		display_name="Aspiration offset",
		description="Offset from bottom of well for aspiration (mm)",
		default=2,
		minimum=0,
		maximum=10,
	)
	parameters.add_int(
		variable_name='disp_offset',
		display_name="Dispense offset",
		description="Offset from bottom of well for dispense (mm)",
		default=4,
		minimum=0,
		maximum=20
	)

def run(ctx: protocol_api.ProtocolContext):
	ncols = ctx.params.num_columns
	asp = ctx.params.asp_offset
	disp = ctx.params.disp_offset

	required_qbit = int(round(ncols * 8 * 195 * 1.1))
	ctx.pause(
		f'Estimated qbit reagent needed for {ncols} columns: {required_qbit} µl.\n'
	)

	if ctx.params.qbit_reservoir == "nest_12_reservoir_15ml" and ncols > 6:
		raise Exception(
			'ERROR: nest_12_reservoir_15ml cannot hold enough reagent for more than 6 columns. '
			'Reduce num_columns to 6 or select a larger reservoir.'
		)

	tips50 = [ctx.load_labware("opentrons_flex_96_filtertiprack_50ul", loc) for loc in ['B3', 'B2']]
	tips1000 = ctx.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A3")
	
	#pip_left = ctx.load_instrument('flex_1channel_1000', 'left')
	pip_right = ctx.load_instrument('flex_8channel_1000', 'right', tip_racks = [tips1000])

	#labware
	start_stack = ctx.load_labware(load_name = "stack_plate_biorad96well", location = "D2", label = "Stacked strips (samples)")
	dil_plate = ctx.load_labware(load_name = "biorad_96_wellplate_200ul_pcr", location = "C2", label = "Dilution plate")
	qbit_plate = ctx.load_labware(load_name = "biorad_96_wellplate_200ul_pcr", location = "C1", label = "Qbit plate")
	final_plate = ctx.load_labware(load_name = "biorad_96_wellplate_200ul_pcr", location = "B1", label = "Final plate")
	res = ctx.load_labware(load_name = ctx.params.qbit_reservoir, location = "D1", label = "Qbit reagent reservoir")
	waterlid = ctx.load_labware(load_name = "axygen_1_reservoir_90ml", location = "C3", label = "Water lid")
	trash = ctx.load_waste_chute()
		
	# distribute qbit reagent
	pip_right.flow_rate.aspirate = 50
	pip_right.flow_rate.dispense = 150

	pip_right.distribute(
		195, 
		res['A1'].bottom(asp),
		[col[0].bottom(disp) for col in qbit_plate.columns()[:ncols]],
		disposal_volume = 10,
		blow_out = True,
		blowout_location = 'source well'
	)
	

	# dilute and add samples to qbit plate
	pip_right.configure_nozzle_layout(style = ALL, tip_racks = tips50)
	if ctx.params.prep_qbit:
		for col in range(ncols):
			pip_right.pick_up_tip()
			pip_right.aspirate(8, waterlid['A1'].bottom(asp), rate=0.1)
			pip_right.aspirate(2, start_stack.rows()[0][col].bottom(asp), rate=0.05)
			pip_right.dispense(10, dil_plate.rows()[0][col].bottom(disp))
			pip_right.mix(repetitions = 5, volume = 18, location = dil_plate.rows()[0][col].bottom(disp))
			pip_right.aspirate(5, dil_plate.rows()[0][col].bottom(asp), rate=0.1)
			pip_right.dispense(5, qbit_plate.rows()[0][col].bottom(disp))
			pip_right.mix(repetitions = 7, volume = 40, location = qbit_plate.rows()[0][col].bottom(disp + 2))
			pip_right.drop_tip()
	
	if ctx.params.prep_plate:
		pip_right.flow_rate.aspirate = 5
		pip_right.flow_rate.dispense = 25
		pip_right.transfer(
			ctx.params.sample_volume, 
			[well.bottom(asp) for well in start_stack.rows()[0][:ncols]], 
			[well.bottom(disp) for well in final_plate.rows()[0][:ncols]], 
			new_tip='always'
		)