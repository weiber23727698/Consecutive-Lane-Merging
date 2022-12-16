import json
def greedy(Lane_A=[],Lane_B=[], W_same = 1, W_diff = 3):
    i=0
    j=0
    time=-10
    delay=0
    schedule=[]
    if Lane_A[0]<=Lane_B[0] :
        lane=0
    else :
        lane=1
    while i<len(Lane_A)-1 or j<len(Lane_B)-1 :
        if Lane_A[i]<=Lane_B[j] :
            if lane == 0:
                time+=W_same
            else: 
                time+=W_diff
            arrival=Lane_A[i]
            if time<arrival:
                time = arrival
            delay+=time-arrival
            lane = 0
            i += 1
        elif Lane_A[i]>Lane_B[j] :
            if lane == 1:
                time+=W_same
            else: 
                time+=W_diff
            arrival=Lane_B[j]
            if time<arrival:
                time = arrival
            delay+=time-arrival
            lane = 1
            j += 1
        schedule.append(round(time,4))
    delay=round(delay,4)
    time=round(time,4)
    return(time,delay,schedule)

if __name__=="__main__":
    for i in range(1,6):
        with open(f"temp/test_data_{i}.json" ,"r") as f:
            data=json.load(f)
        Lane_A=data["Lane_A"]
        Lane_B=data["Lane_B"]
        Lane_C=data["Lane_C"]
        Lane_A.append(1e8)
        Lane_B.append(1e8)
        Lane_C.append(1e8)
        W_same=1

        W_diff=3

        last,first_delay,schedule=greedy(Lane_A,Lane_B,W_same,W_diff)
        for j in range(len(schedule)):
            schedule[j]+=3
        schedule.append(1e8)
        last,second_delay,schedule = greedy(Lane_C,schedule, W_same, W_diff)
        total_delay=first_delay+second_delay
        avg_delay=total_delay/(len(Lane_A)+len(Lane_B)+len(Lane_C)-3)
        avg_delay=round(avg_delay,3)
        print("last = ",last,"   delay=",avg_delay)
        #print("schedule = ", schedule)
        json.dump({"last":last,"delay":avg_delay,"schedule": schedule}, open(f"temp/greedy_result_{i}.json", 'w',encoding='utf-8'), indent=2, ensure_ascii=False)
