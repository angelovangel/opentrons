# this file serves as a template only, Shiny app or replace-from-excel.py and the template excel file is used to change the wells and volumes
from opentrons import protocol_api
from collections import Counter

########################## metadata ##########################
metadata = {
    'protocolName': 'Sanger sequencing setup Flex',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Transfer templates and primers to destination plate, add Sequencing master mix',
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.18"
}

### Replaced by Shiny app
sourcewells1=['','','','','','','','','A2','B2','C2','D2','E2','F2','G2','H2','','B3','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
destwells1=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume1=[0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 15, 15, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sourcewells2=['A1','B1','C1','D1','E1','F1','G1','H1','','','','','','','','','A3','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
destwells2=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume2=[15, 15, 15, 15, 15, 15, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sourcewells3=['','','','','','','','','','','','','','','','','A1','A1','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
destwells3=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume3=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
dmso=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.5, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

left_mount = 'flex_1channel_1000'
right_mount = 'flex_8channel_1000'
left_tips = 'opentrons_flex_96_filtertiprack_50ul'
multi_tips = 'opentrons_flex_96_filtertiprack_50ul'

change_primer_tip = True
mm_pos = 'D6'
dmso_pos = 'C6'

### Replaced by Shiny app

# for those dest where dmso is added, reduce sample volume with 1.5 ul
for i, v in enumerate(destwells1):
    if dmso[i] > 0:
        if volume1[i] > 0: volume1[i] = volume1[i] - 1.5
        if volume2[i] > 0: volume2[i] = volume2[i] - 1.5

# exit early if there is something wrong with the dest wells
if len(destwells1) != 96:
    exit("Please make sure that there are 96 destination wells! Check the excel template is correct...")


######################## Master mix calculations ########################
# get number of rxns, to use in calculating MM
rxns = len(
    list(filter(lambda n: n > 0, volume1)) + 
    list(filter(lambda n: n > 0, volume2))
    #list(filter(lambda n: n > 0, volume3)) # these are primers, so no MM added here
    )

# get non-empty dest columns, by using the index of the volumes
# these are used to decide where to distribute PCR mm
destwells1_ne_index = [index for index, value in enumerate(volume1) if value > 0]
destwells1_pcr = [destwells1[i] for i in destwells1_ne_index]

destwells2_ne_index = [index for index, value in enumerate(volume2) if value > 0]
destwells2_pcr = [destwells2[i] for i in destwells2_ne_index]

# get columns with at least one rxn, use this to transfer PCR mm for the whole column
# e.g. wet lab has to try to fill columns with reactions
destwells_all_pcr = destwells1_pcr + destwells2_pcr
#print(destwells_all_pcr)
destcolumns_num_sorted_pcr = sorted(list(set([int(col[1:]) for col in destwells_all_pcr]))) # converting the list to a set gives unique elements
destcolumns_pcr = ['A' + str(x) for x in destcolumns_num_sorted_pcr] # restore well names to use with p20_multi
# print(destcolumns)

# 5 ul per reaction, 40 ul per column needed (44 with overhead)
# mastermix = len(destcolumns_pcr) * 44

# determine volumes per row for the MM strip col 1 in position 2
rows_mm_vols = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}
rows_counts = Counter([row[:1] for row in destwells_all_pcr]) # count how many A, B ... to determine MM needed in each row
rows_mm_vols.update(rows_counts)
rows_mm_vols.update((x, y * 6) for x, y in rows_mm_vols.items()) # 6 ul per reaction here but 5 ul used
mastermix = sum(rows_mm_vols.values()) * 1.1 # or rxns * 5.5
######################## Master mix calculations ########################

######################## Calculations for full column transfer ########################
# the requirement is that:
# for ONE source column all rows go to ONE dest column AND 
# there has to be a row correspondence A-A, B-B...H-H 
# AND the volumes are the same for the whole column
scols1_fulltransfer = []
svol1_fulltransfer = []
dcols1_fulltransfer = []

scols2_fulltransfer = []
svol2_fulltransfer = []
dcols2_fulltransfer = []

for i in range(0, 95, 8):

    scols1 = [col[1:] for col in sourcewells1[i:i + 8]]
    svol1 = [vol for vol in volume1[i:i + 8]]
    dcols1 = [col[1:] for col in destwells1[i:i + 8]]

    scols2 = [col[1:] for col in sourcewells2[i:i + 8]]
    svol2 = [vol for vol in volume2[i:i + 8]]
    dcols2 = [col[1:] for col in destwells2[i:i + 8]]

   # elegant solution to see if requirements are met
    if( [row[:1] for row in sourcewells1[i:i + 8]] ==  [row[:1] for row in destwells1[i:i + 8]] and # there is row correspondence
        scols1.count(scols1[0]) == len(scols1) and # all wells in the batch of 8 are the same column
        svol1.count(svol1[0]) == len(svol1) # all volumes in column are equal
        ):
        # collect data for transfer
        scols1_fulltransfer.append( scols1[0] )
        svol1_fulltransfer.append( svol1[0])
        dcols1_fulltransfer.append( dcols1[0] )
        #print( scols1_fulltransfer, ": ", dcols1_fulltransfer, "volume: ", svol1_fulltransfer)

    if( [row[:1] for row in sourcewells2[i:i + 8]] ==  [row[:1] for row in destwells2[i:i + 8]] and 
        scols2.count(scols2[0]) == len(scols2) and 
        svol2.count(svol2[0]) == len(svol2) ):
        # collect data for transfer
        scols2_fulltransfer.append( scols2[0] )
        svol2_fulltransfer.append( svol2[0])
        dcols2_fulltransfer.append( dcols2[0] )
        #print( scols2_fulltransfer, ": ", dcols2_fulltransfer, "volume: ")

# set the vol1 and vol2 for the whole col transfers to 0, this way they are skipped by the single transfers but the primers are added in case
for i, v in enumerate(destwells1):
    if v[1:] in dcols1_fulltransfer:
        volume1[i] = 0
    
for i, v in enumerate(destwells2):
    if v[1:] in dcols2_fulltransfer:
        volume2[i] = 0

#exit


######################## Calculations for full column transfer ########################
def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")


def run(ctx: protocol_api.ProtocolContext):

    ctx.load_waste_chute()

    comment(
        ctx,
        "Starting setup of " + 
        str(rxns) +
         " reactions in " + 
        str(len(destcolumns_pcr)) + 
        " destination plate columns.\nHave a coffee..."
        )

    # Use stack as dest, no PCR here
    destplate = ctx.load_labware('stack_plate_biorad96well', 'C1', 'Destination plate')
    sourceplate = ctx.load_labware('stack_plate_biorad96well', 'B2', 'Source plate') 
    sourcestrip = ctx.load_labware('stack_strip_biorad96well', 'B1', 'Source strip') 
    sourcetube = ctx.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', 'C2', 'Tube block')
    
    tips_left = [ctx.load_labware(left_tips, slot) for slot in ['A1', 'A2']]
    tips_multi = [ctx.load_labware(multi_tips, slot) for slot in ['A3']]

    pip_single = ctx.load_instrument(left_mount, mount='left', tip_racks=tips_left)
    pip_multi = ctx.load_instrument(right_mount, mount='right', tip_racks=tips_multi)

    pip_single.flow_rate.aspirate = 100
    pip_single.flow_rate.dispense = 100
    pip_single_original_flowrate = 100
    pip_multi.flow_rate.aspirate = 100
    pip_multi.flow_rate.dispense = 100

    # Define and load liquids
    liquid_mm = ctx.define_liquid(name="Master Mix", description="Sequencing Master Mix", display_color="#00CC00")
    liquid_dmso = ctx.define_liquid(name="DMSO", description="DMSO", display_color="#0000CC")
    liquid_primer = ctx.define_liquid(name="Primer", description="Sequencing Primer", display_color="#CC0000")
    liquid_template1 = ctx.define_liquid(name="Template (Plate)", description="DNA Template", display_color="#CCCC00")
    liquid_template2 = ctx.define_liquid(name="Template (Strip)", description="DNA Template", display_color="#CC00CC")

    sourcetube.wells_by_name()[mm_pos].load_liquid(liquid=liquid_mm, volume=mastermix + 20)
    
    dmso_vol = sum(dmso)
    if dmso_vol > 0:
        sourcetube.wells_by_name()[dmso_pos].load_liquid(liquid=liquid_dmso, volume=dmso_vol + 10)
    
    primer_vols = {}
    for w, vol in zip(sourcewells3, volume3):
        if w and vol > 0:
            primer_vols[w] = primer_vols.get(w, 0) + vol
    for w, vol in primer_vols.items():
        sourcetube.wells_by_name()[w].load_liquid(liquid=liquid_primer, volume=vol + 10)

    template1_vols = {}
    for w, vol in zip(sourcewells1, volume1):
        if w and vol > 0:
            template1_vols[w] = template1_vols.get(w, 0) + vol
    for c, vol in zip(scols1_fulltransfer, svol1_fulltransfer):
        for r in 'ABCDEFGH':
            w = r + c
            template1_vols[w] = template1_vols.get(w, 0) + vol
    for w, vol in template1_vols.items():
        sourceplate.wells_by_name()[w].load_liquid(liquid=liquid_template1, volume=vol + 5)

    template2_vols = {}
    for w, vol in zip(sourcewells2, volume2):
        if w and vol > 0:
            template2_vols[w] = template2_vols.get(w, 0) + vol
    for c, vol in zip(scols2_fulltransfer, svol2_fulltransfer):
        for r in 'ABCDEFGH':
            w = r + c
            template2_vols[w] = template2_vols.get(w, 0) + vol
    for w, vol in template2_vols.items():
        sourcestrip.wells_by_name()[w].load_liquid(liquid=liquid_template2, volume=vol + 5)

    message1 = str(f"MM distribute. \nFor {rxns} reactions, please prepare {mastermix:.1f} ul mastermix and place it in D6 of Eppendorf tube rack.")
    comment(ctx, message1)
    
    # distribute MM (change tip once in between if > 48 samples)
    mm_dest_wells = [ destplate.wells_by_name()[v] for v in destwells_all_pcr ]
    if rxns > 48:
        midpoint = len(mm_dest_wells) // 2
        # First half
        pip_single.distribute(
            5, 
            sourcetube[mm_pos], 
            mm_dest_wells[:midpoint],
            blow_out = True, 
            blowout_location = "source well"
        )
        # Second half
        pip_single.distribute(
            5, 
            sourcetube[mm_pos], 
            mm_dest_wells[midpoint:],
            blow_out = True, 
            blowout_location = "source well"
        )
    else:
        pip_single.distribute(
            5, 
            sourcetube[mm_pos], 
            mm_dest_wells,
            blow_out = True, 
            blowout_location = "source well"
        )

    # DMSO distribute, use pip_single only, fixed position on C6
    dmsorxns = len(list(filter(lambda x: x > 0, dmso)))
    comment(ctx, str(f"DMSO distribute for {dmsorxns} reactions."))
    pip_single.flow_rate.aspirate = pip_single_original_flowrate/4
    pip_single.flow_rate.dispense = pip_single_original_flowrate/4

    if dmsorxns > 0:
        pip_single.distribute(
            1.5, 
            sourcetube[dmso_pos], 
            [ destplate[destwells1[i]] for i,v in enumerate(dmso) if v > 0 ], 
            touch_tip = True, 
            air_gap = 0,
            new_tip = 'always', 
        )
    
    pip_single.flow_rate.aspirate = pip_single_original_flowrate
    pip_single.flow_rate.dispense = pip_single_original_flowrate

    # full column transfers first
    # plate
    comment(ctx, str(f"Full column transfer for plate cols"))
    for i, v in enumerate(scols1_fulltransfer):
        pip_multi.transfer(
        svol1_fulltransfer[i], 
        sourceplate.wells_by_name()['A' + scols1_fulltransfer[i]], 
        destplate.wells_by_name()['A' + dcols1_fulltransfer[i]], 
        mix_after = (4, 5)
        )
    
    # strip
    comment(ctx, str(f"Full column transfer for strip cols"))
    for i, v in enumerate(scols2_fulltransfer):
        pip_multi.transfer(
        svol2_fulltransfer[i], 
        sourcestrip.wells_by_name()['A' + scols2_fulltransfer[i]], 
        destplate.wells_by_name()['A' + dcols2_fulltransfer[i]],
        mix_after = (4, 5)
        )
    
    # first take primer then air gap then sample, all in one mmove
    # process both source1 and source2!!
    def mytransfer_multistep(vol1, src_type1, src_well1, # plate
                             vol2, src_type2, src_well2, # strip
                             vol3, src_type3, src_well3, # primer
                             dest_type, dest_well, 
                             chtip = True):
        
        if vol1 <= 0 and vol2 <= 0 and vol3 <= 0: 
            return
        ctx.comment("--------------------------------------")
        if not pip_single.has_tip:
            pip_single.pick_up_tip()
        # dont try to get wells which are '', will error
        # primer
        if vol3 > 0:    
            pip_single.aspirate(vol3, src_type3.wells_by_name()[src_well3])
            pip_single.air_gap(1)
            if chtip:
                ctx.comment("Changing tip")
                pip_single.dispense(location = dest_type.wells_by_name()[dest_well])
                pip_single.drop_tip()
                #pip_single.pick_up_tip()
        
        # plate
        if vol1 > 0:
            if not pip_single.has_tip:
                pip_single.pick_up_tip()
            pip_single.aspirate(vol1, src_type1.wells_by_name()[src_well1])
        #strip
        if vol2 > 0:
            if not pip_single.has_tip:
                pip_single.pick_up_tip()
            pip_single.aspirate(vol2, src_type2.wells_by_name()[src_well2])
        if pip_single.current_volume > 0:
            pip_single.dispense(location = dest_type.wells_by_name()[dest_well])
            pip_single.mix(4, 5, dest_type.wells_by_name()[dest_well])
        
        if pip_single.has_tip:
            pip_single.drop_tip()

    # use it
    comment(ctx, str(f"Single rxns transfer"))
    for i, v in enumerate(destwells1): # could be any destwells
        mytransfer_multistep(
            volume1[i], sourceplate, sourcewells1[i], 
            volume2[i], sourcestrip, sourcewells2[i], 
            volume3[i], sourcetube, sourcewells3[i], 
            destplate, destwells1[i], 
            chtip = change_primer_tip
            )
    ctx.comment("--------------------------------------")
    
    comment(ctx, "Protocol finished!")

