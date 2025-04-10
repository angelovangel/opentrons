from opentrons import protocol_api
from opentrons import types
import math

metadata= {
	'protocolName': 'PacBio SRE and Shearing',
	'author': 'Opentrons <protocols@opentrons.com>',
	'source': 'Protocol Library',
}

requirements = {
	"robotType": "Flex",
	"apiLevel": "2.18",
}
def add_parameters(parameters):
	parameters.add_bool(
		variable_name="SRE",
		display_name="Short Read Elimination",
		description="This will perform short read elimination",
		default=True)

	parameters.add_bool(
		variable_name="Shearing",
		display_name="Shearing",
		description="This will perform pipette shearing",
		default=True)

	parameters.add_bool(
		variable_name="DryRun",
		display_name="Dry Run",
		description="Dry runs will return used tips to tip rack and skip incubations on the heater shaker",
		default=False)

	parameters.add_int(
		variable_name="Samples",
		display_name="Sample Count",
		description="How many samples are being processed?",
		default=8,
		minimum=1,
		maximum=48)

	parameters.add_int(
		variable_name="cycles",
		display_name="Mix Cycles",
		description="Specify how many cycles (x100) you wish to use to shear gDNA",
		default=8,
		minimum=6,
		maximum=15,
		unit="x100 cycle")


