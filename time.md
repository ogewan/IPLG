Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

Quilt V2 - VERY SLOW
timeit('''s[np.unravel_index(np.random.choice(nst['arr_'+str(7)])+1,[256,512,512])]''','''import numpy as np
s = np.fromfile("books//0.nsorce",dtype=np.uint8).reshape(256,512,512)
nst = np.load("books//0.npz")''',number=100)
0.5940110517198036
>>> timeit('''s[np.unravel_index(np.random.choice(nst['arr_'+str(7)])+1,[256,512,512])]''','''import numpy as np
s = np.fromfile("books//0.nsorce",dtype=np.uint8).reshape(256,512,512)
nst = np.load("books//0.npz")''',number=1000)
5.992977313594679
>>> timeit('''es[np.random.choice(nst['arr_'+str(7)])+1]''','''import numpy as np
es = np.fromfile("books//0.nsorce",dtype=np.uint8).reshape(256,512,512).flatten()
nst = np.load("books//0.npz")''',number=100)
0.5923405670368993
>>> timeit('''es[np.random.choice(nst['arr_'+str(7)])+1]''','''import numpy as np
es = np.fromfile("books//0.nsorce",dtype=np.uint8).reshape(256,512,512).flatten()
nst = np.load("books//0.npz")''',number=1000)
5.89890591258802

best case: 5.89 
((256*128*128)/1000)*5.89 seconds = 24704.46 sec = 6.86235 hours per map (64 chunks)
((256*64*64)/1000)*5.89 seconds = 6176.112639999999 sec = 1.71559 hours per map (32 chunks)

ngschm.py - premade 20 individuals, 10 generations w/ fitness
Exit code      : 0
Elapsed time   : 828.16
Kernel time    : 3.29 (0.4%)
User time      : 819.68 (99.0%)
page fault #   : 2244454
Working set    : 524464 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 520656 KB

Exit code      : 0
Elapsed time   : 824.69
Kernel time    : 3.17 (0.4%)
User time      : 817.54 (99.1%)
page fault #   : 2250605
Working set    : 524432 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 520608 KB

Exit code      : 0
Elapsed time   : 2249.36
Kernel time    : 741.15 (32.9%)
User time      : 1501.28 (66.7%)
page fault #   : 733871036
Working set    : 524508 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 520648 KB

Exit code      : 0
Elapsed time   : 806.21
Kernel time    : 2.42 (0.3%)
User time      : 803.03 (99.6%)
page fault #   : 2232604
Working set    : 524476 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 520620 KB

ngschm.py - full; 20 quilted individuals, 10 generations w/ fitness
Exit code      : 0
Elapsed time   : 5852.52
Kernel time    : 2295.82 (39.2%)
User time      : 3521.21 (60.2%)
page fault #   : 2197799954
Working set    : 525112 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 521208 KB

ngschm.py
Exit code      : 0
Elapsed time   : 3014.72
Kernel time    : 765.59 (25.4%)
User time      : 2213.51 (73.4%)
page fault #   : 734549705
Working set    : 525288 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 521380 KB

Exit code      : 0
Elapsed time   : 4437.92
Kernel time    : 1541.80 (34.7%)
User time      : 2850.61 (64.2%)
page fault #   : 1466167254
Working set    : 525208 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 521284 KB



ngschm.py - 2 quilted individuals, no generation, no fitness
Exit code      : 0
Elapsed time   : 59.40
Kernel time    : 0.33 (0.6%)
User time      : 58.55 (98.6%)
page fault #   : 103374
Working set    : 221576 KB
Paged pool     : 256 KB
Non-paged pool : 14 KB
Page file size : 217704 KB

ngschm.py - 20 quilted
Exit code      : 1
Elapsed time   : 606.86
Kernel time    : 0.67 (0.1%)
User time      : 599.51 (98.8%)
page fault #   : 94018
Working set    : 287084 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 283304 KB

Exit code      : 1
Elapsed time   : 606.86
Kernel time    : 0.67 (0.1%)
User time      : 599.51 (98.8%)
page fault #   : 94018
Working set    : 287084 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 283304 KB

Exit code      : 1
Elapsed time   : 618.29
Kernel time    : 0.67 (0.1%)
User time      : 610.45 (98.7%)
page fault #   : 122766
Working set    : 287136 KB
Paged pool     : 256 KB
Non-paged pool : 15 KB
Page file size : 283356 KB

ngschm.py - no fitness, random individuals
Exit code      : 0
Elapsed time   : 442.80 (7 min)
Kernel time    : 1.90 (0.4%)
User time      : 440.75 (99.5%)
page fault #   : 1891746
Working set    : 532716 KB
Paged pool     : 248 KB
Non-paged pool : 15 KB
Page file size : 529160 KB

ngschm.py fitness, random individuals
Exit code      : 0
Elapsed time   : 806.93 (13 min)
Kernel time    : 3.32 (0.4%)
User time      : 803.16 (99.5%)
page fault #   : 2356035
Working set    : 532628 KB
Paged pool     : 248 KB
Non-paged pool : 15 KB
Page file size : 529112 KB

gschem.py - no fitness, random individuals
Exit code      : 0
Elapsed time   : 1960.60 (30 min)
Kernel time    : 13.32 (0.7%)
User time      : 541.18 (27.6%)
page fault #   : 14184813
Working set    : 1291764 KB
Paged pool     : 121 KB
Non-paged pool : 12 KB
Page file size : 1365156 KB