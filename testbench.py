from argparse import ArgumentParser
from poisson import poisson_gen
from dynamic import first_merge_dynamic
from dynamic import second_merge_dynamic
from greedy import greedy
import numpy as np
import csv
import os
import json
parser = ArgumentParser()
parser.add_argument("--output_dir", help="Number of cars in each lane", type=str , default = "temp")
parser.add_argument("--generate", help="Whether to generate data" , action='store_true')
parser.add_argument("--num_cars" ,help="Number of cars in each lane", type=int, default = 30)
parser.add_argument("--W1_same", help="The same lane waiting time for first merging point", type=float, default = 1)
parser.add_argument("--W1_diff",help="The different lane waiting time for first merging point", type=float, default = 3)
parser.add_argument("--W2_same", help="The same lane waiting time for second merging point", type=float, default = 1)
parser.add_argument("--W2_diff",help="The different lane waiting time for second merging point", type=float, default = 3)

args = parser.parse_args()


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, args.output_dir)
os.makedirs(filename, exist_ok=True)
if args.generate:
    for i in range(1,6):
        poisson_1 = poisson_gen(i/10, args.num_cars)
        poisson_2 = poisson_gen(i/10, args.num_cars)
        poisson_3 = poisson_gen(i/10, args.num_cars)
        output_file = os.path.join(args.output_dir, f"test_data_{i}.json")
        json.dump({"Lane_A":poisson_1,"Lane_B":poisson_2,"Lane_C":poisson_3}, open(output_file, 'w',encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f"Generated test data{i}")
    for i in range(20,120,20):
        poisson_1 = poisson_gen(0.5, i)
        poisson_2 = poisson_gen(0.5, i)
        poisson_3 = poisson_gen(0.5, i)
        output_file = os.path.join(args.output_dir, f"mult_data_{i}.json")
        json.dump({"Lane_A":poisson_1,"Lane_B":poisson_2,"Lane_C":poisson_3}, open(output_file, 'w',encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f"Generated mult data{i}")
greedy_lambda_output={}
for i in range(1,6):  
    input_file = os.path.join(args.output_dir, f"test_data_{i}.json")  
    with open(input_file ,"r") as f:
        data=json.load(f)
    Lane_A = data["Lane_A"]
    Lane_B = data["Lane_B"]
    Lane_C = data["Lane_C"]
    Lane_A.append(1e8)
    Lane_B.append(1e8)
    Lane_C.append(1e8)
    last,first_delay,schedule=greedy(Lane_A, Lane_B, args.W1_same, args.W1_diff)
    for j in range(len(schedule)):
        schedule[j]+=3
    schedule.append(1e8)
    last,second_delay,schedule = greedy(Lane_C, schedule, args.W2_same, args.W2_diff)
    total_delay=first_delay+second_delay
    avg_delay=total_delay/(len(Lane_A)+len(Lane_B)+len(Lane_C)-3)
    avg_delay=round(avg_delay,3)
    print(f"First come first go on test data {i} results:")
    print("Last = ",last,"   Delay=",avg_delay)
    print("\n")
    #print("schedule = ", schedule)
    greedy_lambda_output[f"{i}"] = {"Last":last,"Delay":avg_delay}
greedy_w_output={}
for i in np.arange(1,3.2,0.2):
    i = round(i,1) 
    input_file = os.path.join(args.output_dir, f"test_data_5.json")  
    with open(input_file ,"r") as f:
        data=json.load(f)
    Lane_A = data["Lane_A"]
    Lane_B = data["Lane_B"]
    Lane_C = data["Lane_C"]
    Lane_A.append(1e8)
    Lane_B.append(1e8)
    Lane_C.append(1e8)
    last,first_delay,schedule = greedy(Lane_A, Lane_B, i, 3)
    for j in range(len(schedule)):
        schedule[j]+=3
    schedule.append(1e8)
    last,second_delay,schedule = greedy(Lane_C, schedule, i, 3)
    total_delay=first_delay+second_delay
    avg_delay=total_delay/(len(Lane_A)+len(Lane_B)+len(Lane_C)-3)
    avg_delay=round(avg_delay,3)
    greedy_w_output[f"{i}"] = {"Last":last,"Delay":avg_delay}

dp_lambda_output = {}
for i in range(1,6):
    input_file = os.path.join(args.output_dir, f"test_data_{i}.json")  
    with open(input_file ,"r") as f:
        data=json.load(f)
    Lane_A=data["Lane_A"]
    Lane_B=data["Lane_B"]
    Lane_C=data["Lane_C"]

    Lane_A.insert(0,0)
    Lane_B.insert(0,0)
    Lane_C.insert(0,0)
    tf_time=3

    last,first_schedule = first_merge_dynamic(1, 3, Lane_A, Lane_B)
    last,avg_delay,schedule,order = second_merge_dynamic(1, 3, 1, 3 ,tf_time , first_schedule, Lane_A , Lane_B , Lane_C )
    print(f"Dynamic programming on test data {i} results:")
    print("Last = ",last,"   Delay=",avg_delay)
    print("\n")
    dp_lambda_output [f"{i}"] = {"Last":last,"Delay":avg_delay}
dp_w_output = {}
for i in np.arange(1,3.2,0.2):
    i = round(i,1) 
    input_file = os.path.join(args.output_dir, f"test_data_5.json")  
    with open(input_file ,"r") as f:
        data=json.load(f)
    Lane_A = data["Lane_A"]
    Lane_B = data["Lane_B"]
    Lane_C = data["Lane_C"]
    Lane_A.insert(0,0)
    Lane_B.insert(0,0)
    Lane_C.insert(0,0)
    tf_time=3

    last,first_schedule = first_merge_dynamic(i, 3, Lane_A, Lane_B)
    last,avg_delay,schedule,order = second_merge_dynamic(i, 3, i, 3 ,tf_time , first_schedule, Lane_A , Lane_B , Lane_C )
    dp_w_output[f"{i}"] = {"Last":last,"Delay":avg_delay}

greedy_n_output={}
for i in range(20,120,20):  
    input_file = os.path.join(args.output_dir, f"mult_data_{i}.json")  
    with open(input_file ,"r") as f:
        data=json.load(f)
    Lane_A = data["Lane_A"]
    Lane_B = data["Lane_B"]
    Lane_C = data["Lane_C"]
    Lane_A.append(1e8)
    Lane_B.append(1e8)
    Lane_C.append(1e8)
    last,first_delay,schedule=greedy(Lane_A, Lane_B, 1, 3)
    for j in range(len(schedule)):
        schedule[j]+=3
    schedule.append(1e8)
    last,second_delay,schedule = greedy(Lane_C, schedule, 1, 3)
    total_delay=first_delay+second_delay
    avg_delay=total_delay/(len(Lane_A)+len(Lane_B)+len(Lane_C)-3)
    avg_delay=round(avg_delay,3)
    print(f"First come first go on test data {i} results:")
    print("Last = ",last,"   Delay=",avg_delay)
    print("\n")
    #print("schedule = ", schedule)
    greedy_n_output[f"{i}"] = {"Last":last,"Delay":avg_delay}

dp_n_output = {}
for i in range(20,120,20):
    input_file = os.path.join(args.output_dir, f"mult_data_{i}.json")  
    with open(input_file ,"r") as f:
        data=json.load(f)
    Lane_A=data["Lane_A"]
    Lane_B=data["Lane_B"]
    Lane_C=data["Lane_C"]

    Lane_A.insert(0,0)
    Lane_B.insert(0,0)
    Lane_C.insert(0,0)
    tf_time=3

    last,first_schedule = first_merge_dynamic(1, 3, Lane_A, Lane_B)
    last,avg_delay,schedule,order = second_merge_dynamic(1, 3, 1, 3 ,tf_time , first_schedule, Lane_A , Lane_B , Lane_C )
    print(f"Dynamic programming on test data {i} results:")
    print("Last = ",last,"   Delay=",avg_delay)
    print("\n")
    dp_n_output [f"{i}"] = {"Last":last,"Delay":avg_delay}



data_file = open('result.csv', 'w')
csv_writer = csv.writer(data_file)
csv_writer.writerow(("Lambda","First arrive first go","","Dynamic Programming"))
csv_writer.writerow(("","Tlast","","Tdelay"))
for key,value in greedy_lambda_output.items():
    csv_writer.writerow((key,value["Last"],value["Delay"],dp_lambda_output[key]["Last"],dp_lambda_output[key]["Delay"]))
csv_writer.writerow(("W same","First arrive first go","","Dynamic Programming"))
csv_writer.writerow(("","Tlast","","Tdelay"))
for key,value in greedy_w_output.items():
    csv_writer.writerow((key,value["Last"],value["Delay"],dp_w_output[key]["Last"],dp_w_output[key]["Delay"]))
csv_writer.writerow(("N","First arrive first go","","Dynamic Programming"))
csv_writer.writerow(("","Tlast","","Tdelay"))
for key,value in greedy_n_output.items():
    csv_writer.writerow((key,value["Last"],value["Delay"],dp_n_output[key]["Last"],dp_n_output[key]["Delay"]))

