from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL


metadata = {
    "protocolName": "Custom transfer Flex",
    "description": """Custom transfer, column or full head loading""",
    "author": "angel.angelov@kaust.edu.sa"
    }

requirements = {"robotType": "Flex", "apiLevel": "2.21"}
    
# Variables replaced by the Shiny app

mypipette = 'flex_96channel_1000'
mypipconfig = 'partial'

mytips = 'opentrons_flex_96_filtertiprack_200ul'
source_type = 'nest_12_reservoir_15ml'
dest_type = 'biorad_96_wellplate_200ul_pcr'

pipetting_type = 'distribute' # can be transfer, distribute, consolidate
newtip = 'always'
mbefore = (0,0)
mafter = (0,0)
agap = 0
aspirate_factor = 2
dispense_factor = 1
# len volumes should be == longer list
# if distribute len source_wells <= len dest_wells
# if consolidate len source_wells >= len dest_wells
source_wells = ['A1', 'A1']
dest_wells =   ['A1', 'B1']
volumes = [55, 45]

# End of variables handled by the Shiny app

def comment(myctx, message):
    myctx.comment("-----------")
    myctx.comment(message)
    myctx.comment("-----------")

def run(ctx: protocol_api.ProtocolContext):
    
    # tips and pipette
    partial_tips = ctx.load_labware(load_name=mytips, location='B3')
    full_tips = ctx.load_labware(load_name=mytips, location='A3', adapter="opentrons_flex_96_tiprack_adapter")
    pip = ctx.load_instrument(mypipette)
    pip.flow_rate.aspirate = pip.flow_rate.aspirate / aspirate_factor
    pip.flow_rate.dispense = pip.flow_rate.dispense / dispense_factor

    
    #labware
    source = ctx.load_labware(source_type, "B1")
    dest = ctx.load_labware(dest_type, "D1")
    trash = ctx.load_waste_chute()

    # helper functions
    def pip_config(type):
        if type == 'partial':
            pip.configure_nozzle_layout(
                style=COLUMN,
                start="A12",
                tip_racks=[partial_tips]
            )
        elif type == 'full':
            pip.configure_nozzle_layout(
                style = ALL, 
                tip_racks=[full_tips]
            )
    
    # 
    ########################################################################
    pip_config(mypipconfig)
    ########################################################################
    if pipetting_type == 'transfer':
        pip.transfer(
            [v for v in volumes if v > 0],
            [source[v] for i, v in enumerate(source_wells) if volumes[i] > 0],
            [dest[v] for i, v in enumerate(dest_wells) if volumes[i] > 0], 
            new_tip = newtip, 
            mix_before = mbefore,
            mix_after = mafter, 
            air_gap = agap
        )

    elif pipetting_type == 'distribute':
        if mypipconfig == 'full':
            exit("Not possible to distribute with full head configuration")
        
        distr_set = sorted(set(source_wells))
        for i, v in enumerate(distr_set):
            volumeslist = [m for l, m in enumerate(volumes) if m > 0 and source_wells[l] == v]
            if not volumeslist: continue # type error if empty list so skip this
            destlist = [dest[k] for j, k in enumerate(dest_wells) if volumes[j] > 0 and source_wells[j] == v]

            pip.distribute(
                volumeslist,
                source[v],
                destlist,
                new_tip = newtip,
                mix_before = mbefore,
                air_gap = agap
            )
    elif pipetting_type == 'consolidate':
        if mypipconfig == 'full':
            exit("Not possible to distribute with full head configuration")
        
        cons_set = sorted(set(dest_wells))
        for i, v in enumerate(cons_set):
            volumeslist = [m for l, m in enumerate(volumes) if m > 0 and dest_wells[l] == v]
            if not volumeslist: continue # type error if empty list so skip this
            sourcelist = [source[k] for j, k in enumerate(source_wells) if volumes[j] > 0 and dest_wells[j] == v]
            
            pip.consolidate(
                volumeslist,
                sourcelist,
                dest[v],
                new_tip = newtip,
                mix_after = mafter,
                air_gap = agap
            )
    

    