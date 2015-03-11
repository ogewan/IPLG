#!/usr/bin/env python
import os,sys
import time
import random
from io import BytesIO
from struct import pack, unpack
import array, math
import glob
from collections import Counter
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
"""'
methodology:
MCEdit(Minecraft World) -> NBTExplorer(.schematic) -> text2book(block array) -> source book
(source||random) -> child book
child book -> MCEdit(.schematic) -> Minecraft World
nbtexplorer can export .schematic block array as text which is coverted to
a book(base91 string) representing the 3D block array

genetic algortihm natively generates random individuals for its starting popupulation,
this requires many generations to get anywhere (even after 10 gens, it is effectively random}

quilting can be used to grow individuals from a source
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

evolve: breeding cross over chunk by chunk
"""
index = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',13:'N',14:'O',15:'P',16:'Q',17:'R',18:'S',19:'T',20:'U',21:'V',22:'W',23:'X',24:'Y',25:'Z',26:'a',27:'b',28:'c',29:'d',30:'e',31:'f',32:'g',33:'h',34:'i',35:'j',36:'k',37:'l',38:'m',39:'n',40:'o',41:'p',42:'q',43:'r',44:'s',45:'t',46:'u',47:'v',48:'w',49:'x',50:'y',51:'z',52:'0',53:'1',54:'2',55:'3',56:'4',57:'5',58:'6',59:'7',60:'8',61:'9',62:'!',63:'#',64:'$',65:'%',66:'&',67:'(',68:')',69:'*',70:'+',71:',',72:'.',73:'/',74:':',75:';',76:'<',77:'=',78:'>',79:'?',80:'@',81:'[',82:']',83:'^',84:'_',85:'`',86:'{',87:'|',88:'}',89:'~',90:'"'}
iindex = {y:x for x,y in index.items()} #inverse index
iindex['|'] = 103#melon
iindex['}'] = 111#waterlily
iindex['~'] = 129#emerald
iindex['"'] = 142#potatoes
#87:'|',88:'}',89:'~',90:'"'
relmap = []
class foo():
    id = 10

