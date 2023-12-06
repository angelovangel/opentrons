from opentrons import protocol_api

# this file serves as a template only, use shiny app to customize
# one source and one target labware
# as flexible as possible

metadata = {
	'protocolName': '10-custom-transfer.py',
	'author': 'BCL <angel.angelov@kaust.edu.sa>',
	'description': 'Custom transfer template',
	'apiLevel': '2.15'
}

# Variables replaced by the Shiny app

left_mount = 'p20_single_gen2'
left_tips = 'opentrons_96_filtertiprack_20ul'
right_mount = 'p20_multi_gen2'
right_tips = 'opentrons_96_filtertiprack_20ul'
source_type = 'biorad_96_wellplate_200ul_pcr'
dest_type = 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap'

pipetting_type = 'consolidate' # can be transfer, distribute, consolidate

source_wells = ['A1', 'C1']
dest_wells = ['A1', 'B1']
volumes = [1, 10]

# End of variables handled by the Shiny app

def run(ctx: protocol_api.ProtocolContext):
    ctx.comment('Starting custom transfer protocol: ' + pipetting_type + ' from ' + str(source_wells) + ' to ' + str(dest_wells))
    ctx.comment('----------------------------------------------------------------')
    odtc = ctx.load_module(module_name='thermocyclerModuleV2') # just a placeholder
    tips_left = [ctx.load_labware(left_tips, slot) for slot in ['1', '2']]
    tips_right = [ctx.load_labware(right_tips, slot) for slot in ['3']]
    left_pipette = ctx.load_instrument(left_mount, mount = 'left', tip_racks= tips_left)
    right_pipette = ctx.load_instrument(right_mount, mount = 'right', tip_racks = tips_right)

    source = ctx.load_labware(source_type, '4', 'Source')
    dest = ctx.load_labware(dest_type, '5', 'Destination')
    if pipetting_type == 'transfer':
        left_pipette.transfer(
            volumes,
            [ source[v] for i, v in enumerate(source_wells) ],
            [ dest[v] for i, v in enumerate(dest_wells) ]
        )
    elif pipetting_type == 'distribute':
        for i, v in enumerate(source_wells):
            left_pipette.distribute(
                volumes,
                source[v],
                [dest[v] for i, v in enumerate(dest_wells)],
        )
    elif pipetting_type == 'consolidate':
        for i, v in enumerate(dest_wells):
            left_pipette.consolidate(
                volumes,
                [source[v] for i, v in enumerate(source_wells)],
                dest[v]
            )
