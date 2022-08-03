# this file serves as a template only, Run-this-first.py is used to change the wells and volumes
from opentrons import protocol_api

metadata = {
    'protocolName': 'Sanger sequencing setup',
    'author': 'BCL <xiang.zhao@kaust.edu.sa>, <angel.angelov@kaust.edu.sa>',
    'description': 'Transfer templates and primers to destination plate, add Sequencing master mix',
    'apiLevel': '2.8'
}
sourcewells1=["A1", "C1", "A2"] # fixed line, if this changes also Run-this-first.py has to be changed
destwells1=["A1","A10", "A12"]
volume1=[4.00, 6.00, 7.00]
sourcewells2=["A1","B1","B1"]
destwells2=["A1","A2","B12"]
volume2=[2.00,10.00,1.00]
sourcewells3=["A1","A3","A1"]
destwells3=["A1","A3","C2"] # these are primers, so no MM added here
volume3=[2.00,5.00,1.00]

# get number of rxns, to use in calculating MM
rxns = len(
    list(filter(lambda n: n > 0, volume1)) + 
    list(filter(lambda n: n > 0, volume2))
    #list(filter(lambda n: n > 0, volume3))
    )

# get non-emty dest columns, by using the index of the volumes
# these are used to decide where to distribute PCR mm
destwells1_ne_index = [index for index, value in enumerate(volume1) if value > 0]
destwells1_pcr = [destwells1[i] for i in destwells1_ne_index]

destwells2_ne_index = [index for index, value in enumerate(volume2) if value > 0]
destwells2_pcr = [destwells2[i] for i in destwells2_ne_index]

# get columns with at least one rxn, use this to transfer PCR mm for the whole column
# e.g. wet lab has to try to fill columns with reactions
destwells_all_pcr = destwells1_pcr + destwells2_pcr
destcolumns_num_pcr = list(set([int(col[1:]) for col in destwells_all_pcr])) # converting the list to a set gives unique elements
destcolumns_num_sorted_pcr = sorted(destcolumns_num_pcr)
destcolumns_pcr = ['A' + str(x) for x in destcolumns_num_sorted_pcr] # restore well names to use with p20_multi
# print(destcolumns)

# 5 ul per reaction, 40 ul per column needed (44 with overhead)
mastermix = len(destcolumns_pcr) * 44

def run(ctx: protocol_api.ProtocolContext):

    ctx.comment(
        "Starting setup of " + 
        str(rxns) +
         " reactions (in " + 
        str(len(destcolumns_pcr)) + 
        " destination plate columns).\nHave a coffee..."
        )

    p20_single_mount ='left'
    p20_multi_mount='right' 

    destplate = ctx.load_labware('pcrplate_96_wellplate_200ul', '5', 'Destination plate') # stack of 96 well base plate and PCR plate
    sourceplate= ctx.load_labware('pcrplate_96_wellplate_200ul', '4', 'Source plate') # stack of 96 well base plate and PCR plate
    sourcestrip= ctx.load_labware('pcrstrip_96_wellplate_200ul', '8', 'Source strip') # stack of 96 well base plate and strips
    sourcetube = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '7', 'Primers in tube rack')
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['10', '11']]
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['3']]
    mmstrip = ctx.load_labware('pcrstrip_96_wellplate_200ul', '2', label='Sequencing master mix in strip')

    s20 = ctx.load_instrument(
        'p20_single_gen2', mount=p20_single_mount, tip_racks=tips20_single)
    m20 = ctx.load_instrument(
        'p20_multi_gen2', mount=p20_multi_mount, tip_racks=tips20_multi)
    
    
    # def mytransfer(vol, src_type, src_well, dst_type, dst_well, air_gap = 0):
    #     for i in range(len(src_well)):
    #         volume = vol[i]
    #         if volume <= 0: continue

    #         s20.transfer(
    #             volume,
    #             src_type.wells_by_name()[src_well[i]],
    #             dst_type.wells_by_name()[dst_well[i]],
    #             new_tip = 'always', 
    #             air_gap = air_gap
    #     )
    
    # first take primer then air gap then sample, all in one mmove
    def mytransfer_multi(vol1, src_type1, src_well1, vol2, src_type2, src_well2, dest_type, dest_well):
        
        # only do something if there is template to be pipetted
        if vol2 <= 0: return
        s20.pick_up_tip()
        # dont try to get wells which are '', will error
        if vol1 > 0:    
            s20.aspirate(vol1, src_type1.wells_by_name()[src_well1])
            s20.air_gap(1)
        
        s20.aspirate(vol2, src_type2.wells_by_name()[src_well2])
        s20.dispense(location = dest_type.wells_by_name()[dest_well])
        s20.drop_tip()

    # use it e.g. first primer then template
    # for plate as source
    for i, v in enumerate(destwells1):
        mytransfer_multi(
            volume3[i], sourcetube, sourcewells3[i], 
            volume1[i], sourceplate, sourcewells1[i], 
            destplate, destwells1[i]
            )

    # for strips as source
    for i, v in enumerate(destwells2):
        mytransfer_multi(
            volume3[i], sourcetube, sourcewells3[i], 
            volume2[i], sourcestrip, sourcewells2[i], 
            destplate, destwells2[i]
            )

    # if len(sourcewells1)!=0: 
    #     mytransfer(volume1, sourceplate, sourcewells1, destplate, destwells1)

    # if len(sourcewells2)!=0:
    #     mytransfer(volume2, sourcestrip, sourcewells2, destplate, destwells2)

    # if len(sourcewells3)!=0:
    #     mytransfer(volume3, sourcetube, sourcewells3, destplate, destwells3, air_gap=1)

    # pause here, prompt adding reservoir with PCR master mix
    # try to attract attention too!
    ctx.set_rail_lights(False)
    ctx.set_rail_lights(True)
    message = str(f"{rxns} reactions were transferred.\nPlease prepare {mastermix} ul Sequencing mastermix, pipet {mastermix/8:.1f} ul in each tube of the strip (deck position 2, column 1) and resume.\nThe mastermix will be distributed to columns {destcolumns_pcr} in the destination plate.")
    ctx.pause(msg = message)

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