#schema grow 
def nexto(arr,ele,w=512,d=512):
    """helper function for finding all blocks adjacent to ele(block)"""
    """s    compass
    e u/d w
       n"""
    #edge cases
    #512*512 = 262144|256*262144 = 67108864
    prx = [0]*27
    #x + w(y +(hz))
    #ele = array id
    #arr = arr
    if (ele%(w*d))<w:
        #no north
        prx[0+3*(0+(3*0))] = -1#ne(high) (0,0,0)
        prx[0+3*(1+(3*0))] = -1#n (high) (0,1,0)
        prx[0+3*(2+(3*0))] = -1#nw(high) (0,2,0)
        prx[0+3*(0+(3*1))] = -1#ne(mid)  (0,0,1)
        prx[0+3*(1+(3*1))] = -1#n (mid)  (0,1,1)
        prx[0+3*(2+(3*1))] = -1#nw(mid)  (0,2,1)
        prx[0+3*(0+(3*2))] = -1#ne(low)  (0,0,2)
        prx[0+3*(1+(3*2))] = -1#n (low)  (0,1,2)
        prx[0+3*(2+(3*2))] = -1#nw(low)  (0,2,2)
    if (ele%(w*d))>((w*d)-w-1):
        #no south
        prx[2+3*(0+(3*0))] = -1#se(high) (2,0,0)
        prx[2+3*(1+(3*0))] = -1#s (high) (2,1,0)
        prx[2+3*(2+(3*0))] = -1#sw(high) (2,2,0)
        prx[2+3*(0+(3*1))] = -1#se(mid)  (2,0,1)
        prx[2+3*(1+(3*1))] = -1#s (mid)  (2,1,1)
        prx[2+3*(2+(3*1))] = -1#sw(mid)  (2,2,1)
        prx[2+3*(0+(3*2))] = -1#se(low)  (2,0,2)
        prx[2+3*(1+(3*2))] = -1#s (low)  (2,1,2)
        prx[2+3*(2+(3*2))] = -1#sw(low)  (2,2,2)
    if (ele%w)==0:
        #no west
        prx[0+3*(2+(3*0))] = -1#nw(high) (0,2,0)
        prx[1+3*(2+(3*0))] = -1# w(high) (1,2,0)
        prx[2+3*(2+(3*0))] = -1#sw(high) (2,2,0)
        prx[0+3*(2+(3*1))] = -1#nw(mid)  (0,2,1)
        prx[1+3*(2+(3*1))] = -1# w(mid)  (1,2,1)
        prx[2+3*(2+(3*1))] = -1#sw(mid)  (2,2,1)
        prx[0+3*(2+(3*2))] = -1#nw(low)  (0,2,2)
        prx[1+3*(2+(3*2))] = -1# w(low)  (1,2,2)
        prx[2+3*(2+(3*2))] = -1#sw(low)  (2,2,2)
    if (ele%w)==(w-1):
        #no east
        prx[0+3*(0+(3*0))] = -1#ne(high) (0,0,0)
        prx[1+3*(0+(3*0))] = -1# e(high) (1,0,0)
        prx[2+3*(0+(3*0))] = -1#se(high) (2,0,0)
        prx[0+3*(0+(3*1))] = -1#ne(mid)  (0,0,1)
        prx[1+3*(0+(3*1))] = -1# e(mid)  (1,0,1)
        prx[2+3*(0+(3*1))] = -1#se(mid)  (2,0,1)
        prx[0+3*(0+(3*2))] = -1#ne(low)  (0,0,2)
        prx[1+3*(0+(3*2))] = -1# e(low)  (1,0,2)
        prx[2+3*(0+(3*2))] = -1#se(low)  (2,0,2)
    if ele<(w*d)+w+1:
        #no down
        prx[0+3*(0+(3*2))] = -1#ne(low)  (0,0,2)
        prx[1+3*(0+(3*2))] = -1# e(low)  (1,0,2)
        prx[2+3*(0+(3*2))] = -1#se(low)  (2,0,2)
        prx[0+3*(1+(3*2))] = -1#n (low)  (0,1,2)
        prx[1+3*(1+(3*2))] = -1#  (low)  (1,1,2)
        prx[2+3*(1+(3*2))] = -1#s (low)  (2,1,2)
        prx[0+3*(2+(3*2))] = -1#nw(low)  (0,2,2)
        prx[1+3*(2+(3*2))] = -1# w(low)  (1,2,2)
        prx[2+3*(2+(3*2))] = -1#sw(low)  (2,2,2)
    if ((ele+512+1+262144)>(len(arr)-1)):
        #no up
        prx[0+3*(0+(3*0))] = -1#ne(high) (0,0,0)
        prx[1+3*(0+(3*0))] = -1# e(high) (1,0,0)
        prx[2+3*(0+(3*0))] = -1#se(high) (2,0,0)
        prx[0+3*(1+(3*0))] = -1#n (high) (0,1,0)
        prx[1+3*(1+(3*0))] = -1#  (high) (1,1,0)
        prx[2+3*(1+(3*0))] = -1#s (high) (2,1,0)
        prx[0+3*(2+(3*0))] = -1#nw(high) (0,2,0)
        prx[1+3*(2+(3*0))] = -1# w(high) (1,2,0)
        prx[2+3*(2+(3*0))] = -1#sw(high) (2,2,0)
    #/////////////////////////
    #print("id: "+str(ele))
    #print("    "+str(ele%512))
    #print("    "+str(ele%262144))
    try:
        prx[0+3*(2+(3*0))] = arr[ele-512-1+262144] if prx[0+3*(2+(3*0))]>-1 else -1#northwest ele-513 (high)
        prx[0+3*(1+(3*0))] = arr[ele-512+0+262144] if prx[0+3*(1+(3*0))]>-1 else -1#north (high)
        prx[0+3*(0+(3*0))] = arr[ele-512+1+262144] if prx[0+3*(0+(3*0))]>-1 else -1#northeast ele-511 (high)
        prx[0+3*(2+(3*1))] = arr[ele-512-1+0] if prx[0+3*(2+(3*1))]>-1 else -1#northwest ele-513 (mid)
        prx[0+3*(1+(3*1))] = arr[ele-512+0+0] if prx[0+3*(1+(3*1))]>-1 else -1#north (mid)
        prx[0+3*(0+(3*1))] = arr[ele-512+1+0] if prx[0+3*(0+(3*1))]>-1 else -1#northeast ele-511 (mid)
        prx[0+3*(2+(3*2))] = arr[ele-512-1-262144] if prx[0+3*(2+(3*2))]>-1 else -1#northwest ele-513 (low)
        prx[0+3*(1+(3*2))] = arr[ele-512+0-262144] if prx[0+3*(1+(3*2))]>-1 else -1#north (low)
        prx[0+3*(0+(3*2))] = arr[ele-512+1-262144] if prx[0+3*(0+(3*2))]>-1 else -1#northeast ele-511 (low)
        #/////////////////////////
        prx[2+3*(2+(3*0))] = arr[ele+512-1+262144] if prx[2+3*(2+(3*0))]>-1 else -1#southwest ele+511 (high)
        prx[2+3*(1+(3*0))] = arr[ele+512+0+262144] if prx[2+3*(1+(3*0))]>-1 else -1#south (high)
        prx[2+3*(0+(3*0))] = arr[ele+512+1+262144] if prx[2+3*(0+(3*0))]>-1 else -1#southeast ele+513 (high)
        prx[2+3*(2+(3*1))] = arr[ele+512-1+0] if prx[2+3*(2+(3*1))]>-1 else -1#southwest ele+511 (mid)
        prx[2+3*(1+(3*1))] = arr[ele+512+0+0] if prx[2+3*(1+(3*1))]>-1 else -1#south (mid)
        prx[2+3*(0+(3*1))] = arr[ele+512+1+0] if prx[2+3*(0+(3*1))]>-1 else -1#southeast ele+513 (mid)
        prx[2+3*(2+(3*2))] = arr[ele+512-1-262144] if prx[2+3*(2+(3*2))]>-1 else -1#southwest ele+511 (low)
        prx[2+3*(1+(3*2))] = arr[ele+512+0-262144] if prx[2+3*(1+(3*2))]>-1 else -1#south (low)
        prx[2+3*(0+(3*2))] = arr[ele+512+1-262144] if prx[2+3*(0+(3*2))]>-1 else -1#southeast ele+513 (low)
        #/////////////////////////
        prx[1+3*(2+(3*0))] = arr[ele-1+262144] if prx[1+3*(2+(3*0))]>-1 else -1#west (high)
        prx[1+3*(2+(3*1))] = arr[ele-1+0] if        prx[1+3*(2+(3*1))]>-1 else -1#west (mid)
        prx[1+3*(2+(3*2))] = arr[ele-1-262144] if prx[1+3*(2+(3*2))]>-1 else -1#west (low)
        #/////////////////////////
        #print("eL: "+str(prx[1+3*(0+(3*2))]>-1)+" neL: "+str(prx[0+3*(0+(3*2))]>-1)+" seL: "+str(prx[2+3*(0+(3*2))]>-1))
        prx[1+3*(0+(3*0))] = arr[ele+1+262144] if prx[1+3*(0+(3*0))]>-1 else -1#east (high)
        prx[1+3*(0+(3*1))] = arr[ele+1+0] if        prx[1+3*(0+(3*1))]>-1 else -1#east (mid)
        prx[1+3*(0+(3*2))] = arr[ele+1-262144] if prx[1+3*(0+(3*2))]>-1 else -1#east (low)
        #/////////////////////////
        prx[1+3*(1+(3*0))] = arr[ele+262144] if prx[1+3*(1+(3*0))]>-1 else -1#High
        #/////////////////////////
        prx[1+3*(1+(3*2))] = arr[ele-262144] if prx[1+3*(1+(3*2))]>-1 else -1#Low
        #print(prx)
    except:
        print("ID "+str(ele)+" MAX: "+str(len(arr)))
    return prx

