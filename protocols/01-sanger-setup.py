# this file serves as a template only, replace-from-excel.py and the template excel file is used to change the wells and volumes
# from doctest import master
from opentrons import protocol_api
from collections import Counter

########################## metadata ##########################
metadata = {
    'protocolName': 'Sanger sequencing setup',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Transfer templates and primers to destination plate, add Sequencing master mix',
    'apiLevel': '2.8'
}

sourcewells1=['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
destwells1=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume1=[15, 15, 15, 15, 15, 15, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sourcewells2=[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'E2', 'B5', ' ', ' ', ' ', ' ', 'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
destwells2=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume2=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sourcewells3=[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', 'A1', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
destwells3=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']
volume3=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
destcolumns_num_sorted_pcr = sorted(list(set([int(col[1:]) for col in destwells_all_pcr]))) # converting the list to a set gives unique elements
destcolumns_pcr = ['A' + str(x) for x in destcolumns_num_sorted_pcr] # restore well names to use with p20_multi
# print(destcolumns)

# 5 ul per reaction, 40 ul per column needed (44 with overhead)
# mastermix = len(destcolumns_pcr) * 44

# determine volumes per row for the MM strip col 1 in position 2
rows_mm_vols = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}
rows_counts = Counter([row[:1] for row in destwells_all_pcr]) # count how many A, B ... to determine MM needed in each row
rows_mm_vols.update(rows_counts)
rows_mm_vols.update((x, y * 5.5) for x, y in rows_mm_vols.items()) # 5.5 ul per reaction
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

def run(ctx: protocol_api.ProtocolContext):

    ctx.comment(
        "Starting setup of " + 
        str(rxns) +
         " reactions in " + 
        str(len(destcolumns_pcr)) + 
        " destination plate columns.\nHave a coffee..."
        )

    # stack of 96 well base plate and PCR plate
    destplate = ctx.load_labware('pcrplate_96_wellplate_200ul', '5', 'Destination plate') # stack of 96 well base plate and PCR plate
    sourceplate = ctx.load_labware('pcrplate_96_wellplate_200ul', '4', 'Source plate') # stack of 96 well base plate and PCR plate
    sourcestrip = ctx.load_labware('pcrstrip_96_wellplate_200ul', '8', 'Source strip') # stack of 96 well base plate and strips
    mmstrip = ctx.load_labware('pcrstrip_96_wellplate_200ul', '2', 'Sequencing master mix in strip') # stack of 96 well base plate and strips
    sourcetube = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '7', 'Primers in tube rack')
    
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['10', '11']]
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3', '6']]
    

    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)
    m20 = ctx.load_instrument('p20_multi_gen2', mount='right', tip_racks=tips20_multi)
    
    # full column transfers first
    # plate
    for i, v in enumerate(scols1_fulltransfer):
        ctx.comment("--------------------------------------")
        ctx.comment("Full column transfer plate : " + str(svol1_fulltransfer[i]) + " ul from A" + v + " to A" + dcols1_fulltransfer[i])
        m20.transfer(
        svol1_fulltransfer[i], 
        sourceplate.wells_by_name()['A' + scols1_fulltransfer[i]], 
        destplate.wells_by_name()['A' + dcols1_fulltransfer[i]]
        )
    
    # strip
    for i, v in enumerate(scols2_fulltransfer):
        ctx.comment("Full column transfer strip : " + str(svol2_fulltransfer[i]) + " ul from A" + v + " to A" + dcols2_fulltransfer[i])
        m20.transfer(
        svol2_fulltransfer[i], 
        sourcestrip.wells_by_name()['A' + scols2_fulltransfer[i]], 
        destplate.wells_by_name()['A' + dcols2_fulltransfer[i]])
    
    # first take primer then air gap then sample, all in one mmove
    # process both source1 and source2!!
    def mytransfer_multistep(vol1, src_type1, src_well1, # plate
                             vol2, src_type2, src_well2, # strip
                             vol3, src_type3, src_well3, # primer
                             dest_type, dest_well):
        
        if vol1 <= 0 and vol2 <= 0 and vol3 <= 0: 
            return
        ctx.comment("--------------------------------------")
        s20.pick_up_tip()
        # dont try to get wells which are '', will error
        # primer
        if vol3 > 0:    
            s20.aspirate(vol3, src_type3.wells_by_name()[src_well3])
            s20.air_gap(1)
        # plate
        if vol1 > 0:
            s20.aspirate(vol1, src_type1.wells_by_name()[src_well1])
        #strip
        if vol2 > 0:
            s20.aspirate(vol2, src_type2.wells_by_name()[src_well2])

        s20.dispense(location = dest_type.wells_by_name()[dest_well])
        s20.drop_tip()

    # use it
    for i, v in enumerate(destwells1): # could be any destwells
        mytransfer_multistep(
            volume1[i], sourceplate, sourcewells1[i], 
            volume2[i], sourcestrip, sourcewells2[i], 
            volume3[i], sourcetube, sourcewells3[i], 
            destplate, destwells1[i]
            )
    ctx.comment("--------------------------------------")
    
	# pause here, prompt adding reservoir with PCR master mix
    # try to attract attention too!
    
    for _ in range(3):
        ctx.set_rail_lights(False)
        ctx.delay(1)
        ctx.set_rail_lights(True)
        ctx.delay(1)
    #message = str(f"{rxns} reactions were transferred.\nPlease prepare {mastermix} ul Sequencing mastermix, pipet {mastermix/8:.1f} ul in each tube of the strip (deck position 2, column 1) and resume.\nThe mastermix will be distributed to columns {destcolumns_pcr} in the destination plate.")
    message = str(f"{rxns} reactions were transferred.\nPlease prepare {mastermix:.1f} ul mastermix and place it in D6 of Eppendorf tube rack. The mastermix will be distributed first to the A1 strip in position 2, and then to columns {destcolumns_pcr} in the destination plate.")
    ctx.pause(msg = message)

    # distribute master mix to col 1 
    s20.distribute(
        list(rows_mm_vols.values()), 
        sourcetube.wells_by_name()['D6'], # fixed position, place MM in D6 of Epi tuberack
        mmstrip.columns()[0],
        new_tip = 'once', disposal_volume = 0, blow_out = False)
    ctx.comment("--------------------------------------")
    
    # transfer master mix
    m20.transfer(
        5,
        mmstrip.columns()[0], # only column 1 is used
        [destplate.wells_by_name()[well_name] for well_name in destcolumns_pcr], 
        new_tip = 'always', 
        mix_after = (3, 15), 
        blow_out = True, 
        blowout_location = 'destination well'
    )
