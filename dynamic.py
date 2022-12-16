import numpy as np
import json

def first_merge_dynamic(W_same, W_diff, Lane_A = [], Lane_B = []):
    schedule = np.full(shape=(len(Lane_A),len(Lane_B),2), fill_value = np.inf ,dtype=np.float)
    schedule[0,0,0] = 0
    schedule[0,0,1] = 0
    schedule[1,0,0]=Lane_A[1]
    schedule[0,1,1]=Lane_B[1]
    for i in range(2,len(Lane_A)):
        schedule[i,0,0]=max(Lane_A[i],schedule[i-1,0,0]+W_same)
    for j in range(2,len(Lane_B)):
        schedule[0,j,1]=max(Lane_B[j],schedule[0,j-1,1]+W_same)
    for i in range(1,len(Lane_A)):
        for j in range(1,len(Lane_B)):
            schedule[i,j,0]=min(max(Lane_A[i],schedule[i-1,j,0]+W_same),
                                max(Lane_A[i],schedule[i-1,j,1]+W_diff)
                                )
            schedule[i,j,1]=min(max(Lane_B[j],schedule[i,j-1,0]+W_diff),
                                max(Lane_B[j],schedule[i,j-1,1]+W_same)
                                )
    result=min(schedule[len(Lane_A)-1,len(Lane_B)-1,0],schedule[len(Lane_A)-1,len(Lane_B)-1,1])
    return(result,schedule)