def relationary(source):
    try:
        f = open(glob.glob('books/*.rlay')[0],'r')
        rela = f.read()
        f.close()
        print("relation map found")
        rela = rela.split("@")
        for u in range(len(rela)):
            rela[u] = rela[u].split("!")
            for t in rela[u]:
                rela[u][t] = rela[u][t].split("~")
    except:
        print("creating relation map")
        rela = [[[0]*91]*27]*91#relational database, 3D list
        fiindx = {y:x for x,y in index.items()} #fictional inverse index
        Asrce = [fiindx[_] for _ in list(source)]
        i =0.0
        for x in range(len(Asrce)):
            #x is element id in Asrce| y is element id in tmp
            #Asrce[x] is block id at x|tmp[y] is block id at y
            if i % math.pow(50,3) ==0:
                sys.stdout.write("Relating")
            elif i % math.pow(2,12) == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            elif i % math.pow(50,3) == math.pow(50,3)-1:
                sys.stdout.write("%5.1f%%\n" % (100*i/len(Asrce)))
            i +=1
            #x+=(67108864-8864)
            tmp = nexto(Asrce,x)
            for y in range(len(tmp)):
                #print(Asrce[x],y,tmp[y])
                if tmp[y]<0:
                    continue
                #print(rela[Asrce[x]])
                #print(rela[Asrce[x]][y])
                #print(rela[Asrce[x]][y][tmp[y]])
                rela[Asrce[x]][y][tmp[y]] += 1
        print("Stringifying")
        bar = []
        for z in rela:#[]*91
            foo =  []
            for a in rela[z]:#[]*27
                for c in rela[z][a]:#[]*91
                    rela[z][a][c] = 0
                foo.append('~'.join(rela[z][a]))
            bar.append('!'.join(foo))
        print("Printing")
        with open('books/source.rlay', 'w') as p:
            p.write('@'.join(bar))
    return rela

