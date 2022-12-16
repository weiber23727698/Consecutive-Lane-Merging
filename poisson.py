import numpy as np
import json
import os
def poisson_gen(lam,length):
    seq = np.zeros(length)
    rng = np.random.default_rng()
    poisson = rng.poisson(lam = lam, size= int(length*3/lam))
    time=0
    num=0
    for i in range(len(poisson)):
        if poisson[i]>0:
            for j in range(poisson[i]):
                seq[num]=time+round(np.random.rand(),3)
                num+=1
                if num>=length:
                    break
        if num>=length:
            break
        time+=1
    np.sort(seq)
    return(seq.tolist())

if(__name__=="__main__"):
    os.makedirs("temp", exist_ok=True)
    for i in range(1,6):    
        poisson_1 = poisson_gen(i/10,30)
        poisson_2 = poisson_gen(i/10,30)
        poisson_3 = poisson_gen(i/10,30)
        json.dump({"Lane_A":poisson_1,"Lane_B":poisson_2,"Lane_C":poisson_3}, open(f"temp/test_data_{i}.json", 'w',encoding='utf-8'), indent=2, ensure_ascii=False)

    