tt_1000=0
def run(ctx):
	SRE=ctx.params.SRE
	Shearing=ctx.params.Shearing
	DryRun=ctx.params.DryRun
	Samples=ctx.params.Samples
	Columns=math.ceil(Samples/8)
	cycles=ctx.params.cycles
	
	#Modules
	mag_block           = ctx.load_module('magneticBlockV1', 'A3')
	hs					=ctx.load_module('heaterShakerModuleV1','D1')
	hs_adap				=hs.load_adapter('opentrons_96_deep_well_adapter')
	chute				=ctx.load_waste_chute()
	
	#Pipettes
	p1000     =ctx.load_instrument('flex_8channel_1000','left')
	p1000.flow_rate.aspirate= 100
	p1000.flow_rate.dispense= 100
	
	p50= ctx.load_instrument('flex_8channel_50','right')
	p50.flow_rate.aspirate=15
	p50.flow_rate.dispense=15
	
	#Tipracks
	tiprack_50_1= ctx.load_labware('opentrons_flex_96_tiprack_50ul','B3')
	tiprack_200_1=ctx.load_labware('opentrons_flex_96_tiprack_200ul','D2')
	tiprack_1000_1= ctx.load_labware('opentrons_flex_96_tiprack_1000ul','B2')
	p50.tip_racks=[tiprack_50_1]
	if Columns==1:
		tip1000=[tiprack_1000_1]

	if Columns >=2:
		tiprack_1000_2=ctx.load_labware('opentrons_flex_96_tiprack_1000ul','C2')
		tip1000=[tiprack_1000_1,tiprack_1000_2]

	if Columns>=3:
		tiprack_50_2= ctx.load_labware('opentrons_flex_96_tiprack_50ul','C3')
		tiprack_1000_3= ctx.load_labware('opentrons_flex_96_tiprack_1000ul','B1')
		p50.tip_racks=[tiprack_50_1,tiprack_50_2]
		tip1000=[tiprack_1000_1,tiprack_1000_2,tiprack_1000_3]


	if Columns>=4:
		tiprack_1000_4=ctx.load_labware('opentrons_flex_96_tiprack_1000ul','A4')
		tip1000=[tiprack_1000_1,tiprack_1000_2,tiprack_1000_3,tiprack_1000_4]
		#Lists for tip Tracking
		p1000_on_deck_slots=['B2','C2','B1']
		p1000_extension_tips=[tiprack_1000_4]

	if Columns>=5:
		tiprack_1000_5=ctx.load_labware('opentrons_flex_96_tiprack_1000ul','B4')
		tip1000=[tiprack_1000_1,tiprack_1000_2,tiprack_1000_3,tiprack_1000_4,tiprack_1000_5]

		#Lists for tip Tracking
		p1000_on_deck_slots=['B2','C2','B1']
		p1000_extension_tips=[tiprack_1000_4,tiprack_1000_5]
	
	#Labware
	Sample_Plate_1=hs_adap.load_labware('nest_96_wellplate_2ml_deep')
	samples=Sample_Plate_1.rows()[0][:12]
	RT_res= ctx.load_labware('nest_96_wellplate_2ml_deep','A2')
	
	SMRTbell_index=ctx.load_labware('biorad_96_wellplate_200ul_pcr',protocol_api.OFF_DECK)
	Index=SMRTbell_index.rows()[0][:12]
	
	Transfer_Plate_1=ctx.load_labware('biorad_96_wellplate_200ul_pcr','A1')
	TS_1=Transfer_Plate_1.rows()[0][:12]


	

	#Assignments
	if SRE==True:
		Buffer_SRE=RT_res['A1']
		Buffer_LTE=RT_res['A2']
		Supernatant_trash= RT_res['A12']
	if Shearing==True:
		SMRTbell_beads=RT_res['A3']
		EtOH	=RT_res.rows()[0][4:10]
		RSB		=RT_res['A4']

	
	
	def move_gripper(labware,new_location):
		ctx.move_labware(
		labware,
		new_location,
		use_gripper=True,
		)

	def drop_tip(pipette): #return or drop tip based on boolean value
		if DryRun==True:
			pipette.return_tip()
		else:
			pipette.drop_tip()

	def TipTrack():
		global tt_1000

		tt_1000+=1 #Add for tip tracking
		#ctx.comment(f'{tt_1000}')
		p1000.tip_racks=tip1000
		if tt_1000==37: # if tips on deck are depleted
			for x in p1000.tip_racks[:]: #discard tipracks on deck
				if x.wells()[-1].has_tip == False: #if tip racks are empty move to chute and remove empty tip rack from list
					ctx.move_labware(x,chute,use_gripper=False)
					p1000.tip_racks.remove(x)
			for y,z in zip(p1000_extension_tips,p1000_on_deck_slots):
				ctx.move_labware(y,z,use_gripper=True)
			for b in range(len(p1000_on_deck_slots)):
				try:
					del p1000_extension_tips[0]
				except:
					pass
		p1000.pick_up_tip()

	#Commands
	if SRE==True:
		hs.close_labware_latch()
		#Short Read Elimination
		for x in range(Columns):
			p50.pick_up_tip()
			p50.aspirate(50,Buffer_SRE)
			p50.dispense(50,samples[x])
			ctx.delay(seconds=3)
			drop_tip(p50)
		ctx.pause('Place a seal on Deep well plate')
		hs.set_and_wait_for_shake_speed(3000)
		ctx.delay(seconds=5)
		hs.deactivate_shaker()
		if DryRun==False:
			hs.set_and_wait_for_temperature(50)
			ctx.delay(minutes=60)
			hs.deactivate_heater()
		hs.open_labware_latch()
		'''if on_deck_thermo==True:
			hs.open_labware_latch()
			move_gripper(Sample_Plate_1,thermocycler)
			thermocycler.close_lid()
			thermocycler.close_lid()
			if DryRun==False:
				profile_SRE = [
					{'temperature':50, 'hold_time_minutes': 60}
					]
				thermocycler.execute_profile(steps=profile_SRE, repetitions=1, block_max_volume=20)
			thermocycler.set_block_temperature(4)
			thermocycler.open_lid()
		else:
			ctx.pause('Place a seal on biorad plate and move to external thermocycler')
			ctx.move_labware(
				Sample_Plate_1,
				protocol_api.OFF_DECK,
				use_gripper=False)
			ctx.pause('Return plate to slot D1')
			ctx.move_labware(
				Sample_Plate_1,
				hs_adap,
				use_gripper=False)
		hs.close_labware_latch()'''
		
		ctx.pause('Load Deep Well plate into Centrifuge, spin at 3000 rcf for 1 hour')
			
		ctx.move_labware(
			Sample_Plate_1,
			protocol_api.OFF_DECK,
			use_gripper=False,
			)

		ctx.comment('Once spinning is complete, place Deepwell plate on heatershaker')
		ctx.move_labware(
			Sample_Plate_1,
			hs_adap,
			use_gripper=False
			)
		hs.close_labware_latch()
		ctx.pause('Remove seal from plate')
		for x in range(Columns):
			p1000.tip_racks=[tiprack_200_1]
			p1000.pick_up_tip()
			p1000.flow_rate.aspirate=10
			p1000.tip_racks=tiprack_200_1
			p1000.aspirate(70,samples[x])
			ctx.delay(seconds=5)
			p1000.aspirate(20,samples[x])
			ctx.delay(seconds=3)
			p1000.dispense(90,Supernatant_trash)
			drop_tip(p1000)
		for x in range (Columns):
			p1000.flow_rate.aspirate=100
			TipTrack()
			p1000.aspirate(300,Buffer_LTE)
			p1000.dispense(300,samples[x])
			drop_tip(p1000)
		ctx.delay(minutes=13)
		for x in range(Columns):
			p1000.flow_rate.aspirate=70
			p1000.flow_rate.dispense=70
			TipTrack()
			p1000.mix(20,250,samples[x])
			drop_tip(p1000)
		hs.set_and_wait_for_shake_speed(2000)
		ctx.delay(seconds=15)
		hs.deactivate_shaker()
		hs.open_labware_latch()
		ctx.pause('Quantify DNA, when finished place plate on slot C1')
		ctx.move_labware(
			Sample_Plate_1,
			protocol_api.OFF_DECK,
			use_gripper=False)
		ctx.move_labware(
			Sample_Plate_1,
			'C1',
			use_gripper=False)
	
	#DNA Shearing Commands
	if Shearing==True:
		p1000.flow_rate.aspirate=1000
		p1000.flow_rate.dispense=1000
		for x in range(Columns):
			p1000.tip_racks=[tiprack_200_1]
			p1000.pick_up_tip()
			for i in range(cycles):
				p1000.mix(100,200,samples[x])
			drop_tip(p1000)

		ctx.pause('Remove Plate and QC sheared material- return plate to C2 for cleanup')

		#Post-Shear 1X Cleanup
		p1000.flow_rate.aspirate=1000
		p1000.flow_rate.dispense=1000
		TipTrack()
		if Columns<=5:
			p1000.mix(60,200*Columns,SMRTbell_beads)
		else:
			p1000.mix(70,1000,SMRTbell_beads)
		drop_tip(p1000)
		p1000.flow_rate.aspirate=100
		p1000.flow_rate.dispense=100
		#Adding Ampure to NA
		for x in range(Columns): 
			TipTrack()
			p1000.aspirate(300,SMRTbell_beads.bottom(z=.5))
			p1000.dispense(300, samples[x])
			p1000.mix(17,500,samples[x].bottom(z=.5))
			drop_tip(p1000)
		ctx.delay(minutes=10)
		move_gripper(Sample_Plate_1,mag_block)
		ctx.delay(minutes=9)
		for x in range(Columns):
			TipTrack()
			p1000.flow_rate.aspirate=50
			p1000.aspirate(490, samples[x])
			ctx.delay(minutes=1)
			p1000.aspirate(100,samples[x])
			p1000.dispense(590,chute)
			drop_tip(p1000)
		p1000.flow_rate.aspirate=100
		#ETOH washes
		for x in range(2):
			for x in range(Columns):
				TipTrack()
				p1000.aspirate(300, EtOH[x])
				p1000.dispense(300,samples[x].top(z=-15))
				drop_tip(p1000)
			ctx.delay(seconds=20)
			for x in range(Columns):
				TipTrack()
				p1000.aspirate(300, samples[x])
				p1000.dispense(300,chute)
				drop_tip(p1000)
		for x in range(Columns):
			p50.pick_up_tip()
			p50.flow_rate.aspirate=8
			p50.aspirate(50,samples[x].bottom(z=.2))
			p50.dispense(50,chute)
			drop_tip(p50)
		ctx.delay(minutes=1.5)
		#Resuspension
		move_gripper(Sample_Plate_1,'C1')
		for x in range(Columns):
			p50.pick_up_tip()
			p50.aspirate(50,RSB.bottom(z=.5))
			p50.dispense(50,samples[x].bottom(z=.3))
			p50.mix(10,40,samples[x])
			p50.blow_out(samples[x])
			drop_tip(p50)
		ctx.delay(minutes=5)
		move_gripper(Sample_Plate_1, mag_block)
		ctx.delay(minutes=3)
		for x in range(Columns):
			p50.pick_up_tip()
			p50.flow_rate.aspirate=8
			p50.aspirate(39, samples[x])
			ctx.delay(seconds=5)
			p50.aspirate(10,samples[x].bottom(.3))
			p50.dispense(49, TS_1[x])
			p50.blow_out(TS_1[x])
			drop_tip(p50)
	ctx.home()


