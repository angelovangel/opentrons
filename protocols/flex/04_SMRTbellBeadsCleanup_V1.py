def get_values(*names):
            import json
            _all_values = json.loads("""{"DRY_WATER_RUN":false,"cols":6,"sample_vol":100,"ethanol_vol":200,"elution_vol":47,"flow_rate_aspirate":100,"flow_rate_dispense":100,"flow_rate_blow_out":100,"incubation_time_1":10,"incubation_time_2":5,"protocol_filename":"SMRTbell Beads Cleanup_V1"}""")
            return [_all_values[n] for n in names]


import math
from opentrons import protocol_api
from opentrons import types
from opentrons.protocol_api import COLUMN, ALL
import numpy as np

metadata = {
    "author": "Opentrons",
    "source": "Custom Protocol Request",
    "description": "SMRTbell Beads Cleanup",
}

requirements = {"robotType": "OT-3", "apiLevel": "2.16"}

# ------------------------------------------------------------------ #
#                         Primary parameters                         #
# ------------------------------------------------------------------ #
# DRY_WATER_RUN = False
# cols = 6
# sample_vol = 100
# ethanol_vol = 200
# elution_vol = 47
# incubation_time_1 = 10
# incubation_time_2 = 5
# flow_rate_aspirate = 100
# flow_rate_dispense = 100
# flow_rate_blow_out = 100

[
    cols,
    DRY_WATER_RUN,
    sample_vol,
    ethanol_vol,
    elution_vol,
    incubation_time_1,
    incubation_time_2,
    flow_rate_aspirate,
    flow_rate_dispense,
    flow_rate_blow_out,
] = get_values(  # noqa: F821
    "cols",
    "DRY_WATER_RUN",
    "sample_vol",
    "ethanol_vol",
    "elution_vol",
    "incubation_time_1",
    "incubation_time_2",
    "flow_rate_aspirate",
    "flow_rate_dispense",
    "flow_rate_blow_out",
)

# ------------------------------------------------------------------ #
#                         Secondary Variables                        #
# ------------------------------------------------------------------ #
if DRY_WATER_RUN:
    cols = 1
beads_vol = sample_vol
mix_reps = 1 if DRY_WATER_RUN else 5
# ! ------------------------------------------------------------------ #
# !                         DO NOT TOUCH BELOW                         #
# ! ------------------------------------------------------------------ #

# ------------------------- Error handling ------------------------- #
# 1
if not (1 <= cols <= 6):
    raise Exception("Number of samples must be between 1 and 6")
# 2
# all volume parameters must be between 5 to 1000
volume_params = [beads_vol, ethanol_vol, elution_vol]
if any([i < 5 or i > 1000 for i in volume_params]):
    raise Exception("All volume parameters must be between 5 to 1000")
# 3
# sample_cols must be an integer
if not isinstance(cols, int):
    raise Exception("Number of samples must be an integer")
# 4
# all flow rate parameters must be between 5 to 716
flow_rates = [flow_rate_aspirate, flow_rate_dispense, flow_rate_blow_out]
if any([i < 5 or i > 716 for i in flow_rates]):
    raise Exception("All flow rate parameters must be between 5 to 716 ul/s")

# ------------------------------------------------------------------ #
#                           main structure                           #
# ------------------------------------------------------------------ #


