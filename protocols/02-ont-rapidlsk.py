from opentrons import protocol_api

# this file serves as a template only, a Shiny app, replace-from-excel.py and the template excel file is used to change the wells and volumes

metadata = {
    'protocolName': '02-ont-rapid-pcr.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'ONT plasmid sequencing - normalise templates, add rapid adapter, incubate, pool',
    'apiLevel': '2.15'
}

# Variables replaced by the Shiny app
sourcewells1=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
destwells1=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume1=[8.828000102971428, 1.5258271782913582, 3.08980003604, 5.617818247345454, 0.5, 0.5721851918592592, 1.9934193780903229, 1.6478933525546666, 1.5072195297756097, 3.08980003604, 1.0214214995173554, 0.8765390173163121, 0.6370721723793815, 0.5517500064357143, 1.2116862886431374, 0.950707703396923, 0.7400718649197605, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#sourcewells2=['A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
destwells2=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume2=[0.17199989702857188, 7.474172821708642, 5.91019996396, 3.382181752654546, 8.5, 8.427814808140742, 7.006580621909677, 7.352106647445334, 7.492780470224391, 5.91019996396, 7.978578500482644, 8.123460982683689, 8.362927827620618, 8.448249993564286, 7.788313711356863, 8.049292296603078, 8.259928135080239, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
sourcewells3=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
destwells3=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume3=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

watersource = 'A1'
finaltube = 'B1'
ermm = 'A2'
ligmm = 'B2'
edta = 'C2'
consolidate_vol_fraction = 0.9
source_labware = 'stack_plate_biorad96well'
aspirate_factor = 1
dispense_factor = 1
pool_reuse_tip = True #for the consolidate step only, but switch to transfer if tip change is needed (consolidate does not change tips)
lsk = True # decide if LSK114 protocol is run or just rapid. Fork at the necessary points if True
barcode_vol = 1
total_rxn_vol = 11
# Variables replaced by the Shiny app

# use 1 ul barcode and 11 ul total rxn vol if it is gDNA, for plasmid use half volumes
# the decision is based on the barcode volumes (volume3)  
# if lsk: 
#     barcode_vol = 1.25
#     total_rxn_vol = 10
# elif max(volume3) == 1:
#     barcode_vol = 1
#     total_rxn_vol = 11
# else:
#     barcode_vol = 0.5
#     total_rxn_vol = 5.5

######################## Calculations for full column transfer  - for rapid barcode plate #######################
# the requirement is that:
# for ONE source column all rows go to ONE dest column AND 
# there has to be a row correspondence A-A, B-B...H-H 
# AND the volumes are the same for the whole column

scols3_fulltransfer = []
dcols3_fulltransfer = []

for i in range(0, 95, 8):
    scols3 = [col[1:] for col in sourcewells3[i:i + 8]]
    dcols3 = [col[1:] for col in destwells3[i:i + 8]]

    if([row[:1] for row in sourcewells3[i:i + 8]] ==  [row[:1] for row in destwells3[i:i + 8]] and # there is row correspondence
        scols3.count(scols3[0]) == len(scols3)): # all wells in the batch of 8 are the same column
    # collect data for transfer
        scols3_fulltransfer.append( scols3[0] )
        dcols3_fulltransfer.append( dcols3[0] )

    # set the vol3 for the whole col transfers to 0
    for i, v in enumerate(destwells3):
        if v[1:] in dcols3_fulltransfer:
            volume3[i] = 0

######################## Calculations for full column transfer  - for rapid barcode plate #######################

# exit early if there is something wrong with the dest wells
if len(destwells1) != 96:
    exit("Please make sure that there are 96 destination wells! Check the excel template is correct...")

def run(ctx: protocol_api.ProtocolContext):
    ctx.comment('----------------------------------------------------------------')
    if lsk:
        ctx.comment("Starting ONT LSK114 protocol")
    else:
        ctx.comment("Starting ONT rapid protocol")
    ctx.comment('----------------------------------------------------------------')
    odtc = ctx.load_module(module_name='thermocyclerModuleV2')
    destplate = odtc.load_labware('biorad_96_wellplate_200ul_pcr') # IMPORTANT - use biorad plates!!!

    #destplate = ctx.load_labware('pcrplate_96_wellplate_200ul', '5', 'Destination plate') # stack of 96 well base plate and PCR plate
    sourceplate = ctx.load_labware(source_labware, '4', 'Source plate') # stack of 96 well base plate and PCR plate
    barcodeplate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '9', 'Rapid barcode plate')
    #sourcetube = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5', 'Tube rack')
    tube_block = ctx.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '5', 'Tube block')
    if lsk:
        ligation_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '6', 'Ligation plate')

    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1', '2']]
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3']]

    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
    m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)

    s20.flow_rate.aspirate = s20.flow_rate.aspirate / aspirate_factor
    s20.flow_rate.dispense = s20.flow_rate.dispense / dispense_factor
    m20.flow_rate.aspirate = m20.flow_rate.aspirate / aspirate_factor
    m20.flow_rate.dispense = m20.flow_rate.dispense / dispense_factor

    ctx.comment('----------------------------------------------------------------')
    ctx.comment('Using s20 aspirate flow rate of ' + str(s20.flow_rate.aspirate) + ' ul/s')
    ctx.comment('Using s20 dispense flow rate of ' + str(s20.flow_rate.dispense) + ' ul/s')
    ctx.comment('Using m20 aspirate flow rate of ' + str(m20.flow_rate.aspirate) + ' ul/s')
    ctx.comment('Using m20 dispense flow rate of ' + str(m20.flow_rate.dispense) + ' ul/s')
    ctx.comment('----------------------------------------------------------------')

    # labels for liquids
    waterlabel = ctx.define_liquid('water', 'Water used to normalize DNA', display_color = '#e41a1c')
    poollabel = ctx.define_liquid('pool', 'Empty tube for final pool', display_color = '#377eb8')
    #bclabel = ctx.define_liquid('barcodes', 'Barcoding plate', display_color = '#99A3A4')
    tube_block[watersource].load_liquid(liquid = waterlabel, volume = sum(volume1, 100))
    tube_block[finaltube].load_liquid(liquid = poollabel, volume = 0)
    # for i in barcodeplate.wells():
    #     i.load_liquid(liquid = bclabel, volume = 1)
    if lsk:
        ermmlabel = ctx.define_liquid('ER MM', 'End repair msster mix', display_color = '#4daf4a')
        ligmmlabel = ctx.define_liquid('Lig MM', 'Ligation master mix', display_color = '#984ea3')
        edtalabel = ctx.define_liquid('EDTA', 'EDTA', display_color = '#ff7f00')
        tube_block[ermm].load_liquid( liquid = ermmlabel, volume = sum(1 for x in volume1 if x > 0) * 3.3 )
        tube_block[ligmm].load_liquid(liquid = ligmmlabel, volume = sum(1 for x in volume1 if x > 0) * 5.5)
        tube_block[edta].load_liquid(liquid = edtalabel, volume = sum(1 for x in volume1 if x > 0) * 2.2)

    # setup ODTC
    odtc.open_lid()
    odtc.set_block_temperature(temperature = 15)
    odtc.set_lid_temperature(100)

    # distribute water without tip change first
    ctx.comment("================= Starting water distribute ==========================")
    s20.distribute(	
        volume2,
        tube_block.wells_by_name()[watersource], 
        [ destplate.wells_by_name()[v] for v in destwells2 ], 
        touch_tip = False, 
        disposal_volume = 2, 
        blow_out = True, 
        blowout_location = 'trash'
    )
    
    # distribute End Repair MM if LSK
    if lsk:
        ctx.comment("================= LSK - End prep MM distribute ==========================")
        s20.distribute(
            3,
            tube_block.wells_by_name()[ermm],
            [destplate.wells_by_name()[v] for i, v in enumerate(destwells2) if volume1[i] > 0 ],
            disposal_volume = 1,
            blow_out = False
        )

    ctx.comment("================= Starting plasmid transfer ==========================")
    # add plasmid, changing tip
    
    s20.transfer(
        [v for v in volume1 if v > 0],
        [ sourceplate.wells_by_name()[v] for i, v in enumerate(sourcewells1) if volume1[i] > 0],
        [ destplate.wells_by_name()[v] for i, v in enumerate(destwells1) if volume1[i] > 0], 
        new_tip = 'always',
        mix_after = (5, total_rxn_vol/1.5) if lsk else (0, 0),
        blow_out = True, 
        blowout_location = 'destination well'
        )

    # If LSK, end prep incubation, transfer DNA to ligation plate and continue up to barcode addition
    #
    if lsk:
        # pause - this is optional in the Shiny app to cover rxn plate
        # optional pause #ctx.pause("Optional pause to cover plate with aluminum foil") 
        odtc.close_lid()
        #odtc.set_lid_temperature(100)
        odtc.set_block_temperature(20, hold_time_minutes = 5)
        odtc.set_block_temperature(65, hold_time_minutes = 5)
        odtc.set_block_temperature(15)
        odtc.open_lid()

        # water to ligation plate
        s20.distribute(
            3,
            tube_block.wells_by_name()[watersource],
            [ligation_plate.wells_by_name()[v] for i, v in enumerate(destwells2) if volume1[i] > 0],
            disposal_volume = 1,
            blow_out = False
        )
        # Ligation MM to ligation plate
        s20.distribute(
            5,
            tube_block.wells_by_name()[ligmm],
            [ligation_plate.wells_by_name()[v] for i, v in enumerate(destwells2) if volume1[i] > 0],
            disposal_volume = 1,
            blow_out = False
        )
        # Samples to ligation plate
        for i,v in enumerate(dcols3_fulltransfer):
            ctx.comment('LSK samples full column transfer to ligation plate')
            m20.transfer(
                1,
                destplate.wells_by_name()['A' + dcols3_fulltransfer[i]],
                ligation_plate.wells_by_name()['A' + dcols3_fulltransfer[i]],
                new_tip = 'always',
                mix_after = (5, 5)
            )
        for i, v in enumerate(volume3):
            if v > 0:
                ctx.comment('LSK samples s20 transfer')
                s20.transfer(
                    1,
                    destplate.wells_by_name()[sourcewells1[i]],
                    ligation_plate.wells_by_name()[sourcewells1[i]],
                    mix_after = (5,5)
                )

    # add barcodes, full columns if possible, has to be as fast as possible
    # depending on lsk, barcodes are added to the destplate or ligation plate
    
    #++++++++++++++++++++++++++++++++++++++++++++++++
    # From here on, the working plate can be either the original destplate or the ligation plate
    if lsk:
        workingplate = ligation_plate
    else:
        workingplate = destplate
    #++++++++++++++++++++++++++++++++++++++++++++++++
        
    ctx.comment("================= Starting barcode transfer ==========================")
    ctx.pause("Pause before barcode transfer") 
    
    for i, v in enumerate(scols3_fulltransfer):
        ctx.comment("Full column transfer barcode plate: " + str(barcode_vol) + "ul from A" + v + " to A" + dcols3_fulltransfer[i])
        m20.transfer(
        barcode_vol, 
        barcodeplate.wells_by_name()['A' + scols3_fulltransfer[i]], 
        workingplate.wells_by_name()['A' + dcols3_fulltransfer[i]], 
        new_tip = 'always', 
        mix_after = (8, total_rxn_vol/1.5), 
        blow_out = True, 
        blowout_location = 'destination well' 
        )
        ctx.comment("--------------------------------------")

    # s20 transfer barcodes for what is left
    for i, v in enumerate(volume3):
        if v > 0:
            ctx.comment("s20 transfer barcode plate")
            s20.transfer(
                barcode_vol,
                barcodeplate.wells_by_name()[sourcewells3[i]], 
                workingplate.wells_by_name()[destwells3[i]], 
                new_tip = 'always', 
                mix_after = (8, total_rxn_vol/1.5), 
                blow_out = True, 
        		blowout_location = 'destination well'
            )
            ctx.comment("--------------------------------------")
    if lsk:
        ctx.delay(minutes = 20, msg = 'Incubate ligation for 20 minutes')
        # Add EDTA
        ctx.comment("================= Add EDTA ==========================")
        s20.distribute(
            2,
            tube_block.wells_by_name()[edta],
            [ workingplate.wells_by_name()[v] for i, v in enumerate(destwells2) if volume1[i] > 0 ]
        )
        

    # ODTC if rapid only
    if not lsk:
        # pause - this is optional in the Shiny app to cover rxn plate
        # optional pause #ctx.pause("Optional pause to cover plate with aluminum foil") 
        odtc.close_lid()
        #odtc.set_lid_temperature(100)
        odtc.set_block_temperature(30, hold_time_minutes = 2)
        odtc.set_block_temperature(80, hold_time_minutes = 2)
        odtc.set_block_temperature(15)
        odtc.open_lid()

    # Pool
    ctx.comment("================= Pool samples =========================")


    # use same tip as everything is aspirated, change to transfer if needed
    if pool_reuse_tip:
        s20.consolidate(
            total_rxn_vol * consolidate_vol_fraction,
            [ workingplate.wells_by_name()[v] for i, v in enumerate(destwells1) if volume1[i] > 0 ], 
            tube_block.wells_by_name()[finaltube]
        )
    else:
        s20.transfer(
            total_rxn_vol * consolidate_vol_fraction,
            [ workingplate.wells_by_name()[v] for i, v in enumerate(destwells1) if volume1[i] > 0 ],
            tube_block.wells_by_name()[finaltube], 
            new_tip = 'always'
        )

    odtc.deactivate_lid()
    odtc.deactivate_block()
    poolvol = len([v for v in volume1 if v > 0]) * (total_rxn_vol * consolidate_vol_fraction)

    ctx.comment("Final volume of pool: " + str(poolvol) + " ul")
    ctx.comment("Add " + str(poolvol) + " ul SPRI beads, incubate 5 minutes. Wash beads 2x with 80 EtOH, aspirate all EtOH and dry 30 sec. Resuspend in 15 ul EB, incubate 10 minutes, take out supernatant and continue with RAP addition")
    
    ctx.comment("================= End =========================")
    