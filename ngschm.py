#!/usr/bin/env python
import os,sys
import time
import random
from io import BytesIO
from struct import pack, unpack
import array, math
import glob
from collections import Counter
import numpy as np
from operator import itemgetter
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
MCEdit(Minecraft World) -> NBTExplorer(.schematic) -> txt2nbok(numpy block array) -> source
(source||random) -> child book
child book -> MCEdit(.schematic) -> Minecraft World
nbtexplorer can export .schematic block array as text which was
coverted to a book(base91 string) representing the 3D block array
NOW it is converted to a numpy array which is printed in binary

genetic algortihm natively generates random individuals for its starting popupulation,
this requires many generations to get anywhere (even after 10 gens, it is effectively random}

quilting can be used to grow individuals from a source
No transcription will be done
evolve: breeding cross over chunk by chunk
"""
verbose = 0
class foo():
    id = 10

def printv(*args, sep=' ', end='\n', file=None, level=1):
	if verbose>=level:
		print(*args, sep=' ', end='\n', file=None)

def probability(a,d):
    """return index of random element based on probability"""
    c = np.sum(a)
    b = np.random.random()
    while b > c:
        b = np.random.random()
    for p in range(len(a)):
        #print(b,[p],a[p])
        if a[p] >= b:
            #print("win")
            return p
        else:
            b -= a[p]
            if b == 0:
                #print("fail")
                return 0#default block
    return 197

def individual(length):
    'Create a member of the population.'
    printv("random individual")
    return np.random.randint(91, size=length).reshape(256,128,128)

def quilt(length,s =''):
    fault = 0
    #mod = 32
    printv("quilted individual v2")
    if s == '':
        sys.exit(1)
    try:
        relam = np.fromfile(glob.glob('books/*.rlay')[0]).reshape(198,2,198)
    except:
        relam = np.zeros((198,2,198))
        #create relay
        for x in range(256):
            for y in range(512):
                for z in range(512):
                    if z==511 and y==511:
                        continue
                    elif z==511:
                        relam[s[x,y,z],1,s[x,y+1,z]] += 1
                    elif y==511:
                        relam[s[x,y,z],0,s[x,y,z+1]] += 1
                    else:
                        relam[s[x,y,z],0,s[x,y,z+1]] += 1
                        relam[s[x,y,z],1,s[x,y+1,z]] += 1
        relam = relam/(len(s.flatten()))
        print(len(s.flatten()))
        relam.tofile('books/0.rlay')
    res = np.zeros((256,128,128),dtype=np.uint8) - 1
    #a = np.random.randint(112)#64)
    b = np.random.randint(384)
    c = np.random.randint(384)
    for x in range(256):
        for y in range(128):
            for z in range(128):
                if (z%32)<16 and (y%32)<16:
                    #if (z%32)==0 or (y%32)==0:
                        #b = np.random.randint(512-16-max(z, y))
                    #print(b,z,y,z+b,y+b)
                    res[x,y,z] = s[x,y+b,z+b]
                elif z>=16 and y<16:
                    res[x,y,z] = probability(relam[res[x,y,z-1],0],res[x,y,z-1])
                elif z<16 and y>=16:
                    res[x,y,z] = s[x,y+c,z+c]#res[x,y,z] = probability(relam[res[x,y-1,z],1],res[x,y-1,z])
                elif z>=16 and y>=16:
                    res[x,y,z] = probability(relam[res[x,y-1,z],1],res[x,y-1,z])
                #else:
                    #res[x,y,z] = 0#np.fabs(relam[f,x,y,z]-np.random.random()).argsort()[0]
    """for b in range(int(length*0.00025)):#randomly choose 0.0025% of blocks
        ranid = np.random.randint(length)
        res[ranid,0] = s.flatten()[ranid*(int(len(s)/length))]
    while 255 in res:#loop till map complete
        if fault>=length:
            printv("OVERFLOW, quilt() has gone to far")
            #sys.exit(100)
    """
    #np.sort(relam.flatten(),kind='mergesort')[::-1].tofile("RELAYCnt.txt", sep=" ")
    return res

def population(s='',count=20, ran=False,length=4194304):
    """Create a number of individuals (i.e. a population).

    count: the number of individuals in the population
    length: the number of values per individual
    min: the minimum possible value in an individual's list of values
    max: the maximum possible value in an individual's list of values
    """
    printv("REAL POPULATION")
    if ran:
        c = np.array([individual(length) for x in range(count)],dtype=np.uint8)
    else:
        c = np.array([quilt(length,s) for x in range(count)],dtype=np.uint8)
    return c

def artpop(count=20, length=4194304):
    """create artificial population, non random individuals"""
    printv("FICTIONAL POPULATION")
    return np.array([[x%90]*length for x in range(count)],dtype=np.uint8).reshape(count,256,128,128)

def fitness(individual, s='', target=0):
    """
    Determine the fitness of an individual. Higher is better.

    individual: the individual to evaluate
    target: the target number individuals are aiming for
    """
    #return np.random.randint(0,50000)
    try:
        srccn = np.fromfile(glob.glob('books/*.cont')[0])
    except:
        srccn = np.zeros(197)
        scntt = Counter(s)
        for x in range(197):
            srccn[x] = scntt[x]
        srccn.tofile('books/0.cont')
    stats = np.zeros(197)
    stcnt = Counter(individual.flatten())
    for x in range(197):
        stats[x] = stcnt[x] 
    return 1000000 - np.sum(np.fabs(stats - (srccn/len(individual))))

def grade(pop, s='',target=0):
    'Find average fitness for a population.'
    arr = np.array([fitness(x, s, target) for x in pop])
    printv(arr)
    summed = np.sum(arr)
    return summed / (len(pop) * 1.0)

def evolve(pop, end=False, s='', length=4194304, target=0, retain=0.25, random_select=0.05, mutate=0.01):
    #printv("start evolve")
    graded = np.array([x[1] for x in sorted([(fitness(x, target), x) for x in pop],key=itemgetter(0),reverse=True)],dtype=np.uint8)
    retain_length = int(len(graded)*retain)
    parents = graded[:retain_length]
    # randomly add other individuals to promote genetic diversity
    for individual in graded[retain_length:]:
        if random_select > random.random():
            np.append(parents,individual)
    # mutate some individuals
    for individual in parents:
        if mutate > np.random.random():
            for x in range(int(length*0.01)):
                #mutate 1% of the positions of an individual
                pos_to_mutate = np.random.randint(0, len(individual))
                individual = individual.flatten()
                individual[pos_to_mutate] = np.random.choice(s)
                individual.reshape(256,128,128)
    # crossover parents to create children
    parents_length = len(parents)
    desired_length = len(pop) - parents_length
    children = []
    iuo = 0
    while len(children) < desired_length:
        male = np.random.randint(0, parents_length-1)
        female = np.random.randint(0, parents_length-1)
        if male != female:
            male = parents[male].flatten()
            female = parents[female].flatten()
            #chunk select: (x%128)<16 and (x%16384)<2048
            child = np.zeros(128*128*256, dtype=np.uint8)
            printv("C"+str(iuo)+",",end="",flush=True)
            for k in range(4194304):
                if ((k%128)%32)<16 and ((k%16384)%4096)<2048:
                    child[k] = male[k]
                elif ((k%128)%32)>=16 and ((k%16384)%4096)>=2048:
                    child[k] = male[k]
                else:
                    child[k] = female[-k]#reversed of female (adds genetic diversity)
            children.append(child)
            iuo = iuo+1
    children = np.array(children,dtype=np.uint8)
    children = children.reshape(desired_length,256,128,128)
    parents = np.concatenate((parents,children))
    if end:
        parents = np.array([x[1] for x in sorted([(fitness(x, target), x) for x in parents],key=itemgetter(0),reverse=True)],dtype=np.uint8)
    return parents

def _schema(blst=[0]*4194304,h=256,l=128,w=128):
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

def main(gue=False,fake=False,fold='qt'):
    gui = """#########################################################