def run(ctx: protocol_api.ProtocolContext):

    # -------------------------- load modules -------------------------- #
    mag = ctx.load_module("magneticBlockV1", location="C2")

    # -------------------------- load labware -------------------------- #
    sample_plate = ctx.load_labware("nest_96_wellplate_2ml_deep", "D2", "sample plate")
    final_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", "A1", "final plate")
    res1 = ctx.load_labware("axygen_1_reservoir_90ml", "C1", "ethanol reservoir")
    res2 = ctx.load_labware("nest_12_reservoir_15ml", "D1", "reagent reservoir")
    default_trash = ctx.load_trash_bin(location="A3")

    # ---------------------------- tips--------------------------- #
    if beads_vol <= 50:
        cols_50 = cols * 3
        cols_1000 = cols * 4 + 2
    else:
        cols_50 = cols * 2
        cols_1000 = cols * 5 + 2
    slots_50_count = math.ceil(cols_50 / 12)
    slots_1000_count = math.ceil(cols_1000 / 12)

    slots = ["A2", "B3", "C3", "D3", "B1"]
    if slots_50_count + slots_1000_count <= len(slots):
        tips50 = [
            ctx.load_labware(
                "opentrons_flex_96_filtertiprack_50ul", slot, "tiprack 50ul"
            )
            for slot in slots[:slots_50_count]
        ]
        tips1000 = [
            ctx.load_labware(
                "opentrons_flex_96_filtertiprack_1000ul", slot, "tiprack 1000ul"
            )
            for slot in slots[slots_50_count : slots_50_count + slots_1000_count]
        ]
    else:
        raise Exception("Not enough slots for tip racks")

    # --------------------- load 96-channel pipette -------------------- #
    pip = ctx.load_instrument("flex_96channel_1000", "left")

    # ----------------------- setup the flow rate ---------------------- #
    pip.flow_rate.aspirate = flow_rate_aspirate
    pip.flow_rate.dispense = flow_rate_dispense
    pip.flow_rate.blow_out = flow_rate_blow_out

    # -------------------------- reagent setup ------------------------- #
    ethanol = res1.wells()[0]
    beads = res2.wells()[0]
    elution = res2.wells()[1]
    waste_wells = res2.wells()[-cols:]

    # -------------------------- plate mapping ------------------------- #
    sample_cols = sample_plate.rows()[0][:cols]
    final_cols = final_plate.rows()[0][:cols]

    # -------------------------- Define liquids -------------------------- #
    colors = [
        "#00FF00",
        "#0000FF",
        "#FFFF00",
        "#0000FF",
        "#00FF00",
        "#FF0000",
        "#800080",
        "#800080",
        "#ADD8E6",
        "#F6ED0E",
        "#F6ED0E",
        "#7FFFD4",
        "#FFFF00",
        "#FF00FF",
        "#7FFFD4",
        "#FFC0CB",
        "#FFA500",
        "#FFEE58",
        "#C0C0C0",
    ]

    locations = [ethanol, beads, elution]
    vols = [
        ethanol_vol * cols * 8 * 2 * 1.25,
        beads_vol * cols * 8 * 1.25,
        elution_vol * cols * 8 * 1.25,
    ]

    liquids = ["ethanol", "beads", "elution"]
    # ---------------- load liquids in each single well ---------------- #
    for liquid, loc, color, v in zip(liquids, locations, colors, vols):
        liq = ctx.define_liquid(
            name=str(liquid), description=str(liquid), display_color=color
        )
        loc.load_liquid(liquid=liq, volume=v)

    # ------------------------------------------------------------------ #
    #                        help function (basic)                       #
    # ------------------------------------------------------------------ #
    # ------------------------------ pause ----------------------------- #
    pause_time = 1

    def pause_attention(msg):
        """pause the robot, flashes the light, and display a message"""
        nonlocal pause_time
        ctx.set_rail_lights(False)
        ctx.delay(seconds=0.25)
        ctx.set_rail_lights(True)
        ctx.delay(seconds=0.25)
        ctx.set_rail_lights(False)
        ctx.delay(seconds=0.25)
        ctx.set_rail_lights(True)
        ctx.delay(seconds=0.25)
        ctx.set_rail_lights(False)
        ctx.delay(seconds=0.25)
        ctx.set_rail_lights(True)
        ctx.comment(f"PAUSE X{pause_time}")
        ctx.pause(msg)
        pause_time += 1

    # -------------------------- tip handling -------------------------- #
    tip_count_1000, tip_count_50 = 0, 0
    tiporder_1000 = [t1 for _ in range(len(tips1000)) for t1 in tips1000[_].rows()[0]]
    tiporder_50 = [t2 for _ in range(len(tips50)) for t2 in tips50[_].rows()[0]]

    def rack_selection(vol):
        if vol <= 50:
            return tips50
        else:
            return tips1000

    def pick_up(pipette, p_volume):
        nonlocal tip_count_1000, tip_count_50
        if 50 < p_volume < 1000:
            if tip_count_1000 == len(tiporder_1000):
                pause_attention(" Replace empty 1000ul filter tips")
                tip_count_1000 = 0
            pipette.pick_up_tip(tiporder_1000[tip_count_1000])
            tip_count_1000 += 1
        elif 5 <= p_volume <= 50:
            if tip_count_50 == len(tiporder_50):
                pause_attention("Replace empty 200ul filter tips")
                tip_count_50 = 0
            pipette.pick_up_tip(tiporder_50[tip_count_50])
            tip_count_50 += 1
        else:
            raise ValueError("A wrong volume is used")

    def slow_tip_withdrawal(pipette, well, to_center=False):
        factor_slow = 40
        pipette.default_speed /= factor_slow
        if to_center is False:
            pipette.move_to(well.top(-3))
        else:
            pipette.move_to(well.center())
        pipette.default_speed *= factor_slow

    # ------------------------- liquid handling ------------------------ #
    def custom_mix(
        pipette, mvol, mix_loc, mix_rep, blowout=False, low=False, high=False
    ):
        if low:
            asp = mix_loc.bottom(low)
        else:
            asp = mix_loc.bottom(1.5)
        if high:
            disp = mix_loc.bottom(high)
        else:
            disp = mix_loc.bottom(3.5)
        # define mixing volume, and use the 2nd smallest value
        a = pipette.min_volume * 2
        b = 0.5 * tips50[0].wells()[0].max_volume
        d = 0.5 * tips1000[0].wells()[0].max_volume
        c = round((0.8 * mvol), 1)
        numbers = [a, b, c, d]
        vol = sorted(numbers)[2]

        ctx.comment(f"---Mixing volume: {vol} out of {mvol} ul")
        for _ in range(mix_rep):
            pipette.aspirate(vol, asp)
            pipette.dispense(vol, disp, push_out=0)
        if blowout:
            slow_tip_withdrawal(pipette, mix_loc, to_center=False)
            pipette.blow_out(mix_loc.top(-4))
            pipette.touch_tip(radius=0.75, v_offset=-4, speed=10)

    # ------------------------------------------------------------------ #
    #                         advanced functions                         #
    # ------------------------------------------------------------------ #

    def incubation_airdry(name, time):
        if DRY_WATER_RUN:
            for j in np.arange(time, 0, -time):
                msg = (
                    "There are "
                    + str(j)
                    + " seconds left in the "
                    + str(name)
                    + " step"
                )  # noqa
                ctx.delay(seconds=time, msg=msg)
        else:
            for j in np.arange(time, 0, -0.5):
                msg = (
                    "There are "
                    + str(j)
                    + " minutes left in the "
                    + str(name)
                    + " step"
                )  # noqa
                ctx.delay(minutes=0.5, msg=msg)

    def plate_to_plate(vol1, vol2, source_list, dest_list, premix=False, postmix=False):
        """
        Transfer liquid from source wells to destination wells on a plate.

        Args:
            vol1 (float): Volume to aspirate from source wells.
            vol2 (float): Volume already present in destination wells.
            source_list (list): List of source wells.
            dest_list (list): List of destination wells.
            premix (bool, optional): If True, perform premixing before aspiration. Defaults to False.
            postmix (bool, optional): If True, perform postmixing after dispensing. Defaults to False.

        """
        # vol1: volume to aspirate
        # vol2: volume already in the destination well
        for i, (s, d) in enumerate(zip(source_list, dest_list)):
            rack = rack_selection(vol1)
            pip.configure_nozzle_layout(style=COLUMN, start="A12", tip_racks=rack)
            ctx.comment(f"---Column X{i+1}")
            ctx.comment(f"---Source: {str(s)}")
            ctx.comment(f"---Destination: {str(d)}")
            pick_up(pip, vol1)
            if premix:
                custom_mix(pip, vol1, s, mix_reps, blowout=False)
            pip.aspirate(vol1, s.bottom(2))
            ctx.delay(seconds=2)
            slow_tip_withdrawal(pip, s, to_center=False)
            pip.dispense(vol1, d.bottom(2), push_out=0)
            ctx.delay(seconds=2)
            if postmix:
                postmix_vol = min(rack[0].wells()[0].max_volume, vol1 + vol2)
                custom_mix(
                    pip,
                    postmix_vol,
                    d,
                    mix_reps,
                    blowout=True,
                    low=2,
                    high=3,
                )
            pip.drop_tip(default_trash)
            ctx.comment("\n")

    def remove(removal_vol, dest_list, mode="super_ethanol"):
        """
        Remove liquid from source wells and dispense it into destination wells.

        Args:
            removal_vol (float): Volume to remove from source wells.
            dest_list (list): List of destination wells.
            mode (str, optional): Removal mode. Options are "super_ethanol" or "elution".
                Defaults to "super_ethanol".

        Raises:
            ValueError: If removal volume is outside the valid range.

        """
        rack = rack_selection(removal_vol)
        pip.configure_nozzle_layout(style=COLUMN, start="A12", tip_racks=rack)
        if removal_vol < 5 or removal_vol > 1000:
            raise ValueError("A wrong volume is used")
        extra_vol = 50
        if removal_vol + extra_vol * 2 > rack[0].wells()[0].max_volume:
            extra_vol = (rack[0].wells()[0].max_volume - removal_vol) / 2
        disp_vol = removal_vol + extra_vol * 2
        for i, (s, d) in enumerate(zip(sample_cols, dest_list)):
            if mode == "elution":
                re_rate = 0.2
                loc = d.bottom(2)
            elif mode == "super_ethanol":
                re_rate = 0.4
                loc = d.top(-5)
            else:
                raise ValueError("A wrong mode is used")
            ctx.comment(f"---Removal mode: {mode}-------------")
            ctx.comment(f"---Removing Column X{i+1}")
            ctx.comment(f"---Source: {str(s)}")
            ctx.comment(f"---Destination: {str(d)}")
            pick_up(pip, removal_vol)
            pip.aspirate(
                removal_vol,
                s.bottom().move(types.Point(x=0, y=0, z=0.7)),
                rate=0.1,
            )
            pip.aspirate(
                2 * extra_vol,
                s.bottom().move(types.Point(x=0, y=0, z=0.5)),
                rate=0.05,
            )
            slow_tip_withdrawal(pip, s, to_center=False)
            pip.dispense(disp_vol, loc, rate=re_rate, push_out=0)
            ctx.delay(seconds=3)
            if mode == "elution":
                slow_tip_withdrawal(pip, d, to_center=False)
                pip.blow_out(d.top(-0.5 * (d.depth)))
                pip.touch_tip(radius=0.75, v_offset=-5, speed=5)
            if mode == "super_ethanol":
                pip.blow_out(loc)
                pip.air_gap(extra_vol)
            pip.drop_tip(default_trash)
            ctx.comment("\n")

    # ------------------------------------------------------------------ #
    #                        Protocol starts here                        #
    # ------------------------------------------------------------------ #
    # pause before the protocol starts
    pause_attention(
        msg=f"Set up for Beads cleanup workflow:\
            The last chance to double check everything is loaded correctly\
            Click CONFIRM AND RESUME to start the protocol"
    )
    ctx.comment("\n~~~Step 3.1- 3.3: Add beads to the samples~~~")
    plate_to_plate(beads_vol, sample_vol, [beads] * cols, sample_cols, True, True)

    ctx.comment("\n~~~Step 3.4: 10 minutes incubation~~~\n")
    incubation_airdry("beads incubation", incubation_time_1)

    ctx.comment("\n~~~Step 3.5 - 3.6: plate to the mag and remove supernatant~~~")
    ctx.move_labware(sample_plate, mag, use_gripper=True)
    incubation_airdry("beads binding", incubation_time_2)
    remove(sample_vol, waste_wells, mode="super_ethanol")

    ctx.comment("\n~~~Step 3.7-3.9: Ethanol wash x2~~~")
    for i in range(2):
        ctx.comment(f"---Ethanol Wash X{i+1}")
        pick_up(pip, ethanol_vol)
        for j, d in enumerate(sample_cols):
            pip.aspirate(ethanol_vol, ethanol.bottom(2))
            ctx.delay(seconds=2)
            pip.dispense(ethanol_vol, d.top(-3), push_out=0)
            ctx.delay(seconds=2)
            pip.blow_out(d.top(-3))
        pip.drop_tip(default_trash)
        incubation_airdry("ethanol wash waiting", time=0.5)
        ctx.comment(f"---removal {i+1}")
        remove(2 * ethanol_vol, waste_wells, mode="super_ethanol")

    ctx.comment("\n~~~Step 3.10: plate to D2 and then add Elution buffer~~~")
    ctx.move_labware(sample_plate, "D2", use_gripper=True)
    plate_to_plate(elution_vol, 0, [elution] * cols, sample_cols, False, True)

    ctx.comment("\n~~~Step 3.11-12: 5 minutes incubation~~~")
    incubation_airdry("elution incubation", incubation_time_2)

    ctx.comment("\n~~~Step 3.13: plate to the mag and transfer the elution~~~")
    ctx.move_labware(sample_plate, mag, use_gripper=True)
    remove(elution_vol, final_cols, mode="elution")

    # change the nozzle layout to ALL
    pip.configure_nozzle_layout(style=ALL)

    # ctx.comment(f"1000ul tip count: {tip_count_1000}")
    # ctx.comment(f"50ul tip count: {tip_count_50}")

    # pause after the protocol is complete
    pause_attention("The protocol is now complete")