#													Liquid Definitions and Assignments

	Samples_=ctx.define_liquid(name="Samples",description="Samples",display_color="#0000cc")
	for well in Sample_Plate_1.wells()[:Columns*8]:
		well.load_liquid(liquid=Samples_,volume=50)
	SMRTbell_beads_=ctx.define_liquid(name="SMRTbell Beads",description="SMRTbell Beads",display_color="#663300")
	for well in RT_res.wells()[16:24]:
		well.load_liquid(liquid=SMRTbell_beads_, volume=330*Columns)
	RSB_=ctx.define_liquid(name="Elution Buffer",description="Elution Buffer", display_color="#e6f9ff")
	for well in RT_res.wells()[24:32]:
		well.load_liquid(liquid=RSB_,volume=55*Columns)
	BufferSRE_=ctx.define_liquid(name="Buffer SRE",description="Buffer SRE", display_color="#009900")
	for well in RT_res.wells()[0:8]:
		well.load_liquid(liquid=BufferSRE_,volume=55*Columns)
	EtOH_=ctx.define_liquid(name="80% Ethanol", description="80% Ethanol",display_color="#a3a3c2")
	for well in RT_res.wells()[32:32+(Columns*8)]:
		well.load_liquid(liquid=EtOH_,volume=600)
	BufferLTE_=ctx.define_liquid(name="Buffer LTE",description="Buffer LTE",display_color="#fcc000")
	for well in RT_res.wells()[8:16]:
		well.load_liquid(liquid=BufferLTE_,volume=330*Columns)
	
