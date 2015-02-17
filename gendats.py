#!/usr/bin/env python
"""
Create a file that can be used as a basic level.dat file with all required fields
"""
# http://www.minecraftwiki.net/wiki/Alpha_Level_Format#level.dat_Format

import os,sys
import time
import random
from io import BytesIO
from struct import pack, unpack
import array, math
# local module
try:
    import nbt
except ImportError:
    # nbt not in search path. Let's see if it can be found in the parent folder
    extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
    if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
        raise
    sys.path.append(extrasearchpath)
from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_Compound, TAG_Byte, TAG_Byte_Array
from nbt.chunk import Chunk

def generate_level():
    level = NBTFile() # Blank NBT
    level.name = "Data"
    level.tags.extend([
        TAG_Long(name="Time", value=1),
        TAG_Long(name="LastPlayed", value=int(time.time())),
        TAG_Int(name="SpawnX", value=0),
        TAG_Int(name="SpawnY", value=2),
        TAG_Int(name="SpawnZ", value=0),
        TAG_Long(name="SizeOnDisk", value=0),
        TAG_Long(name="RandomSeed", value=random.randrange(1,9999999999)),
        #TAG_Int(name="version", value=19132),
        #TAG_String(name="LevelName", value="Testing")
    ])

    player = TAG_Compound()
    player.name = "Player"
    player.tags.extend([
        TAG_Int(name="Score", value=0),
        TAG_Int(name="Dimension", value=0)
    ])
    inventory = TAG_Compound()
    inventory.name = "Inventory"
    player.tags.append(inventory)
    level.tags.append(player)

    return level

def generate_chunk(x=0,z=0,blst=[0]*32768):
    chunk = NBTFile() # Blank NBT
    chunk.name = "Level"
    chunk.tags.extend([
        TAG_Int(name="xPos", value=x),
        TAG_Int(name="zPos", value=z),
        TAG_Byte(name="TerrainPopulated", value=1),
        TAG_Long(name="LastUpdate", value=0),
        TAG_Byte_Array("Blocks", gbba(blst,True)),
        TAG_Byte_Array("Data",gbba([0]*16384,True)),
        TAG_Byte_Array("BlockLight",gbba([0]*16384,True)),
        TAG_Byte_Array("SkyLight",gbba([0]*16384,True)),
        TAG_Byte_Array("HeightMap",gbba([0]*256,True)),
    ])
    return chunk


def gbba(blocksList, buffer=False):
    """Return a list of all blocks in this chunk."""
    if buffer:
        length = len(blocksList)
        return BytesIO(pack(">i", length)+gbba(blocksList))
    else:
        return array.array('B', blocksList).tostring()

if __name__ == '__main__':
    level = generate_level()
    chunk = generate_chunk()
    print(level.pretty_tree())
    #level.write_file("level.dat")
    print(chunk.pretty_tree())
