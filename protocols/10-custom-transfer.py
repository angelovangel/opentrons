from opentrons import protocol_api

# this file serves as a template only, use shiny app to customize
# one source and one target labware
# as flexible as possible

metadata = {
	'protocolName': '10-custom-transfer.py',
	'author': 'BCL <angel.angelov@kaust.edu.sa>',
	'description': 'Custom transfer template',
	'apiLevel': '2.18'
}

# Variables replaced by the Shiny app

mypipette = 'p20_single_gen2'
mymount = 'left'
mytips = 'opentrons_96_filtertiprack_20ul'
source_type = 'biorad_96_wellplate_200ul_pcr'
dest_type = 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap'

pipetting_type = 'transfer' # can be transfer, distribute, consolidate
newtip = 'always'
mbefore = (0,0)
mafter = (0,0)
agap = 0
aspirate_factor = 2
dispense_factor = 1
# len volumes should be == longer list
# if distribute len source_wells <= len dest_wells
# if consolidate len source_wells >= len dest_wells
source_wells = ['A1','B1','C1','D1', 'B1', 'C2']
dest_wells =   ['A1','A1','C1','C1', 'C1', 'C1']
volumes = [3, 3, 1, 1, 0, 0]

# End of variables handled by the Shiny app

def run(ctx: protocol_api.ProtocolContext):
    ctx.comment('Starting custom transfer protocol: ' + pipetting_type + ' from ' + str(source_wells) + ' to ' + str(dest_wells))
    ctx.comment('----------------------------------------------------------------')
    # odtc = ctx.load_module(module_name='thermocyclerModuleV2') # just a placeholder
    tips = [ctx.load_labware(mytips, slot) for slot in ['1', '2', '3']]
    # tips_right = [ctx.load_labware(right_tips, slot) for slot in ['3']]
    pipette = ctx.load_instrument(mypipette, mount = mymount, tip_racks = tips)
    pipette.flow_rate.aspirate = pipette.flow_rate.aspirate / aspirate_factor
    pipette.flow_rate.dispense = pipette.flow_rate.dispense / dispense_factor

    ctx.comment('Loaded pipette: ' + mypipette + ' on ' + mymount + ' mount')
    ctx.comment('Aspirate rate : ' + str(pipette.flow_rate.aspirate) + ' ul/s')
    ctx.comment('Dispense rate : ' + str(pipette.flow_rate.dispense) + ' ul/s')
    ctx.comment('----------------------------------------------------------------')

    source = ctx.load_labware(source_type, '4', 'Source labware')
    dest = ctx.load_labware(dest_type, '5', 'Destination labware')
    if pipetting_type == 'transfer':
        pipette.transfer(
            [v for v in volumes if v > 0],
            [source[v] for i, v in enumerate(source_wells) if volumes[i] > 0],
            [dest[v] for i, v in enumerate(dest_wells) if volumes[i] > 0], 
            new_tip = newtip, 
            mix_before = mbefore,
            mix_after = mafter, 
            air_gap = agap
        )

    elif pipetting_type == 'distribute':
        distr_set = sorted(set(source_wells))
        for i, v in enumerate(distr_set):
            volumeslist = [m for l, m in enumerate(volumes) if m > 0 and source_wells[l] == v] # gives vol list for each distr_set
            if not volumeslist: continue # type error if empty list so skip this
            destlist = [dest[k] for j, k in enumerate(dest_wells) if volumes[j] > 0 and source_wells[j] == v]
            
            pipette.distribute(
                volumeslist,
                source[v],
                destlist,
                new_tip = newtip,
                mix_before = mbefore,
                air_gap = agap
            )

    elif pipetting_type == 'consolidate':
        cons_set = sorted(set(dest_wells))
        for i, v in enumerate(cons_set):
            volumeslist = [m for l, m in enumerate(volumes) if m > 0 and dest_wells[l] == v]
            if not volumeslist: continue # type error if empty list so skip this
            sourcelist = [source[k] for j, k in enumerate(source_wells) if volumes[j] > 0 and dest_wells[j] == v]
            
            pipette.consolidate(
                volumeslist,
                sourcelist,
                dest[v],
                new_tip = newtip,
                mix_after = mafter,
                air_gap = agap
            )
