from opentrons import protocol_api

# this file serves as a template only, use shiny app or excel to replace well volumes

metadata = {
	'protocolName': '06-normalize-dna.py',
	'author': 'BCL <angel.angelov@kaust.edu.sa>',
	'description': 'Normalize DNA to a target concentration or molarity',
	'apiLevel': '2.8'
}

sourcewells1=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
destwells1=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume1=[8.828000102971428, 1.5258271782913582, 3.08980003604, 5.617818247345454, 0.5, 0.5721851918592592, 1.9934193780903229, 1.6478933525546666, 1.5072195297756097, 3.08980003604, 1.0214214995173554, 0.8765390173163121, 0.6370721723793815, 0.5517500064357143, 1.2116862886431374, 0.950707703396923, 0.7400718649197605, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#sourcewells2= this is water, defined as constant below
destwells2=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume2=[0.17199989702857188, 7.474172821708642, 5.91019996396, 3.382181752654546, 8.5, 8.427814808140742, 7.006580621909677, 7.352106647445334, 7.492780470224391, 5.91019996396, 7.978578500482644, 8.123460982683689, 8.362927827620618, 8.448249993564286, 7.788313711356863, 8.049292296603078, 8.259928135080239, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

watersource = 'A1'
finaltube = 'B1'

total_rxn_vol = 10

# exit early if there is something wrong with the dest wells
if len(destwells1) != 96:
	exit("Please make sure that there are 96 destination wells! Check that the template is correct...")

######################## BEGIN Calculations for full column transfer ########################
# the requirement is that:
# the volumes are the same for the whole column
scols1_fulltransfer = []
dcols1_fulltransfer = []
svol1_fulltransfer = []

for i in range(0, 95, 8):
	svol1 = [vol for vol in volume1[i:i + 8]]
	scols1 = [col[1:] for col in sourcewells1[i:i + 8]]
	dcols1 = [col[1:] for col in destwells1[i:i + 8]]
	
	if svol1.count(svol1[0]) == len(svol1): # all volumes in column are equal
		# collect data for transfer
		scols1_fulltransfer.append( scols1[0] )
		dcols1_fulltransfer.append( dcols1[0] )
		svol1_fulltransfer.append( svol1[0] )

# set the vol1 for the whole col transfers to 0
for i, v in enumerate(destwells1):
	if v[1:] in dcols1_fulltransfer:
		volume1[i] = 0
		
######################## END Calculations for full column transfer ########################


def run(ctx: protocol_api.ProtocolContext):
	ctx.comment("Starting normalize DNA protocol")

	destplate = ctx.load_labware('pcrplate_96_wellplate_200ul', '5', 'Destination plate') # stack of 96 well base plate and PCR plate
	sourceplate = ctx.load_labware('pcrplate_96_wellplate_200ul', '4', 'Source plate') # stack of 96 well base plate and PCR plate
	
	sourcetube = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '7', 'Tube rack')

	tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['10', '11']]
	tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3']]

	s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
	m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)

	# distribute water without tip change first, always s20
	ctx.comment("================= Starting water transfer ==========================")
	s20.distribute(	
		volume2,
		sourcetube.wells_by_name()[watersource], 
		[ destplate.wells_by_name()[i] for i in destwells2 ], 
		new_tip = 'always', 
		touch_tip = False
	)
	
	ctx.comment("================= Starting DNA transfer ==========================")
	for i, v in enumerate(scols1_fulltransfer):
		ctx.comment("Full column transfer DNA: " + str(svol1_fulltransfer[i]) + "ul from A" + v + " to A" + dcols1_fulltransfer[i])
		m20.transfer(
			svol1_fulltransfer[i], 
			sourceplate.wells_by_name()['A' + scols1_fulltransfer[i]], 
			destplate.wells_by_name()['A' + dcols1_fulltransfer[i]], 
			new_tip = 'always', 
			mix_after = (3, 4), 
			blow_out = True, 
			blowout_location = 'destination well' 
		)
		ctx.comment("--------------------------------------")
	
	# transfer what is left with s20
	s20.transfer(
		[v for v in volume1 if v > 0],
		[ sourceplate.wells_by_name()[v] for i, v in enumerate(sourcewells1) if volume1[i] > 0],
		[ destplate.wells_by_name()[v] for i, v in enumerate(destwells1) if volume1[i] > 0], 
		new_tip = 'always',
		mix_after = (3, 4), 
		blow_out = True, 
		blowout_location = 'destination well'
		)
	