# playground to implement pipetting with liquid level monitoring

from opentrons import protocol_api
import re

metadata = {
    'protocolName': 'Liquid level tracking',
    'author': '<angel.angelov@kaust.edu.sa>',
    'apiLevel': '2.8'
}

def run(ctx: protocol_api.ProtocolContext):
    # dont use labels in load_labware, the default labels are used to decide tube_type in calculate_depth !!!
    epitubes = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2')
    falcontubes = ctx.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '1')
    #falcontubes = ctx.load_labware('opentrons_6_tuberack_falcon_50ml_conical', '4')
    
    tips20_single = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in ['10']]
    s20 = ctx.load_instrument('p20_single_gen2', 'left', tip_racks=tips20_single)

    def mytransfer(vol, srctype, srcwell, desttype, destwell, z = 0):
        if z < 0:
            print('Negative z! Skipping this pipetting step')
            return

        s20.pick_up_tip()
        s20.aspirate(vol, srctype.wells_by_name()[srcwell].bottom(z))
        s20.dispense(vol, desttype.wells_by_name()[destwell].bottom(z + 1)) # default depth for dispense 
        s20.drop_tip()
    

    def calculate_depth(location, vol):
        # calculate depth based on available volume in well
        # for epi, up to 500 ul it is frustum, from 500 to 1500 cylinder
        # tube_type can be pcr, epi, falcon15 and falcon50: only for these we calculate frustum for vols below certain cuttoff
        #frustum volume:
        # volume = (1/3) * π * depth * (r² + r * R + R²), where R is the big, and r the small radius
        # h = (3 * V) / (π * (r12 + r22 + (r1 * r2)))
        ########### measure exactly #########

        # get tube type from location
        #print(str(location))
        if re.search('pcrstrip', str(location)):
            cutoff_vol = 100
            small_radius = 3/2
        elif re.search('Eppendorf 1.5 mL', str(location)):
            print('using 1.5 ml epi for liquid depth calculation')
            cutoff_vol = 500
            small_radius = 3.4/2
        elif re.search('Falcon 15 mL', str(location)):
            print('using 15 mL Falcon for liquid depth calculation')
            cutoff_vol = 1250
            small_radius = 4.4/2
        elif re.search('Falcon 50 mL', str(location)):
            print('using 50 mL Falcon for liquid depth calculation')
            cutoff_vol = 3850
            small_radius = 6.9/2
        else:
            print('can not determine tube type, will skip depth calculation')
            return
        ########### measure exactly #########

        well_radius = location.diameter/2
        #print(small_radius)
        #print(well_radius)

        
        if vol <= cutoff_vol:
            depth = (3*vol)/(3.14*(pow(small_radius, 2) + pow(well_radius, 2) + (small_radius*well_radius)))
            #print(depth)
        else:
            depth1 = (vol-cutoff_vol)/(3.14*pow(well_radius, 2))
            depth2 = (3*cutoff_vol)/(3.14*(pow(small_radius, 2) + pow(well_radius, 2) + (small_radius*well_radius)))
            depth = depth1 + depth2
            #print(depth1)
            #print(depth2)
        if depth < 0:
            depth = 0
        return round(depth, 2)

    
    def init_volumes(labware, init_vol):
        if init_vol < 0: return
        wells = dict(labware.wells_by_name())
        for i in wells:
            wells[i] = init_vol
        return wells
    
    sourcewells=["A1", "A1", "A1"]
    destwells=["A2","B2", "B2"]
    volumes=[15.00, 20.00, 15.00]
    
        
    # for i, v in enumerate(sourcewells):
        
    #     mytransfer(volumes[i], epitubes, sourcewells[i], epitubes, destwells[i])
    #     epiwells[v] = epiwells[v] - volumes[i]
    #     liquid_depth = calculate_depth(epitubes.wells_by_name()[v], epiwells[v])

    #     print(f'{v} curr_volume: {epiwells[v]} total_depth: {epitubes.wells_by_name()[v].depth} liquid depth: {liquid_depth}')
    
    # initialise to track these
    src_levels = init_volumes(epitubes, 500)
    dest_levels = init_volumes(falcontubes, 1250)
    

    s20.pick_up_tip()
    for w in ['D3', 'D4']:
        for i in range(10):
            src_depth = calculate_depth(epitubes[w], src_levels[w])
            dest_depth = calculate_depth(falcontubes['A1'], dest_levels['A1'])
            #mytransfer(20, epitubes, 'A1', epitubes, 'A2', z = liquid_depth-1)
            # safe lock
            if src_depth >= 0 and dest_depth >= 0:
                s20.aspirate(20, epitubes[w].bottom(src_depth))
                s20.dispense(20, falcontubes['A1'].bottom(dest_depth))

                # update levels
                src_levels[w] = src_levels[w] - 20
                dest_levels['A1'] = dest_levels['A1'] + 20
                print(src_depth)
                print(dest_depth)
    
    s20.drop_tip()

        