def access(filename):
    #get string from filename
    return list(open(filename,'r').read())

def deactv(string,name="child.tmp"):
    with open(name, 'w') as p:
        p.write(string)
    return name

def individual(length):
    'Create a member of the population.'
    print("random individual")
    return [index[random.choice(range(90))] for x in range(length) ]

def quilt(length,s ='',r=False):
    print("quilted individual")
    if s == '':
        sys.exit(1)
    #res = []
    relamap = relmap
    print("     WARNING: quilt() unfinished, Defaulting to individual()")
    return [index[random.choice(range(90))] for x in range(length) ]#RANDOM
    #TODO
    if relamap==[] and r:
        relamap = relationary(s)
    res = [(-1,0)]*length
    for b in range(int(length*0.00025)):#randomly choose 0.0025% of blocks
        res[random.randint(0,length-1)] = (random.randint(0,90),0)
    
    while True:#loop till map complete
        e = 0
        try:
            res.index((-1,0))#raises exception if no more -1 blocks; aka map complete
            while True:
                try:
                    targ = res.index((e,0))
                    res[targ] = (e,1)#set flag on solid block
                    #grow to surrounding blocks
                    FSRC = list(s)
                    random.shuffle(FSRC)
                    me = s[FSRC.index(e)]
                except ValueError:
                    if e >= 90:
                        break
                    e+=1
                    continue
        except ValueError:
            break
    res = [index[_] for _ in res]
    print("     WARNING: quilt() unfinished, Defaulting to individual()")
    return [index[random.choice(range(90))] for x in range(length) ]#RANDOM

def population(count=20, q=False, s='',length=4194304,disk=False):
    """
    Create a number of individuals (i.e. a population).

    count: the number of individuals in the population
    length: the number of values per individual
    min: the minimum possible value in an individual's list of values
    max: the maximum possible value in an individual's list of values

    """
    print("REAL POPULATION")
    c = []
    if disk:
        #disk
        x = []
        for r in range(count):
            print("Iv "+str(r))
            if q:
                x.append(''.join(individual(length)))
            else:
                x.append(''.join(quilt(length,s)))
        u = 0
        for _ in x:
            with open(str(u)+'.tmp', 'w') as p:
                p.write(_)
            c.append(str(u)+'.tmp')        
            u = u+1
        print(c)
    elif q:
        c = [quilt(length,s) for x in range(count) ]
    else:
        c = [individual(length) for x in range(count) ]
    return c

def artpop(count=20, length=4194304):
    """create artificial population, non random individuals"""
    print("FICTIONAL POPULATION")
    return [[index[(x%90)]]*length for x in range(count)]

