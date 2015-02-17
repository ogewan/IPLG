#!/usr/bin/env python
"""
creates minecraft map
"""
import locale, os, sys, random
import json
import re, math#, binascii
from struct import pack, unpack
import glob
import mape
import gendats
# local module
try:
    import nbt
except ImportError:
    # nbt not in search path. Let's see if it can be found in the parent folder
    extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
    if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
        raise
    sys.path.append(extrasearchpath)
from nbt.region import RegionFile
from nbt.chunk import Chunk
from nbt.world import WorldFolder,McRegionWorldFolder
# PIL module (not build-in)
try:
    from PIL import Image
except ImportError:
    # PIL not in search path. Let's see if it can be found in the parent folder
    sys.stderr.write("Module PIL/Image not found. Pillow (a PIL fork) can be found at http://python-imaging.github.io/\n")
    # Note: it may also be possible that PIL is installed, but JPEG support is disabled or broken
    sys.exit(70) # EX_SOFTWARE

"""'
process:
create a seed
	convert real minecraft save to book
	use minecraft book as a seed, will be large but more data is good
validate seed
	convert book to minecraft save
	create empty nbt and populate with info from book
	create map of original and fake
	compare the two
use seed to make child
	texture quilting + genetic algorithm
use seed to make map
use seed to make minecraft save

minecraft save -> string (book)
minecraft save -> image (map)
book -> minecraft save
book -> image

region file = 32*32 (x,z) chunks = 1024 chunks = 67108864 blocks/bytes = 32  mB MAX
chunk = 16*128*16 (x,y,z) blocks = 32768 blocks/bytes = 0.03 mB MAX
block = 1 byte
target:
map = 128*128*128  (x,y,z) = 4194304 blocks/bytes = 64 chunks = 8*8 (x,z) chunks = 2 mB
map can be done in one region file.

Alpha: infdev - MCBETA 1.2
****McRegion: MCBETA 1.3 - MC 1.1****
Anvil: MC 1.2 - 

profile: iplg
version: release 1.1

Proof of concept
map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
map is a base91 string representing a map
x = y = z = w = d = 2
print(map[3 + y*w + z*w*d])
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
index = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',24:'Y',25:'Z',26:'a',27:'b',28:'c',29:'d',30:'e',31:'f',32:'g',33:'h',34:'i',35:'j',36:'k',37:'l',38:'m',39:'n',40:'o',41:'p',42:'q',43:'r',44:'s',45:'t',46:'u',47:'v',48:'w',49:'x',50:'y',51:'z',52:'0',53:'1',54:'2',55:'3',56:'4',57:'5',58:'6',59:'7',60:'8',61:'9',62:'!',63:'#',64:'$',65:'%',66:'&',67:'(',68:')',69:'*',70:'+',71:',',72:'.',73:'/',74:':',75:';',76:'<',77:'=',78:'>',79:'?',80:'@',81:'[',82:']',83:'^',84:'_',85:'`',86:'{',87:'|',88:'}',89:'~',"null":'"'}
iindex = {y:x for x,y in index.items()} #inverse index
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

def book2mape(baok,rd=False):
    try:
        try:
            f = open('books/'+baok+'.txt','r')
        except:
            f = open('books/'+baok+'.source','r')
        book = f.read()
        f.close()
    except:
        print("CANNOT FIND BOOK to map")
        return 0
    #print(book[:100])
    #return 0
    block_colors = {
        0: {'h':0, 's':0, 'l':0},       # Air
        1: {'h':0, 's':0, 'l':32},      # Stone
        2: {'h':94, 's':42, 'l':32},    # Grass
        3: {'h':27, 's':51, 'l':15},    # Dirt
        4: {'h':0, 's':0, 'l':25},      # Cobblestone
        8: {'h':228, 's':50, 'l':23},   # Water
        9: {'h':228, 's':50, 'l':23},   # Water
        10: {'h':16, 's':100, 'l':48},  # Lava
        11: {'h':16, 's':100, 'l':48},  # Lava
        12: {'h':53, 's':22, 'l':58},   # Sand
        13: {'h':21, 's':18, 'l':20},   # Gravel
        17: {'h':35, 's':93, 'l':15},   # Wood
        18: {'h':114, 's':64, 'l':22},  # Leaves
        24: {'h':48, 's':31, 'l':40},   # Sandstone
        37: {'h':60, 's':100, 'l':60},  # Yellow Flower
        38: {'h':0, 's':100, 'l':50},   # Red Flower
        50: {'h':60, 's':100, 'l':50},  # Torch
        51: {'h':55, 's':100, 'l':50},  # Fire
        59: {'h':123, 's':60, 'l':50},  # Crops
        60: {'h':35, 's':93, 'l':15},   # Farmland
        78: {'h':240, 's':10, 'l':85},  # Snow
        79: {'h':240, 's':10, 'l':95},  # Ice
        81: {'h':126, 's':61, 'l':20},  # Cacti
        82: {'h':7, 's':62, 'l':23},    # Clay
        83: {'h':123, 's':70, 'l':50},  # Sugarcane
        86: {'h':24, 's':100, 'l':45},  # Pumpkin
        91: {'h':24, 's':100, 'l':45},  # Jack-o-lantern
    }
    map = Image.new('RGB', (16*8,16*8))
    t = 64
    i =0.0
    #pixels = b""
    for bx in range(8):
        for bz in range(8):
            if i % 50 ==0:
                sys.stdout.write("Rendering image")
            elif i % 2 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            elif i % 50 == 49:
                sys.stdout.write("%5.1f%%\n" % (100*i/t))
            i +=1
            #get_map
            # Show an image of the chunk from above
            pixels = b""
            for z in range(16):
                for x in range(16):
                    # Find the highest block in this column
                    ground_height = 127
                    tints = []
                    for y in range(127,-1,-1):
                        #print(book[(bx*16 + x) + y*128 + (bz*16 + z)*128*16],iindex[book[(bx*16 + x) + y*128 + (bz*16 + z)*128*16]],sep=":")
                        block_id = iindex[book[(bx*16 + x) + y*128 + (bz*16 + z)*128*16]]
                        if block_id == "null":
                            block_id == 0
                        #block_data = chunk.blocks.get_data(x,y,z)
                        if rd: block_id = random.sample([0,1,2,3,4,8,9,10,11,12,13,17,18,24,37,38,50,51,59,60,78,79,81,82,83,86,91],1)[0]
                        #random block id overwrite
                        #print(block_id)
                        if (block_id == 8 or block_id == 9):
                            tints.append({'h':228, 's':50, 'l':23}) # Water
                        elif (block_id == 18):
                            if (0):
                                tints.append({'h':114, 's':64, 'l':22}) # Redwood Leaves
                            elif (0):
                                tints.append({'h':93, 's':39, 'l':10}) # Birch Leaves
                            else:
                                tints.append({'h':114, 's':64, 'l':22}) # Normal Leaves
                        elif (block_id == 79):
                            tints.append({'h':240, 's':5, 'l':95}) # Ice
                        elif (block_id == 51):
                            tints.append({'h':55, 's':100, 'l':50}) # Fire
                        elif (block_id != 0 or y == 0):
                            # Here is ground level
                            ground_height = y
                            break

                    color = block_colors[block_id] if (block_id in block_colors) else {'h':0, 's':0, 'l':100}
                    height_shift = (ground_height-64)*0.25
                    
                    final_color = {'h':color['h'], 's':color['s'], 'l':color['l']+height_shift}
                    if final_color['l'] > 100: final_color['l'] = 100
                    if final_color['l'] < 0: final_color['l'] = 0
                    
                    # Apply tints from translucent blocks
                    for tint in reversed(tints):
                        final_color = mape.hsl_slide(final_color, tint, 0.4)

                    rgb = mape.hsl2rgb(final_color['h'], final_color['s'], final_color['l'])
                    #print(rgb)

                    pixels += pack("BBB", rgb[0], rgb[1], rgb[2])
            #print("@@@@@@@@@@@@@",pixels,"@@@@@@@@@@@@")
            im = Image.frombytes('RGB', (16,16), pixels)
            #return im
            map.paste(im, (16*(bx-0),16*(bz-0)))
            #print("chunk printed {}".format(i))
            
    print(" done\n")
    filename = baok+".png"
    if rd:
        filename = "RANDOM"+filename
    map.save("maps/"+filename,"PNG")
    print("Saved map as %s" % filename)
    map.show()
    return 0

def main():
    gui = """
