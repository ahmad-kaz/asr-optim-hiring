from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Instance:
    machine_num: int
    budget: int
    day_num: int
    availability: Dict[int, int]
    price: Dict[int, int]
    resell: Dict[int, int]
    profit: Dict[int, int]
    day_availability: Dict[int, List[int]]
    stages: List[int]
    new_machines_days: List[int]
    best: int
    
def read_one_instance(f, m: int, b: int, d: int) -> Instance:
    #this method reads the info of one instance
    availability, price, resell, profit = {}, {}, {}, {}
    day_availability = {}
    st = [d+1]
    new_machines_days = []
    for i in range(m):
        a, p, r, t = map(int, f.readline().split(" "))
        availability[i] = a
        price[i] = p
        resell[i] = r
        profit[i] = t
        if a in day_availability:
            day_availability[a].append(i)
        else:
            day_availability[a] = [i]
        st.append(a)
        st.append(a+1)
        new_machines_days.append(a)
    return Instance(machine_num = m,
                    budget = b,
                    day_num = d,
                    availability = availability,
                    price = price, 
                    resell = resell,
                    profit = profit,
                    day_availability =day_availability,
                    stages = sorted(list(set(st))),
                    new_machines_days = list(set(new_machines_days)),
                    best = 0)

def create_dataset_from_disk(data_dir: str) -> List[Instance]:
    #this method reads all instances from disk
    ins = []
    f = open(data_dir, "r")
    m, b, d = map(int, f.readline().split(" "))
    while(True):
        ins.append(read_one_instance(f, m, b, d))
        m, b, d = map(int, f.readline().split(" "))
        if (m==0 and b==0 and d==0):
            f.close()
            break
    return ins
    
def action_buy_machine(ins: Instance, state: Tuple[str, int, int, int], m: int) -> Tuple[str, int, int, int]:
    #return the state (and stage) after buying: betta function (please see the report for definition)
    value = state[1]
    machine = state[2]
    d = state[3]
    if machine != -1:
        return ("r", value, machine, d+1)
    if m==-1:
        return ("r", value, -1, d+1)   
    if ins.price[m] <= value:
        return ("r", value-ins.price[m], m, d+1)
    else:
        return ("r", value, -1, d+1)

def action_resell_machine(ins: Instance, state: Tuple[str, int, int, int], m: int) -> Tuple[str, int, int, int]:
    #return the state (and stage) after reselling: betta function (please see the report for definition)
    value = state[1]
    machine = state[2]
    d = state[3]
    if (ins.stages[d]==ins.day_num+1):
        if machine==-1:
            return value
        else:
            return value+ins.resell[machine]
    else:
        if machine==-1:
            return ("b", value, -1, d)
        if m!=-1:
            return ("b", value+ins.resell[m], -1, d)
        return("b", value+ins.profit[machine]*(ins.stages[d+1]-ins.stages[d]), machine, d)
    
def get_max(ins: Instance, state: Tuple[str, int, int, int]) -> int:
    #the recursive function
    current_action = state[0]
    value = state[1]
    machine = state[2]
    d = state[3]
    if ins.stages[d]==ins.day_num+1:
        v = action_resell_machine(ins, ("r", value, machine, d), machine)
        if v > ins.best:
            ins.best = v
        return v
    if current_action == "r":
        #possible actions: alpha function when staage is reslling
        action_1 = action_resell_machine(ins, ("r", value, machine, d), -1) #do nothing 
        v1 = get_max(ins, action_1)
        action_2 = action_resell_machine(ins, ("r", value, machine, d), machine) #sell the machine
        v2 = get_max(ins, action_2)
        return max(v1, v2)
    if current_action == "b":
        #possible actions: alpha function when stage is buying
        if ins.stages[d] not in ins.new_machines_days:
            v = get_max(ins, ("r", value, machine, d+1))
            return v
        max_values = []   
        for m in ins.day_availability[ins.stages[d]]:
            action_1 = action_buy_machine(ins, ("b", value, machine, d), -1)#do nothing
            v1 = get_max(ins, action_1)
            action_2 = action_buy_machine(ins, ("b", value, machine, d), m)#buy the machine
            v2 = get_max(ins, action_2)
            max_values.append(max(v1, v2))
        return max(max_values)
    
def DP(ins: Instance):
    if ins.machine_num == 0 or ins.budget < min(ins.price.values()) or ins.day_num == 0:
        return 0
    #initial state: (resell/buy, value, machine, d)
    #machine = -1 means no machine in hand
    stage = ("b", ins.budget, -1, 0)
    get_max(ins, stage)

def solve_instances(instance_list: List[Instance]):
    #iterate over instances list to optimise each
    for i in range(len(instance_list)):
        DP(instance_list[i])
        print("Case {0}: {1}".format(i+1, instance_list[i].best))

if __name__ == "__main__":    
    #read the input data for all instances
    data_dir = "instance.txt"
    instance_list = create_dataset_from_disk(data_dir)
    #solve the all instances
    solve_instances(instance_list)