def fitness(individual, target=0,disk=False):
    """
    Determine the fitness of an individual. Higher is better.

    individual: the individual to evaluate
    target: the target number individuals are aiming for
    """
    #todo
    return random.randint(0,50000)
    score = 50000
    stats = Counter(individual)
    if stats['A'] >= len(individual)/2:#air is more than half
        score += 10000
    if stats['A'] >= sorted(stats.values(),reverse=True)[0]:#air is most common
        score += 5000
    #print(index(stats['A']))
    try:
        if sorted(stats.values(),reverse=True).index(stats['A']) > 45:#air is top 45 blocks
            score += 2500
        else:
            score -= 5000
    except:
        score -= 10000
    top = [iindex[_] for _ in individual[:int(len(individual)/2)]]
    bot = [iindex[_] for _ in individual[int(len(individual)/2):]]
    for b in top:
        if b == 0:
            score += 1
        elif ((b<=4)and(b>0)) or ((b>=8)and(b<=20)) or b==24 or b==31 or b==32 or ((37<=b)and(40>=b))or b==48 or b==59 or b==60 or ((b>=78)and(b<=83)) or b==142 or b==103 or b==111:
            score -= 2
        else:
            score -= 10
    for b in bot:
        if b==0:
            score -= 1
        elif ((b<=5)and(b>2)) or ((b>=7)and(b<=11)) or((13<=b)and(16>=b)) or b==48 or b==56 or b==73 or b==129:
            score += 1
        else:
            score -= 10
    return score

def grade(pop, disk=False,target=0):
    'Find average fitness for a population.'
    arr = [fitness(x, target, disk) for x in pop]
    #print('\n')
    print(arr)
    summed = sum(arr)
    return summed / (len(pop) * 1.0)

def evolve(pop, length=4194304, target=0, retain=0.25, random_select=0.05, mutate=0.01,disk=False):
    graded = [ (fitness(x, target,disk), x) for x in pop]
    #test = [x[0] for x in sorted(graded,reverse=True)]
    graded = [ x[1] for x in sorted(graded,reverse=True)]
    #print(test)
    retain_length = int(len(graded)*retain)
    #print(test[:retain_length])
    parents = graded[:retain_length]
    # randomly add other individuals to
    # promote genetic diversity
    for individual in graded[retain_length:]:
        if random_select > random.random():
            parents.append(individual)
    # mutate some individuals
    for individual in parents:
        if mutate > random.random():
            if disk:
                oseds = access(individual)
            else:
                oseds = individual
            for x in range(int(length*0.01)):
                #mutate 1% of the positions of an individual
                pos_to_mutate = random.randint(0, len(oseds)-1)
                # this mutation is not ideal, because it
                # restricts the range of possible values,
                # but the function is unaware of the min/max
                # values used to create the individuals,
                oseds[pos_to_mutate] = index[random.choice(range(90))]
                #randint(min(individual), max(individual))
    # crossover parents to create children
    parents_length = len(parents)
    desired_length = len(pop) - parents_length
    children = []
    iuo = 0
    while len(children) < desired_length:
        male = random.randint(0, parents_length-1)
        female = random.randint(0, parents_length-1)
        if male != female:
            if disk:
                male = access(parents[male])
                female = access(parents[female])
            else:
                male = parents[male]
                female = parents[female]
            #chunk select: (x%128)<16 and (x%16384)<2048
            child = []
            print("C"+str(iuo)+",",end="",flush=True)
            for k in range(4194304):
                if ((k%128)%32)<16 and ((k%16384)%4096)<2048:
                    child.append(male[k])
                    #sys.stdout.write("m")
                elif ((k%128)%32)>=16 and ((k%16384)%4096)>=2048:
                    child.append(male[k])
                    #sys.stdout.write("m")
                else:
                    child.append(female[-k])#reversed of female (adds genetic diversity)
                    #sys.stdout.write("f")
            #half = len(male) / 2
            #child = male[:half] + female[half:]
            if disk:
                child = deactv(''.join(child),str(iuo)+"child.tmp")
            children.append(child)
            iuo = iuo+1
    #print("\n")
    parents.extend(children)
    return parents