#########################################################
Intelligent Procedural Level Generation #1.00
using Minecraft
source: {}
commands: create source - 0, validate source - 1, map source - 2,
create book - 3, save from book(Alpha) - 4, map book - 5, map save - 6,
random book map -7, exit - 8
"""
    sourcename = glob.glob('books/*.source')[0]
    try:
        f = open(sourcename,'r')
        source = f.read()
        f.close()
    except:
        source = ""
    #index = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',24:'Y',25:'Z',26:'a',27:'b',28:'c',29:'d',30:'e',31:'f',32:'g',33:'h',34:'i',35:'j',36:'k',37:'l',38:'m',39:'n',40:'o',41:'p',42:'q',43:'r',44:'s',45:'t',46:'u',47:'v',48:'w',49:'x',50:'y',51:'z',52:'0',53:'1',54:'2',55:'3',56:'4',57:'5',58:'6',59:'7',60:'8',61:'9',62:'!',63:'#',64:'$',65:'%',66:'&',67:'(',68:')',69:'*',70:'+',71:',',72:'.',73:'/',74:':',75:';',76:'<',77:'=',78:'>',79:'?',80:'@',81:'[',82:']',83:'^',84:'_',85:'`',86:'{',87:'|',88:'}',89:'~',"null":'"'}
    #print(sourcename)
    while True:
        print(gui.format(sourcename))
        if source == "":
            world_folder = input('<SEED REQUIRED>Select Source World:')
            if world_folder == "":
                continue
            sourcename,source = convertbook(world_folder)
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
        if cmd+1 == 1:#create source book
            world_folder = input('Select Source World:')
            if world_folder == "":
                continue
            sourcename,source = convertbook(world_folder)
            sourcename = "books/"+sourcename
        elif cmd+1 == 2:#validate source(use source book to make copy of source save)
            continue
        elif cmd+1 == 3:#map source
            mape.main('mcsaves/saves/'+sourcename[6:-7])
            continue
        elif cmd+1 == 4:#generate new book using algorithms and such
            continue
        elif cmd+1 == 5:#turn a book into a save
            name = input('level name: ')
            dirs = "mcsaves/saves/"+name+"/"
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            level = gendats.generate_level()
            level.write_file(dirs+"level.dat")
            #alpha level creation
            #gendats.generate_chunk()
            continue
        elif cmd+1 == 6:#make a map of book
            book = input('name:')
            book2mape(book)
            continue
        elif cmd+1 == 7:#make map of save
            save = input('World Save:')
            mape.main('mcsaves/saves/'+save)
            continue
        elif cmd+1 == 8:#random book map
            book = input('seed:')
            book2mape(book,True)
            continue
        elif cmd+1 == 9:#exit
            break
        else:
            print("Command {} is not found".format(cmd))
    return 0

if __name__ == '__main__':
    """
    if (len(sys.argv) == 1):
        print("No world folder specified!")
        sys.exit(64) # EX_USAGE
    if sys.argv[1] == '--noshow' and len(sys.argv) > 2:
        world_folder = sys.argv[2]
    else:
        world_folder = sys.argv[1]
    # clean path name, eliminate trailing slashes. required for os.path.basename()
    world_folder = os.path.normpath(world_folder)
    if (not os.path.exists(world_folder)):
        print("No such folder as "+world_folder)
        sys.exit(72) # EX_IOERR
    """
    sys.exit(main())