Intelligent Procedural Level Generation #5.00
using Minecraft, MCEdit, NBTExplorer, numpy, threading
source: {}
cmd: select source - 0, generate schematic - 1, test schematic - 2, exit - 3
"""
    while True:
        if(gue==False):
            sourcename = glob.glob('books/*.nsorce')[0]
            source = np.fromfile(sourcename, dtype=np.uint8).reshape(256,512,512)
            cmd = 1
        else:
            try:
                printv(gui.format(sourcename))
            except:
                try:
                    sourcename = glob.glob('books/*.nsorce')[0]
                    source = np.fromfile(sourcename, dtype=np.uint8).reshape(256,512,512)
                    continue
                except:
                    printv('<SOURCE REQUIRED>')
                    printv('add .nsorce to book dir and')
                    input('press enter')
                    continue
            try:
                cmd = int(input('c: '))
            except:
                printv("command must be integer")
                continue
        if cmd == 0:#select source
            directory = glob.glob('books/*.nsorce')
            printv(directory)
            wid = input('Select Source ID: ')
            try:
                sourcename = directory[int(wid)]
            except:
                continue
            source = np.fromfile(sourcename, dtype=np.uint8).reshape(256,512,512)
        elif cmd == 1:#generate schematics
            if (gue==False):
                name = fold
                psize = 20
                gennm = 10
                #auto
                psize = 2
                gennm = 0
            else:
                name = input('Book Folder name: ')
                try:
                    fake = int(input('Quilt - 0 or Solid - 1 or Random - 2 or Quilt[NO GEN] - 3\n'))
                except:
                    fake = 1
                try:
                    psize = int(math.fabs(int(input('Pop Size: '))))
                except:
                    psize = 20
                try:
                    gennm = int(math.fabs(int(input('Number of Generations: '))))
                except:
                    gennm = 10
            if name == "":
                continue
            j = "schema/"+name+"/"
            k = "books/"+name+"/"
            if not os.path.exists(j):
                os.makedirs(j)
            if not os.path.exists(k):
                os.makedirs(k)
            if fake==1:
                p = artpop()
            elif fake==2:
                p = population(source,psize,True)
            elif fake==3:
                gennm = 0
                p = population(source,psize)
            else:
                p = population(source,psize)
            fitness_history = np.zeros(gennm+1)
            printv("Int Grade")
            fitness_history[0] = grade(p,s=source)
            printv("generation INTIAL")
            printv(fitness_history[0])
            for i in range(gennm):
                printv("generation "+str(i+1))
                if i==gennm-1:
                    p = evolve(p,True,source)#last p, returns reverse sorted list
                else:
                    p = evolve(p,s=source)
                fitness_history[i+1] = grade(p)
                printv(fitness_history[i+1])
            jkl = 0
            for _ in p:
                _ = _.flatten()
                _.tofile(k+str(jkl)+'.nbok')
                mine = _schema(blst=_.tolist())
                mine.write_file(j+str(jkl)+'.schematic')
                jkl = jkl+1
            if gue==False:
                break
        elif cmd == 3:#exit
            break
        elif cmd == 2:#test schematic
            name = input('Schematic Name:')
            try:
                typ = input('Type? B - Blank, R - Random, L - Random Legal, S - Source(nbok), Q - Quilt\n: ').lower()
            except:
                typ ='b'
            if name == "":
                continue
            if typ == 'b':
                mine = _schema()
            elif typ == 'r':
                mp = np.random.randint(197, size=4194304)
                mp.tofile('books/'+typ.upper()+name+".book")
                mine = _schema(mp.tolist())
            elif typ == 'l':
                mp = np.random.randint(91, size=4194304)
                mp.tofile('books/'+typ.upper()+name+".book")
                mine = _schema(mp.tolist())
            elif typ == 'q':
                mp = quilt(4194304,source)
                mp.tofile('books/'+typ.upper()+name+".book")
                mine = _schema(mp.tolist())
            elif typ == 's':
                mp = np.fromfile("books/"+name+".nbok", dtype=np.uint8)
                mine = _schema(mp.tolist())
            else:
                typ = 'b'
                mine = _schema()
            printv(mine.pretty_tree())
            mine.write_file("schema/"+typ.upper()+name+".schematic")
        else:
            printv("Command {} is not found".format(cmd))
    return 0


if __name__ == '__main__':
    g = False
    f = False
    if len(sys.argv) >= 2:
        try:
            sys.argv.index("-g")
            g = True
        except:
            pass
        try:
            sys.argv.index("-f")
            f = True
        except:
            pass
        if g and f:
            sys.exit(main(g,f))
        elif g:
            sys.exit(main(g))
        elif f:
            sys.exit(main(fake=f))
    else:
        sys.exit(main())
