from opentrons import protocol_api

# this file serves as a template only, use shiny app or excel to replace well volumes

metadata = {
	'protocolName': '06-normalize-dna.py',
	'author': 'BCL <angel.angelov@kaust.edu.sa>',
	'description': 'Normalize DNA to a target concentration or molarity',
	'apiLevel': '2.8'
}

# destwells is fixed
sourcewells=['A1', '', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
destwells=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume1=[1, 0, 10, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# water
volume2=[9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

left_mount = 'p20_single_gen2'
right_mount = 'p20_multi_gen2'
watersource = 'A1'

# exit early if there is something wrong with the dest wells
if len(destwells) != 96:
	exit("Please make sure that there are 96 destination wells! Check that the template is correct...")

######################## BEGIN Calculations for full column transfer ########################
# the requirement is that:
# for ONE source column all rows go to ONE dest column AND 
# there is row correspondence, i.e. A-A, B-B...H-H AND
# the volumes are the same for the whole column
scols1_fulltransfer = []
dcols1_fulltransfer = []
svol1_fulltransfer = []

for i in range(0, 95, 8):
	svol1 = [vol for vol in volume1[i:i + 8]]
	scols1 = [col[1:] for col in sourcewells[i:i + 8]]
	dcols1 = [col[1:] for col in destwells[i:i + 8]]
	
	if ([row[:1] for row in sourcewells[i:i + 8]] ==  [row[:1] for row in destwells[i:i + 8]] and # there is row correspondence 
		scols1.count(scols1[0]) == len(scols1) and # all wells in the batch of 8 are the same column
		svol1.count(svol1[0]) == len(svol1) # all volumes in column are equal
		): 
		# collect data for transfer
		scols1_fulltransfer.append( scols1[0] )
		dcols1_fulltransfer.append( dcols1[0] )
		svol1_fulltransfer.append( svol1[0] )

# set the vol1 for the whole col transfers to 0
for i, v in enumerate(destwells):
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
	s20 = ctx.load_instrument(left_mount, mount='left', tip_racks=tips20_single)
	m20 = ctx.load_instrument(right_mount, mount='right', tip_racks=tips20_multi)

	# distribute water without tip change first, always s20
	ctx.comment("================= Starting water transfer ==========================")
	if any(vol > 0 for vol in volume2):
		s20.distribute(	
			volume2,
			sourcetube.wells_by_name()[watersource], 
			[ destplate.wells_by_name()[i] for i in destwells ], 
			new_tip = 'always', 
			touch_tip = False
		)
	
	ctx.comment("================= Starting DNA transfer ==========================")
	for i, v in enumerate(scols1_fulltransfer):
		if svol1_fulltransfer[i] > 0:
			ctx.comment("Full column transfer DNA: " + str(svol1_fulltransfer[i]) + "ul from A" + v + " to A" + dcols1_fulltransfer[i])
			m20.transfer(
			svol1_fulltransfer[i], 
			sourceplate.wells_by_name()['A' + scols1_fulltransfer[i]], 
			destplate.wells_by_name()['A' + dcols1_fulltransfer[i]], 
			new_tip = 'always', 
			mix_after = (3, svol1_fulltransfer[i]*0.7), 
			blow_out = True, 
			blowout_location = 'destination well' 
			)
			ctx.comment("------------------------------------------------------------")
	
	# transfer what is left with s20
	ctx.comment("Single channel transfer DNA ")
	
	for i, v in enumerate(volume1):
		if v > 0:
			s20.transfer(
			v,
        	sourceplate.wells_by_name()[sourcewells[i]] ,
        	destplate.wells_by_name()[destwells[i]],
			new_tip = 'always',
			mix_after = (3, v * 0.7), 
			blow_out = True, 
			blowout_location = 'destination well'
			)
	ctx.comment("================= END =================")