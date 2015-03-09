from collections import Counter
import numpy as np
if __name__ == '__main__':
    name = input("Source name: ")
    result = input("Result name: ")
    q = open(name, 'r')
    w = q.read()
    q.close()
    e = w.replace('\n','  ')
    e = e.split('  ')
    e.pop()
    #j = Counter(e)
    #print(j)
    k = np.array(e, dtype=np.uint8)
    print(Counter(k))
    k.tofile('books/'+result)
    #np.save('books/'+result, k)