def _schema(h=256,l=128,w=128,blst=[0]*4194304):
    if len(blst) < 4194304:
        #pad
        blst = blst + [0]*(4194304-len(blst))
    elif len(blst) > 4194304:
        #truncate
        blst = blst[:4194304]
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
#@profile
def main(auto=False,fold='firstrun',fake=0):
    gui = """
#########################################################
Intelligent Procedural Level Generation #3.00
using Minecraft, MCEdit, NBTExplorer
source: {}
cmd: select source - 0, generate schematic - 1, test schematic - 2, exit - 3
"""
    while True:
        if(auto):
            sourcename = glob.glob('books/*.source')[0]
            f = open(sourcename,'r')
            source = f.read()
            f.close()
            cmd = 1
        else:
            try:
                print(gui.format(sourcename))
            except:
                try:
                    sourcename = glob.glob('books/*.source')[0]
                    f = open(sourcename,'r')
                    source = f.read()
                    f.close()
                    continue
                except:
                    print('<SEED REQUIRED>')
                    print('add .source to book dir and')
                    input('press enter')
                    continue
            try:
                cmd = int(input('c: '))
            except:
                print("command must be integer")
                continue
        if cmd == 0:#select source
            directory = glob.glob('books/*.source')
            print(directory)
            wid = input('Select Source ID: ')
            try:
                sourcename = directory[int(wid)]
            except:
                continue
            handle = open(sourcename,'r')
            source = handle.read()
            handle.close()
        elif cmd == 1:#generate schematics
            if auto:
                name = fold
            else:
                name = input('Book Folder name:')
                try:
                    fake = int(input('Random - 0 or Solid - 1 or Quilt - 2'))
                except:
                    fake = 1
            if name == "":
                continue
            disk = False;
            j = "schema/"+name+"/"
            k = "books/"+name+"/"
            if not os.path.exists(j):
                os.makedirs(j)
            if not os.path.exists(k):
                os.makedirs(k)
            if fake==1:
                p = artpop()
            if fake==2:
                p = population(q=True,s=source)
            else:
                p = population()
            fitness_history = [grade(p)]
            print("generation INTIAL")
            print(fitness_history[0])
            for i in range(10):#100):
                print("generation "+str(i))
                p = evolve(p)
                r = grade(p)
                fitness_history.append(r)
                print(r)
            #for datum in fitness_history:
                #print(datum)
            #last p
            jkl = 0
            p = [(fitness(x), x) for x in p]
            p = [x[1] for x in sorted(p)]
            for _ in p:
                if disk:
                    m = access(_)
                else:
                    m = _
                mpl = [iindex[x] for x in m]
                mps = ''.join(m)
                with open(k+str(jkl)+'.book', 'w') as a:
                    a.write(mps)
                mine = _schema(blst=mpl)
                mine.write_file(j+str(jkl)+'.schematic')
                jkl = jkl+1
            trash = glob.glob('*.tmp')
            for z in trash:
                os.remove(z)
            if auto:
                break
        elif cmd == 3:#exit
            break
        elif cmd == 2:#test schematic
            name = input('Schematic Name:')
            try:
                typ = input('Type? B - Blank, R - Random, L - Random Legal, S - Source, Q - Quilt\n: ').lower()
            except:
                typ ='b'
            if name == "":
                continue
            if typ == 'b':
                mine = _schema()
            elif typ == 'r':
                mine = _schema(blst=[iindex[_] for _ in [random.choice(range(197)) for _ in range(4194304)]])
            elif typ == 'l':
                mpl = [index[random.choice(range(90))] for _ in range(4194304)]
                mps = ''.join(mpl)
                with open('books/'+typ.upper()+name+".book", 'w') as _:
                    _.write(mps)
                mine = _schema(blst=[iindex[_] for _ in mpl])
            elif typ == 'q':
                mpl = quilt(4194304,source)
                mps = ''.join(mpl)
                with open('books/'+typ.upper()+name+".book", 'w') as _:
                    _.write(mps)
                mine = _schema(blst=[iindex[_] for _ in mpl])
            elif typ == 's':
                srce = open("books/"+name+".book", 'r')
                mine = _schema(blst=[iindex[_] for _ in list(srce.read())])
                srce.close()
            else:
                typ = 'b'
                mine = _schema()
            print(mine.pretty_tree())
            mine.write_file("schema/"+typ.upper()+name+".schematic")
        else:
            print("Command {} is not found".format(cmd))
    return 0


if __name__ == '__main__':
    """schmatic = _schema()
    print(schmatic.pretty_tree())
    schmatic.write_file("artificial2.schematic")"""
    if len(sys.argv) >= 1:
        try:
            sys.exit(main(True,sys.argv[1],fake=2))
        except:
            sys.exit(main(True,fake=2))
    else:
        sys.exit(main())
