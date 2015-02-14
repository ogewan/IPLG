#!/usr/bin/env python
"""
creates minecraft map
"""
import locale, os, sys
import json
import re, math#, binascii
from struct import pack, unpack
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
"""'
minecraft map -> string
minecraft map -> image
string -> minecraft map
string -> image

region file = 32*32 (x,z) chunks = 1024 chunks = 67108864 blocks/bytes = 64  mB MAX
chunk = 16,256,256 (x,y,z) blocks = 65536 blocks/bytes = 0.06 mB MAX
block = 1 byte
target:
map = 128*256*128  (x,y,z) = 4194304 blocks/bytes = 64 chunks = 8*8 (x,z) chunks = 4 mB
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

def main(world_folder):
    world = McRegionWorldFolder(world_folder)  # map still only supports McRegion maps
    bb = world.get_boundingbox()
    b_id= {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',24:'Y',25:'Z',26:'a',27:'b',28:'c',29:'d',30:'e',31:'f',32:'g',33:'h',34:'i',35:'j',36:'k',37:'l',38:'m',39:'n',40:'o',41:'p',42:'q',43:'r',44:'s',45:'t',46:'u',47:'v',48:'w',49:'x',50:'y',51:'z',52:'0',53:'1',54:'2',55:'3',56:'4',57:'5',58:'6',59:'7',60:'8',61:'9',62:'!',63:'#',64:'$',65:'%',66:'&',67:'(',68:')',69:'*',70:'+',71:',',72:'.',73:'/',74:':',75:';',76:'<',77:'=',78:'>',79:'?',80:'@',81:'[',82:']',83:'^',84:'_',85:'`',86:'{',87:'|',88:'}',89:'~',"null":'"'}
    t = world.chunk_count()
    mapMAX = t*16*16*128 #or 32768t
    mapstr = '"'*mapMAX
    mapACT = 0
    mape = list(mapstr)
    mpae = {}
    print(world)
    #return 0
    try:
        i =0.0
        for chunk in world.iter_chunks():
            if i % 50 ==0:
                sys.stdout.write("Rendering image")
            elif i % 2 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            elif i % 50 == 49:
                sys.stdout.write("%5.1f%%\n" % (100*i/t))
            i +=1
            #chunkmap = get_map(chunk)
            cx,cz = chunk.get_coords()
            for z in range(16):
                for x in range(16):
                    for y in range(128):
                        block_id = chunk.blocks.get_block(x,y,z)
                        if block_id > 89: block_id = 12 #turn block into sand if it is not first 91 blocks
                        #91st entry changed to null
                        mpae[(cx*16 + x) + y*128 + (cz*16 + z)*128*16] = b_id[block_id]
                        #print(b_id[block_id])
                        #mapACT+=1
                        
        print(" done\n")
        filename = os.path.basename(world_folder)+".txt"
        mapstr = ''.join(mape)
        mapdic = json.dumps(mpae)
        print(mapMAX)
        print(len(mapdic))
        #with open('DICTIONARY'+filename, 'w') as fi:
            #fi.write(mapdic)
        #with open('b'+filename,'w') as fo:
            #fo.write(binascii.a2b_uu(mapstr))
        print("Saved map as %s" % filename)
    except KeyboardInterrupt:
        """print(" aborted\n")
        filename = os.path.basename(world_folder)+".partial.png"
        map.save(filename,"PNG")
        print("Saved map as %s" % filename)
        return 75 # EX_TEMPFAIL"""
    return 0 # NOERR


if __name__ == '__main__':
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
    
    sys.exit(main(world_folder))
