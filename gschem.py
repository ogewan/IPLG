#!/usr/bin/env python
"""
Create a file .schematic
"""
import os,sys
import time
import random
from io import BytesIO
from struct import pack, unpack
import array, math
import glob
# local module
try:
    import nbt
except ImportError:
    # nbt not in search path. Let's see if it can be found in the parent folder
    extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
    if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
        raise
    sys.path.append(extrasearchpath)
from nbt.nbt import NBTFile, TAG_Short, TAG_Int, TAG_String, TAG_List, TAG_Byte, TAG_Byte_Array, TAG_Compound
from nbt.chunk import Chunk

"""'
process:
create seed source, generate book from sorce map block array
use seed to create .schematics with books
book is a base91 string representing a the 3D block array
The translation table is composed of the remaining characters as shown below.

0	A	0x41	 	13	N	0x4E	 	26	a	0x61	 	39	n	0x6E	 	52	0	0x30	 	65	%	0x25	 	78	>	0x3E
1	B	0x42	14	O	0x4F	27	b	0x62	40	o	0x6F	53	1	0x31	66	&	0x26	79	?	0x3F
2	C	0x43	15	P	0x50	28	c	0x63	41	p	0x70	54	2	0x32	67	(	0x28	80	@	0x40
3	D	0x44	16	Q	0x51	29	d	0x64	42	q	0x71	55	3	0x33	68	)	0x29	81	[	0x5B
4	E	0x45	17	R	0x52	30	e	0x65	43	r	0x72	56	4	0x34	69	*	0x2A	82	]	0x5D
5	F	0x46	18	S	0x53	31	f	0x66	44	s	0x73	57	5	0x35	70	+	0x2B	83	^	0x5E
6	G	0x47	19	T	0x54	32	g	0x67	45	t	0x74	58	6	0x36	71	,	0x2C	84	_	0x5F
7	H	0x48	20	U	0x55	33	h	0x68	46	u	0x75	59	7	0x37	72	.	0x2E	85	`	0x60
8	I	0x49	21	V	0x56	34	i	0x69	47	v	0x76	60	8	0x38	73	/	0x2F	86	{	0x7B
9	J	0x4A	22	W	0x57	35	j	0x6A	48	w	0x77	61	9	0x39	74	:	0x3A	87	|	0x7C
10	K	0x4B	23	X	0x58	36	k	0x6B	49	x	0x78	62	!	0x21	75	;	0x3B	88	}	0x7D
11	L	0x4C	24	Y	0x59	37	l	0x6C	50	y	0x79	63	#	0x23	76	<	0x3C	89	~	0x7E
12	M	0x4D	25	Z	0x5A	38	m	0x6D	51	z	0x7A	64	$	0x24	77	=	0x3D	90	"	0x22
"""
index = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',24:'Y',25:'Z',26:'a',27:'b',28:'c',29:'d',30:'e',31:'f',32:'g',33:'h',34:'i',35:'j',36:'k',37:'l',38:'m',39:'n',40:'o',41:'p',42:'q',43:'r',44:'s',45:'t',46:'u',47:'v',48:'w',49:'x',50:'y',51:'z',52:'0',53:'1',54:'2',55:'3',56:'4',57:'5',58:'6',59:'7',60:'8',61:'9',62:'!',63:'#',64:'$',65:'%',66:'&',67:'(',68:')',69:'*',70:'+',71:',',72:'.',73:'/',74:':',75:';',76:'<',77:'=',78:'>',79:'?',80:'@',81:'[',82:']',83:'^',84:'_',85:'`',86:'{',87:'|',88:'}',89:'~',90:'"'}
iindex = {y:x for x,y in index.items()} #inverse index

class foo():
    id = 10

"""
def convertbook(world_folder):
    world = McRegionWorldFolder(world_folder)  # map still only supports McRegion maps
    t = world.chunk_count()
    mapMAX = t*32768
    mapstr = '"'*mapMAX
    mape = list(mapstr)
    i = 0.0
    for chunk in world.iter_chunks():
        if i % 50 ==0:
            sys.stdout.write("creating book(Source)")
        elif i % 2 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
        elif i % 50 == 49:
            sys.stdout.write("%5.1f%%\n" % (100*i/t))
        i +=1
        cx,cz = chunk.get_coords()
        for z in range(16):
            for x in range(16):
                for y in range(128):
                    block_id = chunk.blocks.get_block(x,y,z)
                    if block_id > 89: block_id = 12 #turn block into sand if it is not first 91 blocks
                    #91st entry changed to null
                    mape[(cx*16 + x) + y*128 + (cz*16 + z)*128*16] = index[block_id]
                    
    print(" done\n")
    filename = os.path.basename(world_folder)+".source"
    mapstr = ''.join(mape)
    with open('books/'+filename, 'w') as fi:
        fi.write(mapstr)
    print("Saved book as %s" % filename)
    #return 0
    return filename,mapstr
"""
    
