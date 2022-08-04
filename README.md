# opentrons

This repository contains protocols and helper scripts for working with Opentrons lab robots

## Overview
Explanation of the folders:
 - `bin` - contains helper scripts, check their help for details
 - `labware` - custom labware definitions used in the protocols
 - `protocols` - python scripts for running on the OT2 robot. Not all are actually tested on the machine.

## Protocols
Each protocol file is accompanied by a short description in a markdown file with the same name. The numbering in the files has no meaning, it is for convenience only.
The pipetting section contains lists of well positions and volumes to be used in the protocol. This section can be easily modified with data from Excel using the `bin/replace-from-excel.py`.

**Protocols**:
 - [Sanger setup BCL](protocols/Sanger-setup-BCL.md)

