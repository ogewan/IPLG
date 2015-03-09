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
class foo():
    id = 10

def individual(length):
    'Create a member of the population.'
    print("random individual")
    return np.random.randint(91, size=length).reshape(128,128,256)

def quilt(length,s =''):
    print("quilted individual")
    if s == '':
        sys.exit(1)
    #res = []
    relamap = relmap
    #TODO
    if relamap==[]:
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
    return np.random.randint(91, size=length).reshape(128,128,256)#RANDOM

def population(s='',count=20, ran=False,length=4194304):
    """Create a number of individuals (i.e. a population).

    count: the number of individuals in the population
    length: the number of values per individual
    min: the minimum possible value in an individual's list of values
    max: the maximum possible value in an individual's list of values
    """
    print("REAL POPULATION")
    c = []
    if ran:
        c = np.array([individual(length) for x in range(count)],dtype=np.uint8)
    else:
        c = np.array([quilt(length,s) for x in range(count)],dtype=np.uint8)
    return c

def artpop(count=20, length=4194304):
    """create artificial population, non random individuals"""
    print("FICTIONAL POPULATION")
    return np.array([[x%90]*length for x in range(count)],dtype=np.uint8)

def fitness(individual, target=0):
    """
    Determine the fitness of an individual. Higher is better.

    individual: the individual to evaluate
    target: the target number individuals are aiming for
    """
    #todo
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
        score -= 1000
    spl = np.split(individual.flatten(),2)
    for b in spl[0]:
        if b == 0:
            score += 1
        elif ((b<=4)and(b>0)) or ((b>=8)and(b<=20)) or b==24 or b==31 or b==32 or ((37<=b)and(40>=b))or b==48 or b==59 or b==60 or ((b>=78)and(b<=83)) or b==142 or b==103 or b==111:
            score -= 2
        else:
            score -= 10
    for b in spl[1]:
        if b==0:
            score -= 1
        elif ((b<=5)and(b>2)) or ((b>=7)and(b<=11)) or((13<=b)and(16>=b)) or b==48 or b==56 or b==73 or b==129:
            score += 1
        else:
            score -= 10
    return score

def grade(pop, target=0):
    'Find average fitness for a population.'
    arr = [fitness(x, target) for x in pop]
    #print('\n')
    print(arr)
    summed = sum(arr)
    return summed / (len(pop) * 1.0)

def evolve(pop, end=False, s='', length=4194304, target=0, retain=0.25, random_select=0.05, mutate=0.01):
    print("start evolve")
    graded = [(fitness(x, target), x) for x in pop]
    graded = np.array([x[1] for x in sorted(graded,reverse=True)],dtype=np.uint8)
    retain_length = int(len(graded)*retain)
    parents = graded[:retain_length]
    # randomly add other individuals to
    # promote genetic diversity
    for individual in graded[retain_length:]:
        if random_select > random.random():
            np.append(parents,individual)
    # mutate some individuals
    for individual in parents:
        if mutate > np.random.random():
            for x in range(int(length*0.01)):
                #mutate 1% of the positions of an individual
                pos_to_mutate = np.random.randint(0, len(individual))
                # this mutation is not ideal, because it
                # restricts the range of possible values,
                # but the function is unaware of the min/max
                # values used to create the individuals,
                individual = individual.flatten()
                individual[pos_to_mutate] = np.random.choice(s)
                individual.reshape(128,128,256)
                #randint(min(individual), max(individual))
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
            child = np.zeros(128*128*256, dtype=uint8)
            print("C"+str(iuo)+",",end="",flush=True)
            for k in range(4194304):
                if ((k%128)%32)<16 and ((k%16384)%4096)<2048:
                    child[k] = male[k]
                elif ((k%128)%32)>=16 and ((k%16384)%4096)>=2048:
                    child[k] = male[k]
                else:
                    child[k] = female[-k]#reversed of female (adds genetic diversity)
                    #sys.stdout.write("f")
            #half = len(male) / 2
            #child = male[:half] + female[half:]
            children.append(child)
            iuo = iuo+1
    #print("\n")
    children = np.array(children,dtype=np.uint8).reshape(128,128,256)
    parents = np.concatenate(parents,children)
    if end:
        parents = [(fitness(x, target), x) for x in parents]
        parents = np.array([x[1] for x in sorted(parents,reverse=True)],dtype=np.uint8)
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

def main(gue=False,fake=1,fold='firstrun'):
    gui = """#########################################################
Intelligent Procedural Level Generation #5.00
using Minecraft, MCEdit, NBTExplorer, numpy, threading
source: {}
cmd: select source - 0, generate schematic - 1, test schematic - 2, exit - 3
"""
    while True:
        if(gue==False):
            sourcename = glob.glob('books/*.nsorce')[0]
            source = np.fromfile(sourcename, dtype=np.uint8)
            #print(source.shape)
            source.reshape(512,512,256)
            cmd = 1
        else:
            try:
                print(gui.format(sourcename))
            except:
                try:
                    sourcename = glob.glob('books/*.nsorce')[0]
                    source = np.fromfile(sourcename, dtype=np.uint8)
                    source.reshape(512,512,256)
                    continue
                except:
                    print('<SOURCE REQUIRED>')
                    print('add .nsorce to book dir and')
                    input('press enter')
                    continue
            try:
                cmd = int(input('c: '))
            except:
                print("command must be integer")
                continue
        if cmd == 0:#select source
            directory = glob.glob('books/*.nsorce')
            print(directory)
            wid = input('Select Source ID: ')
            try:
                sourcename = directory[int(wid)]
            except:
                continue
            source = np.fromfile(sourcename, dtype=np.uint8)
            source.reshape(512,512,256)
        elif cmd == 1:#generate schematics
            if (gue==False):
                name = fold
                psize = 20
                gennm = 10
            else:
                name = input('Book Folder name: ')
                try:
                    fake = int(input('Quilt - 0 or Solid - 1 or Random - 2\n'))
                except:
                    fake = 1
                try:
                    psize = math.fabs(int(input('Pop Size: ')))
                except:
                    psize = 20
                try:
                    gennm = math.fabs(int(input('Number of Generations: ')))
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
            else:
                p = population(source,psize)
            fitness_history = np.zeros(gennm+1, dtype=np.uint8)
            print("Int Grade")
            fitness_history[0] = grade(p)
            print("generation INTIAL")
            print(fitness_history[0])
            for i in range(gennm):
                print("generation "+str(i+1))
                if i==gennm-1:
                    p = evolve(p,True,source)#last p, returns reverse sorted list
                else:
                    p = evolve(p,s=source)
                fitness_history[i+1] = grade(p)
                print(fitness_history[0])
            jkl = 0
            for _ in p:
                _ = _.flatten()
                _.tofile(k+str(jkl)+'.book')
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
                mp = np.fromfile("books/"+name+".nbok", dtype=uint8)
                mine = _schema(mp.tolist())
            else:
                typ = 'b'
                mine = _schema()
            print(mine.pretty_tree())
            mine.write_file("schema/"+typ.upper()+name+".schematic")
        else:
            print("Command {} is not found".format(cmd))
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
#garbage
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