def second_merge_dynamic(W1_same, W1_diff, W2_same, W2_diff ,tf_time , first_schedule, Lane_A = [], Lane_B = [], Lane_C = []):
    alpha = len(Lane_A)
    beta = len(Lane_B)
    gamma = len(Lane_C)

    schedule = np.full(shape=(alpha,beta,gamma,4), fill_value = np.inf ,dtype=np.float)
    delay = np.zeros(shape=(alpha,beta,gamma,4),dtype=np.float)
    order = np.zeros(shape=(alpha,beta,gamma,4),dtype=np.int)
    A=0
    B=1
    CA=2
    CB=3
    schedule[0,0,0,A ] = 0
    schedule[0,0,0,B ] = 0
    schedule[0,0,0,CA] = 0
    schedule[0,0,0,CB] = 0
    schedule[1,0,0,A ] = Lane_A[1]
    schedule[0,1,0,B ] = Lane_B[1]
    schedule[0,0,1,CA] = Lane_C[1]
    schedule[0,0,1,CB] = Lane_C[1]
    
    order[1,0,0,A ] = A
    order[0,1,0,B ] = B
    order[0,0,1,CA] = CA
    order[0,0,1,CB] = CB
    #A init
    for i in range(2,alpha):
        first_merge_A_same = max( Lane_A[i], first_schedule[i-1,0,A] + W1_same)
        schedule[i,0,0,A] = max( first_merge_A_same + tf_time,
                                        schedule[i-1,0,0,A ] + W2_same)
        delay[i,0,0,A] = delay[i-1,0,0,A]
        delay[i,0,0,A] += schedule[i,0,0,A] - first_merge_A_same - tf_time
        delay[i,0,0,A] += first_merge_A_same - Lane_A[i]
        order[i,0,0,A] = A
    #B init
    for j in range(2,beta):
        first_merge_B_same = max( Lane_B[j], first_schedule[0,j-1,B] + W1_same)
        schedule[0,j,0,B ] = max( max( Lane_B[j], first_schedule[0,j-1,B] + W1_same) + tf_time,
                                        schedule[0,j-1,0,B ] + W2_same)
        delay[0,j,0,B] = delay[0,j-1,0,B]
        delay[0,j,0,B] += schedule[0,j,0,B] - first_merge_B_same - tf_time
        delay[0,j,0,B] += first_merge_B_same - Lane_B[j]
        order[0,j,0,B] = B
    #C init
    for k in range(2,gamma):
        schedule[0,0,k,CA] = max( Lane_C[k], schedule[0,0,k-1,CA] + W2_same)
        delay[0,0,k,CA] = delay[0,0,k-1,CA]
        delay[0,0,k,CA] += schedule[0,0,k,CA] - Lane_C[k]
        schedule[0,0,k,CB] = max( Lane_C[k], schedule[0,0,k-1,CB] + W2_same)
        delay[0,0,k,CB] = delay[0,0,k-1,CB]
        delay[0,0,k,CB] += schedule[0,0,k,CB] - Lane_C[k]
        
        order[0,0,k,CA] = CA
        order[0,0,k,CB] = CB
    #A B init
    for i in range(1,alpha):
        for j in range(1,beta):
            #A
            choice=[max(  max( Lane_A[i], first_schedule[i-1,j,A] + W1_same) + tf_time,
                                            schedule[i-1,j,0,A ] + W2_same),
                    max( max( Lane_A[i], first_schedule[i-1,j,B] + W1_diff) + tf_time,
                                            schedule[i-1,j,0,B ] + W2_same)]
            index_min = np.argmin(choice)
            schedule[i,j,0,A ] = choice[index_min]
            if   index_min == 0:
                delay[i,j,0,A] = delay[i-1,j,0,A]
                order[i,j,0,A] = A
            elif index_min == 1: 
                delay[i,j,0,A] = delay[i-1,j,0,B]
                order[i,j,0,A] = B
            delay[i,j,0,A] += schedule[i,j,0,A] - Lane_A[i] - tf_time
            #B
            choice = [max( max( Lane_B[j], first_schedule[i,j-1,A] + W1_diff) + tf_time,
                                            schedule[i,j-1,0,A ] + W2_same),
                      max( max( Lane_B[j], first_schedule[i,j-1,B]+ W1_same) + tf_time,
                                            schedule[i,j-1,0,B ] + W2_same)]
            index_min = np.argmin(choice)
            schedule[i,j,0,B ] = choice[index_min]
            if   index_min == 0:
                delay[i,j,0,B] = delay[i,j-1,0,A]
                order[i,j,0,B] = A
            elif index_min == 1: 
                delay[i,j,0,B] = delay[i,j-1,0,B]
                order[i,j,0,B] = B
            delay[i,j,0,B] += schedule[i,j,0,B] - Lane_B[j] - tf_time
    #A C init
    for i in range(1,alpha):
        for k in range(1,gamma):
            #A
            choice = [  max( max( Lane_A[i], first_schedule[i-1,0,A] + W1_same) + tf_time,
                                            schedule[i-1,0,k,A ] + W2_same),
                        max( max( Lane_A[i], first_schedule[i-1,0,A] + W1_same) + tf_time,
                                            schedule[i-1,0,k,CA] + W2_diff)]
            '''max( max( Lane_A[i], first_schedule[i-1,0,B] + W1_diff) + tf_time,
                                            schedule[i-1,0,k,CB] + W2_diff)'''
            index_min = np.argmin(choice)
            schedule[i,0,k,A ] = choice[index_min]
            if   index_min == 0:
                delay[i,0,k,A] = delay[i-1,0,k,A]
                order[i,0,k,A] = A
            elif index_min == 1:
                delay[i,0,k,A] = delay[i-1,0,k,CA]
                order[i,0,k,A] = CA
            '''elif index_min == 2:
                delay[i,0,k,A] = delay[i-1,0,k,CB]'''
            delay[i,0,k,A] += schedule[i,0,k,A] - Lane_A[i] - tf_time

            #CA
            choice = [  max( Lane_C[k], schedule[i,0,k-1,A ] + W2_diff),
                        max( Lane_C[k], schedule[i,0,k-1,CA] + W2_same)]
            index_min = np.argmin(choice)            
            schedule[i,0,k,CA] = choice[index_min]
            if   index_min == 0:
                delay[i,0,k,CA] = delay[i,0,k-1,A]
                order[i,0,k,CA] = A
            elif index_min == 1:
                delay[i,0,k,CA] = delay[i,0,k-1,CA]
                order[i,0,k,CA] = CA
            delay[i,0,k,CA] += schedule[i,0,k,CA] - Lane_C[k]
            '''#CB
            schedule[i,0,k,CB] = max(   Lane_C[k], schedule[i,0,k-1,CB] + W2_same)
            delay[i,0,k,CB] =delay[i,0,k-1,CB]
            delay[i,0,k,CB] += schedule[i,0,k,CB] - Lane_C[k]'''
    #B C init
    for j in range(1,beta):
        for k in range(1,gamma):
            #B
            choice = [  max( max( Lane_B[j], first_schedule[0,j-1,B]+ W1_same) + tf_time,
                                            schedule[0,j-1,k,B ] + W2_same),
                        max( max( Lane_B[j], first_schedule[0,j-1,B] + W1_same) + tf_time,
                                            schedule[0,j-1,k,CB] + W2_diff)]
            '''max( max( Lane_B[j], first_schedule[0,j-1,A] + W1_diff) + tf_time,
                                            schedule[0,j-1,k,CA] + W2_diff)'''
            index_min = np.argmin(choice)
            schedule[0,j,k,B ] = choice[index_min]
            if   index_min == 0:
                delay[0,j,k,B] = delay[0,j-1,k,B ]
                order[0,j,k,B] = B
            elif index_min == 1:
                delay[0,j,k,B] = delay[0,j-1,k,CB]
                order[0,j,k,B] = CB
            '''elif index_min == 2:
                delay[0,j,k,B] = delay[0,j-1,k,CA]
                order[0,j,k,B] = 3'''
            delay[0,j,k,B] += schedule[0,j,k,B] - Lane_B[j] - tf_time
            
            '''#CA
            schedule[0,j,k,CA] = max(   Lane_C[k], schedule[0,j,k-1,CA] + W2_same)
            delay[0,j,k,CA] = delay[0,j,k-1,CA]
            delay[0,j,k,CA] += schedule[0,j,k,CA] - Lane_C[k]'''
            
            #CB 
            choice = [  max( Lane_C[k], schedule[0,j,k-1,B ] + W2_diff),
                        max( Lane_C[k], schedule[0,j,k-1,CB] + W2_same)]
            index_min = np.argmin(choice)
            schedule[0,j,k,CB] = choice[index_min]
            if   index_min == 0:
                delay[0,j,k,CB] = delay[0,j,k-1,B]
                order[0,j,k,CB] = B
            elif index_min == 1:
                delay[0,j,k,CB] = delay[0,j,k-1,CB]
                order[0,j,k,CB] = CB
            delay[0,j,k,CB] += schedule[0,j,k,CB] - Lane_C[k]
    for i in range(1,alpha):
        for j in range(1,beta):
            for k in range(1,gamma):
                #A
                choice = [  max( max( Lane_A[i], first_schedule[i-1,j,A] + W1_same) + tf_time,
                                schedule[i-1,j,k,A ] + W2_same),
                            max( max( Lane_A[i], first_schedule[i-1,j,B] + W1_diff) + tf_time,
                                schedule[i-1,j,k,B ] + W2_same),
                            max( max( Lane_A[i], first_schedule[i-1,j,A] + W1_same) + tf_time,
                                schedule[i-1,j,k,CA] + W2_diff),
                            max( max( Lane_A[i], first_schedule[i-1,j,B] + W1_diff) + tf_time,
                                schedule[i-1,j,k,CB] + W2_diff)]
                index_min = np.argmin(choice)
                schedule[i,j,k,A] = choice[index_min]
                if   index_min == 0:
                    delay[i,j,k,A] = delay[i-1,j,k,A]
                    order[i,j,k,A] = A
                elif index_min == 1:
                    delay[i,j,k,A] = delay[i-1,j,k,B]
                    order[i,j,k,A] = B
                elif index_min == 2:
                    delay[i,j,k,A] = delay[i-1,j,k,CA] 
                    order[i,j,k,A] = CA
                elif index_min == 3:
                    delay[i,j,k,A] = delay[i-1,j,k,CB] 
                    order[i,j,k,A] = CB
                delay[i,j,k,A] += schedule[i,j,k,A] - Lane_A[i] - tf_time
                #B
                choice = [  max( max( Lane_B[j], first_schedule[i,j-1,A] + W1_diff) + tf_time,
                                schedule[i,j-1,k,A ] + W2_same),
                            max( max( Lane_B[j], first_schedule[i,j-1,B]+ W1_same) + tf_time,
                                schedule[i,j-1,k,B ] + W2_same),
                            max( max( Lane_B[j], first_schedule[i,j-1,A] + W1_diff) + tf_time,
                                schedule[i,j-1,k,CA] + W2_diff),
                            max( max( Lane_B[j], first_schedule[i,j-1,B] + W1_same) + tf_time,
                                schedule[i,j-1,k,CB] + W2_diff)]
                index_min = np.argmin(choice)
                schedule[i,j,k,B] = choice[index_min]
                if   index_min == 0:
                    delay[i,j,k,B] = delay[i,j-1,k,A] 
                    order[i,j,k,B] = A
                elif index_min == 1:
                    delay[i,j,k,B] = delay[i,j-1,k,B] 
                    order[i,j,k,B] = B
                elif index_min == 2:
                    delay[i,j,k,B] = delay[i,j-1,k,CA] 
                    order[i,j,k,B] = CA
                elif index_min == 3:
                    delay[i,j,k,B] = delay[i,j-1,k,CB] 
                    order[i,j,k,B] = CB
                delay[i,j,k,B] += schedule[i,j,k,B] - Lane_B[j] - tf_time

                #CA
                choice = [  max( Lane_C[k], schedule[i,j,k-1,A ] + W2_diff),
                            max( Lane_C[k], schedule[i,j,k-1,CA] + W2_same)]
                index_min = np.argmin(choice)
                schedule[i,j,k,CA] = choice[index_min]
                if   index_min == 0:
                    delay[i,j,k,CA] = delay[i,j,k-1,A] 
                    order[i,j,k,CA] = A
                elif index_min == 1:
                    delay[i,j,k,CA] = delay[i,j,k-1,CA]
                    order[i,j,k,CA] = CA
                delay[i,j,k,CA] += schedule[i,j,k,CA] - Lane_C[k]
                
                #CB
                choice = [  max( Lane_C[k], schedule[i,j,k-1,B ] + W2_diff),
                            max( Lane_C[k], schedule[i,j,k-1,CB] + W2_same)]
                index_min = np.argmin(choice)
                schedule[i,j,k,CB] = choice[index_min]
                if   index_min == 0:
                    delay[i,j,k,CB] = delay[i,j,k-1,B] 
                    order[i,j,k,CB] = B
                elif index_min == 1:
                    delay[i,j,k,CB] = delay[i,j,k-1,CB]
                    order[i,j,k,CB] = CB
                delay[i,j,k,CB] += schedule[i,j,k,CB] - Lane_C[k]
    choice = [  schedule[alpha-1,beta-1,gamma-1,A ],
                schedule[alpha-1,beta-1,gamma-1,B ],
                schedule[alpha-1,beta-1,gamma-1,CA],
                schedule[alpha-1,beta-1,gamma-1,CB]]
    index_min = np.argmin(choice)
    last = choice[index_min]
    total_delay = 0
    
    if index_min == 0:
        total_delay = delay[alpha-1,beta-1,gamma-1,A ]
    elif index_min == 1:
        total_delay = delay[alpha-1,beta-1,gamma-1,B ]
    elif index_min == 2:
        total_delay = delay[alpha-1,beta-1,gamma-1,CA]
    elif index_min == 3:
        total_delay = delay[alpha-1,beta-1,gamma-1,CB]
    curr = index_min
    optimal_order=[]
    optimal_schedule=[]
    i = alpha-1
    j = beta -1
    k = gamma-1
    while i!=0 or j!=0 or k!=0:
        if curr == A:
            optimal_order.append(f"A_{i}")
            optimal_schedule.append(round(schedule[i,j,k,curr],3))
            curr = order[i,j,k,curr]
            i-=1
        elif curr == B:
            optimal_order.append(f"B_{j}")
            optimal_schedule.append(round(schedule[i,j,k,curr],3))
            curr = order[i,j,k,curr]
            j-=1
        elif curr == CA:
            optimal_order.append(f"C_{k}")
            optimal_schedule.append(round(schedule[i,j,k,curr],3))
            curr = order[i,j,k,curr]
            k-=1
        elif curr == CB:
            optimal_order.append(f"C_{k}")
            optimal_schedule.append(round(schedule[i,j,k,curr],3))
            curr = order[i,j,k,curr]
            k-=1
    #print(np.around(delay,decimals=4))
    avg_delay = np.round(total_delay/(alpha+beta+gamma-3),3)
    optimal_order.reverse()
    optimal_schedule.reverse()
    last = np.round(last,3)
    return(last,avg_delay,optimal_schedule,optimal_order)
if __name__ == "__main__":
    for i in range(1,6):
        with open(f"temp/test_data_{i}.json" ,"r") as f:
            data=json.load(f)

        Lane_A=data["Lane_A"]
        Lane_B=data["Lane_B"]
        Lane_C=data["Lane_C"]

        Lane_A.insert(0,0)
        Lane_B.insert(0,0)
        Lane_C.insert(0,0)

        W1_same=1
        W1_diff=3
        W2_same=1
        W2_diff=3
        tf_time=3

        last,first_schedule = first_merge_dynamic(W1_same, W1_diff, Lane_A, Lane_B)
        last,avg_delay,schedule,order = second_merge_dynamic(W1_same, W1_diff, W2_same, W2_diff ,tf_time , first_schedule, Lane_A , Lane_B , Lane_C )
        print("last = ",last,"   delay=",avg_delay)
        #print(order)
        #print(schedule)
        json.dump({"last":last,"delay":avg_delay,"schedule": schedule,"order":order}, open(f"temp/dynamic_result_{i}.json", 'w',encoding='utf-8'), indent=2, ensure_ascii=False)

                
