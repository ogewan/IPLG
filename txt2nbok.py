import numpy as np
if __name__ == '__main__':
    name = input("Source name: ")
    result = input("Result name: ")
    q = open(name, 'r')
    w = q.read()
    q.close()
    e = w.replace('\n','  ')
    k = np.fromstring(e, dtype=np.uint8, sep='  ')
    #k.tofile('books/'+result)
    np.save('books/'+result, k)
