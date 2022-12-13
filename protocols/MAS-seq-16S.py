# distribute MAS-Seq primers

from opentrons import protocol_api

metadata = {
    'protocolName': 'MAS-seq-16S.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Prepare primers for MAS-Seq-16S. First mix primer combinations and dilute to 10 uM, then dilute to 2.5 mM',
    'apiLevel': '2.8'
}

primers1=['A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4', 'A5', 'B5', 'C5'] # positions of first primers in rack
destcols1=[str(n) for n in list(range(2, 13))] # gives cols 2 to 12 as str

primers2=['A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4', 'A5', 'B5', 'C5']
destcols2=[str(n) for n in list(range(1,12))] # gives cols 1 to 11

barcodes_left=['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2']
barcodes_right=['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2']



def run(ctx: protocol_api.ProtocolContext): 
    ctx.comment('Starting primer transfer')

    source1 = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '7', 'Tube rack 1')
    source2 = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '9', 'Tube rack 2') # spaced like this to avoid contamination
    destplate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '11', 'Destination plate 25 uM')
    finalplate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '10', 'Destination plate 2.5 uM')
    water = ctx.load_labware('nest_12_reservoir_15ml', '8', 'Water reservoir')

    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['4']]
    tips20_multi = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['5', '6']]
    s20 = ctx.load_instrument('p20_single_gen2', mount = 'left', tip_racks=tips20_single)
    m20 = ctx.load_instrument('p20_multi_gen2', mount = 'right', tip_racks=tips20_multi)

    # put water in destplate, when primers are added it will be at 10 uM (10x diluted)
    m20.distribute(
        32, 
        water.wells_by_name()['A1'], 
        destplate.columns(), 
        )

    # first primer distribute
    for i,v in enumerate(primers1):
        s20.distribute(
            4, 
            source1.wells_by_name()[v], 
            destplate.columns_by_name()[destcols1[i]], 
        )
    
    # second primer distribute
    for i,v in enumerate(primers2):
        s20.distribute(
            4,
            source2.wells_by_name()[v],
            destplate.columns_by_name()[destcols2[i]], 
            #air_gap = 2
        )

    # transfer barcodes left
    s20.transfer(
        4,
        [source1.wells_by_name()[v] for v in barcodes_left],
        destplate.columns_by_name()['1'], 
        #air_gap = 1,
        new_tip = 'always'
    )

    # transfer barcodes right
    s20.transfer(
        4,
        [source2.wells_by_name()[v] for v in barcodes_right],
        destplate.columns_by_name()['12'],
        #air_gap = 1,
        new_tip = 'always'
    )
   
   # dilute to 2.5 uM in final plate, plate directly used in PCR
   # wait for confirmation
    ctx.pause("Please press continue to make final plate at 2.5 uM")

    m20.distribute(
        4.5, 
        water.wells_by_name()['A1'], 
        finalplate.columns()
    )

    m20.transfer(
        1.5, 
        destplate.columns(), 
        finalplate.columns(), 
        mix_before = (5, 10), 
        mix_after = (3,3), 
        new_tip = 'always'
    )


