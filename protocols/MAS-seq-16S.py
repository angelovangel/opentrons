# distribute MAS-Seq primers

from opentrons import protocol_api

metadata = {
    'protocolName': 'MAS-seq-16S.py',
    'author': 'BCL <angel.angelov@kaust.edu.sa>',
    'description': 'Prepare primers for MAS-Seq-16S',
    'apiLevel': '2.8'
}

primers1=['A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4', 'A5', 'B5', 'C5'] # positions of first primers in rack
destcols1=[str(n) for n in list(range(2, 13))] # gives cols 2 to 12 as str

primers2=['A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4', 'A5', 'B5', 'C5']
destcols2=[str(n) for n in list(range(1,12))] # gives cols 1 to 11

barcodes_left=['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2']
barcodes_left_dest=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1']
barcodes_right=['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2']
barcodes_right_dest=['A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']

# sourcewells2=['A3', 'A3', 'A3', 'A3', 'A3', 'A3']
# destwells2=['A1', 'B1', 'C1', 'D1', 'E1', 'F1']
# vol=[3, 3, 3, 3, 3, 3]

def run(ctx: protocol_api.ProtocolContext): 
    ctx.comment('Starting primer transfer')

    source1 = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '7', 'Tube rack 1')
    source2 = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '9', 'Tube rack 2') # spaced like this to avoid contamination
    destplate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '11', 'Destination plate')

    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['2']]
    s20 = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=tips20_single)

    # 
    # first primer distribute
    for i,v in enumerate(primers1):
        s20.distribute(
            3, 
            source1.wells_by_name()[v], 
            destplate.columns_by_name()[destcols1[i]]
            #air_gap = 2,
        )
    
    # second primer distribute
    for i,v in enumerate(primers2):
        s20.distribute(
        3,
        source2.wells_by_name()[v],
        destplate.columns_by_name()[destcols2[i]]
        #air_gap = 2
        )

    # transfer barcodes left
    s20.transfer(
        3,
        [source1.wells_by_name()[v] for v in barcodes_left],
        [destplate.wells_by_name()[v] for v in barcodes_left_dest], 
        air_gap = 1,
        new_tip = 'always'
    )

    # transfer barcodes right
    s20.transfer(
        3,
        [source2.wells_by_name()[v] for v in barcodes_right],
        [destplate.wells_by_name()[v] for v in barcodes_right_dest], 
        air_gap = 1,
        new_tip = 'always'
    )
   


