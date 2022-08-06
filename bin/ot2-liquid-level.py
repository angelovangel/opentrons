# playground to implement pipetting with liquid level monitoring

from opentrons import protocol_api
import re

metadata = {
    'protocolName': 'Liquid level tracking',
    'author': '<angel.angelov@kaust.edu.sa>',
    'apiLevel': '2.8'
}

def run(ctx: protocol_api.ProtocolContext):
    #! dont use labels in load_labware, the default labels are used to decide tube_type in calculate_depth !!!
    epitubes = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5')
    falcontubes = ctx.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '4')
    #falcontubes = ctx.load_labware('opentrons_6_tuberack_falcon_50ml_conical', '4')
    
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['1']]
    s20 = ctx.load_instrument('p20_single_gen2', 'left', tip_racks=tips20_single)

    def mytransfer(vol, srctype, srcwell, desttype, destwell, z = 0):
        if z < 0:
            print('Negative z! Skipping this pipetting step')
            return

        s20.pick_up_tip()
        s20.aspirate(vol, srctype.wells_by_name()[srcwell].bottom(z))
        s20.dispense(vol, desttype.wells_by_name()[destwell].bottom(z + 1)) # default depth for dispense 
        s20.drop_tip()
    
    def init_volumes(labware, init_vol):
        if init_vol <= 0: return
        wells = dict(labware.wells_by_name())
        for i in wells:
            wells[i] = init_vol
        return wells

    def calculate_depth(location, vol):
        # calculate depth based on available volume in well
        # for epi, up to 500 ul it is frustum, from 500 to 1500 cylinder
        # tube_type can be pcr, epi, falcon15 and falcon50: only for these we calculate frustum for vols below certain cuttoff
        #frustum volume:
        # volume = (1/3) * π * depth * (r² + r * R + R²), where R is the big, and r the small radius
        # h = (3 * V) / (π * (r12 + r22 + (r1 * r2)))
        ########### measure exactly #########

        # get tube type from location
        print(str(location))
        if re.search('pcrstrip', str(location)):
            cutoff_vol = 50
            small_radius = 5
        elif re.search('Eppendorf 1.5 mL', str(location)):
            print('using 1.5 ml epi for liquid depth calculation')
            cutoff_vol = 500
            small_radius = 2
        elif re.search('Falcon 15 mL', str(location)):
            print('using 15 mL Falcon for liquid depth calculation')
            cutoff_vol = 1500
            small_radius = 2
        elif re.search('Falcon 50 mL', str(location)):
            print('using 50 mL Falcon for liquid depth calculation')
            cutoff_vol = 4000
            small_radius = 10
        else:
            print('can not determine tube type, will skip depth calculation')
            return
        ########### measure exactly #########

        well_radius = location.diameter/2
        
        
        if vol <= cutoff_vol:
            depth = (3*vol)/(3.14*(pow(small_radius, 2) + pow(well_radius, 2) + (small_radius*well_radius)))
            print(depth)
        else:
            depth1 = (vol-cutoff_vol)/(3.14*pow(well_radius, 2))
            depth2 = (3*cutoff_vol)/(3.14*(pow(small_radius, 2) + pow(well_radius, 2) + (small_radius*well_radius)))
            depth = depth1 + depth2
        return round(depth, 2)
    
    sourcewells=["A1", "A2", "A3"]
    destwells=["A1","A3", "B2"]
    volumes=[10.00, 6.00, 5.00]
    
    # initialise to track these
    epiwells = init_volumes(falcontubes, 15000)
    #epiwells_liquid_depth = calculate_depth(falcontubes['A1'], 100, 'falcon15')
        
    for i, v in enumerate(sourcewells):
        
        mytransfer(volumes[i], falcontubes, sourcewells[i], epitubes, destwells[i])
        epiwells[v] = epiwells[v] - volumes[i]
        liquid_depth = calculate_depth(falcontubes.wells_by_name()[v], epiwells[v])

        #print(f'{v} curr_volume: {epiwells[v]} total_depth: {falcontubes.wells_by_name()[v].depth} liquid depth: {liquid_depth}')
        
    print(epiwells)

        