def genblst():
    return [0]*4194304,'A'4*419430

def _schema(h=256,l=128,w=128,blst=[0]*4194304):
    result = NBTFile() #Blank NBT
    result.name = "Schematic"
    result.tags.extend([
        TAG_Short(name="Height", value=h),
        TAG_Short(name="Length", value=l),
        TAG_Short(name="Width", value=w),
        TAG_Byte_Array("Biomes",gbba([0]*16384,True)),
        TAG_Byte_Array("Blocks", gbba(blst,True)),
        TAG_Byte_Array("Data",gbba([0]*4194304,True)),
        TAG_String(name="Materials", value="Alpha"),
        TAG_List(type=foo(),name="Entities"),
        TAG_List(type=foo(),name="TileEntities"),
        TAG_List(type=foo(),name="TileTicks")
    ])
    return result


def gbba(blocksList, buffer=False):
    """Return a list of all blocks in this chunk."""
    if buffer:
        length = len(blocksList)
        return BytesIO(pack(">i", length)+gbba(blocksList))
    else:
        return array.array('B', blocksList).tostring()

def main():
    gui = """
#########################################################
Intelligent Procedural Level Generation #1.00
using Minecraft
source: {}
commands: create source - 0, blank schematic - 1,
generate schematic - 2, random schematic - 3, exit - 4
random schematic LEGAL - 5
"""
    try:
        sourcename = glob.glob('books/*.source')[0]
        f = open(sourcename,'r')
        source = f.read()
        f.close()
    except:
        sourcename = ""
        source = ""
    while True:
        print(gui.format(sourcename))
        if source == "~":
            world_folder = input('<SEED REQUIRED>Select Source Schematic:')
            if world_folder == "":
                continue
            #sourcename,source = convertbook(world_folder)
            sourcename = "books/"+sourcename
            try:
                f = open(sourcename,'r')
                source = f.read()
                f.close()
            except:
                source = ""
            continue
        try:
            cmd = int(input('c: '))
        except:
            continue
        if cmd == 0:#create source book
            world_folder = input('Select Source Schematic:')
            if world_folder == "":
                continue
            #sourcename,source = convertbook(world_folder)
            sourcename = "books/"+sourcename
        elif cmd == 1:#blank schematic
            name = input('Schematic Name:')
            if name == "":
                continue
            mine = _schema()
            print(mine.pretty_tree())
            mine.write_file("schema/B"+name+".schematic")
        elif cmd == 2:#generate schematic
            name = input('Schematic Name:')
            if name == "":
                continue
            mpl,mps = genblst()
            with open('books/'+filename, 'w') as fi:
                fi.write(mps)
            mine = _schema(blst=mpl)
            print(mine.pretty_tree())
            mine.write_file("schema/"+name+".schematic")
        elif cmd == 3:#random schematic
            """for demonstration purposes,
no book can be made but can is a valid schematic
will crash game if loaded"""
            name = input('Schematic Name:')
            if name == "":
                continue
            mpl = [random.choice(range(197)) for _ in range(4194304)]
            #mps = ''.join(mpl)
            """with open('books/'+filename, 'w') as fi:
                fi.write(mps)"""
            print("book cannot be generated, possible values exceed 91")
            mine = _schema(blst=mpl)
            print(mine.pretty_tree())
            mine.write_file("schema/R"+name+".schematic")
        elif cmd == 4:#exit
            break
        elif cmd == 5:#random schematic LEGAL
            """for demonstration purposes,
book can be made and is a valid schematic, but it
is completely random, slows down game to a halt"""
            name = input('Schematic Name:')
            if name == "":
                continue
            mpl = [index[random.choice(range(91))] for _ in range(4194304)]
            mps = ''.join(mpl)
            with open('books/'+name, 'w') as fi:
                fi.write(mps)
            mine = _schema(blst=[iindex[_] for _ in mpl])
            print(mine.pretty_tree())
            mine.write_file("schema/R"+name+".schematic")
        else:
            print("Command {} is not found".format(cmd))
    return 0


if __name__ == '__main__':
    """schmatic = _schema()
    print(schmatic.pretty_tree())
    schmatic.write_file("artificial2.schematic")"""
    sys.exit(main())
