# Aici faci tu Stefan structura de date
import copy

from data import DataLoader


class Action:
    def __init__(self, pipe, cantitate):
        self.pipe = pipe
        self.cantitate = cantitate

    def Valid(self):
        return self.cantitate > 0


# Clasa de actiuni efectuate in fiecare zi
class Actions:
    def __init__(self):
        self.liste = [[] for _ in range(43)]

    def adauga(self, action,zi):
        self.liste[zi].append(action)

    def obtine_zi(self, zi):
        return self.liste[zi]


def prelucrare_date():
    data = DataLoader()
    customers = data.load_customers()



# Clasa singleton care contine toate trasele client<->rafinarie
class Rute(object):
    instance = None

    def __init__(self):
        self.drumuri = {}
        self.__calculeaza()

    def cauta_drumuri(self, from_id, drum_curent, vizitat, connections):
        stack = [(from_id, drum_curent[:])]

        while stack:
            current_id, current_path = stack.pop()
            if current_id in vizitat:
                continue

            vizitat.add(current_id)

            # Adăugăm drumul curent pentru clienți
            if current_id in drumuri:
                self.drumuri[current_id].append(copy.deepcopy(current_path))

            for (src, dest, connection_type), conn in connections.items():
                if src == current_id and dest not in vizitat:
                    current_path.append(conn)
                    stack.append((dest, copy.deepcopy(current_path)))
                    current_path.pop()  # backtrack

            vizitat.remove(current_id)

    def __calculeaza(self):
        data = DataLoader()
        connections = data.load_connections()
        customers = data.load_customers()
        refineries = data.load_refineries()

        self.drumuri = {customer.id: [] for customer in customers}

        for refinery in refineries:
            self.cauta_drumuri(refinery.id, [], set(), connections)

    def __new__(cls):
        if not cls.instance:
            cls.instance = super(Rute, cls).__new__(cls)
        return cls.instance

    # def get_drumuri(self,customer):
    #     self.__calculeaza(customer)
    #     return self.drumuri


class Configuratie(object):
    instance = None

    def __conf(self):
        obj = dict()
        obj["connections"] = DataLoader.load_connections()
        obj["tanks"] = DataLoader.load_tanks()
        obj["customers"] = DataLoader.load_customers()
        obj["refineries"] = DataLoader.load_refineries()
        self.conf = [obj for _ in range(43)]
    def get_conf(self):
        return self.conf

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configuratie, cls).__new__(cls)
        return cls.instance


# Calculeaza capacitatea si distanta legala din drumul din parametru
def cap_drum_legal(drum,zi,start,end,penalty_early_client,penalty_late_client):
    distance = 0
    ziSosire = zi
    capacityRef = Configuratie().get_conf()[zi]["refineries"][drum[0]].max_capacity
    maxOutRef = Configuratie().get_conf()[zi]["refineries"][drum[0]].max_output
    capacity = min(capacityRef, maxOutRef)
    anterior = drum[0]
    for node in drum[1:]:
        distancePipe = int('inf')
        capacityPipe = int('inf')
        capacityTruck = int('inf')
        distanceTruck = int('inf')
        if (anterior, node, 'pipeline') in Configuratie().get_conf()[zi]["connections"].keys():
            connectionPipe = Configuratie().get_conf()[zi]["connections"][(anterior, node, 'pipeline')]
            distancePipe = connectionPipe.distance
            capacityPipe = connectionPipe.max_capacity
        if (anterior, node, 'truck') in Configuratie().get_conf()[zi]["connections"].keys():
            connectionTruck = Configuratie().get_conf()[zi]["connections"][(anterior, node, 'truck')]
            capacityTruck = connectionTruck.max_capacity
            distanceTruck = connectionTruck.distance
        if distancePipe* (0.05+ 0.02) < distanceTruck*(0.42+0.31):
            minimDistance = 'pipe'
        else:
            minimDistance = 'truck'
        capacity += min(capacityPipe, capacityTruck)
        if minimDistance == 'pipe':
            distance += distancePipe
            ziSosire += connectionPipe.lead_time_days
        else:
            distance += distanceTruck
            ziSosire += connectionTruck.lead_time_days
        if node != drum[-1]:
            capacityTank = Configuratie().get_conf()[zi]["tanks"][node].max_capacity
            maxInputTank = Configuratie().get_conf()[zi]["tanks"][node].max_input
            maxOutputTank = Configuratie().get_conf()[zi]["tanks"][node].max_output
            capacity = min(capacityTank, maxInputTank, maxOutputTank,capacity)
        else:
            maxInputCustormer = Configuratie().get_conf()[zi]["customers"][node].max_input
            capacity = min(maxInputCustormer, capacity)
        anterior = node
        penalty = 0
        if ziSosire < start:
            penalty = capacity * (start - ziSosire) * penalty_early_client
        if ziSosire > end:
            penalty = capacity * (ziSosire - end) * penalty_late_client
    return (capacity, distance + penalty, drum,zi)



def cap_drum_illegal(drum,zi,start,end,penalty_early_client,penalty_late_client,cnt):
    distance = 0
    penalty = 0
    ziSosire = zi

    penaltyRefOverflow = Configuratie().get_conf()[zi]["refineries"][drum[0]].overflow_penalty
    penaltyRefOverOutput = Configuratie().get_conf()[zi]["refineries"][drum[0]].over_output_penalty
    maximumRefCapacity = Configuratie().get_conf()[zi]["refineries"][drum[0]].max_capacity
    maximumRefOutput = Configuratie().get_conf()[zi]["refineries"][drum[0]].max_output

    if cnt > maximumRefCapacity:
        penalty += (cnt-maximumRefCapacity)*penaltyRefOverflow
    if cnt > maximumRefOutput:
        penalty += (cnt-maximumRefOutput)*penaltyRefOverOutput
    anterior = drum[0]

    for node in drum[1:]:
        distancePipe = int('inf')
        distanceTruck = int('inf')
        if (anterior, node, 'pipeline') in Configuratie().get_conf()[zi]["connections"].keys():
            connectionPipe = Configuratie().get_conf()[zi]["connections"][(anterior, node, 'pipeline')]
            distancePipe = connectionPipe.distance
            capacityPipe = connectionPipe.max_capacity
        if (anterior, node, 'truck') in Configuratie().get_conf()[zi]["connections"].keys():
            connectionTruck = Configuratie().get_conf()[zi]["connections"][(anterior, node, 'truck')]
            capacityTruck = connectionTruck.max_capacity
            distanceTruck = connectionTruck.distance
        if distancePipe * (0.05 + 0.02) < distanceTruck * (0.42 + 0.31):
            minimCapacity = 'pipe'
        else:
            minimCapacity = 'truck'
        if minimCapacity == 'pipe':
            distance += distancePipe
            ziSosire += connectionPipe.lead_time_days
            penalty += (cnt-capacityPipe)*1.13
        else:
            distance += distanceTruck
            ziSosire += connectionTruck.lead_time_days
            penalty += (cnt-capacityTruck)*0.73
        if node != drum[-1]:
            capacityTank = Configuratie().get_conf()[zi]["tanks"][node].max_capacity
            maxInputTank = Configuratie().get_conf()[zi]["tanks"][node].max_input
            maxOutputTank = Configuratie().get_conf()[zi]["tanks"][node].max_output
            if cnt > capacityTank:
                penalty += (cnt-capacityTank)*Configuratie().get_conf()[zi]["tanks"][node].overflow_penalty
            if cnt > maxInputTank:
                penalty += (cnt-maxInputTank)*Configuratie().get_conf()[zi]["tanks"][node].over_input_penalty
            if cnt > maxOutputTank:
                penalty += (cnt-maxOutputTank)*Configuratie().get_conf()[zi]["tanks"][node].over_output_penalty
        else:
            maxInputCustormer = Configuratie().get_conf()[zi]["customers"][node].max_input
            if cnt > maxInputCustormer:
                penalty += (cnt-maxInputCustormer)*Configuratie().get_conf()[zi]["customers"][node].over_input_penalty
        anterior = node
        if ziSosire < start:
            penalty = cnt * (start - ziSosire) * penalty_early_client
        if ziSosire > end:
            penalty = cnt * (ziSosire - end) * penalty_late_client
    return (cnt, distance + penalty,drum,zi)

def useY(capacity, cost, drum, zi_start):
    zi = zi_start
    Configuratie().get_conf()[zi_start]["refineries"][drum[0]].max_capacity -= capacity
    anterior = drum[0]
    for node in drum[1:]:

        if (anterior, node, 'pipeline') in Configuratie().get_conf()[zi]["connections"].keys():
            connectionPipe = Configuratie().get_conf()[zi]["connections"][(anterior, node, 'pipeline')]
            distancePipe = connectionPipe.distance
            capacityPipe = connectionPipe.max_capacity
        if (anterior, node, 'truck') in Configuratie().get_conf()[zi]["connections"].keys():
            connectionTruck = Configuratie().get_conf()[zi]["connections"][(anterior, node, 'truck')]
            capacityTruck = connectionTruck.max_capacity
            distanceTruck = connectionTruck.distance
        if distancePipe * (0.05 + 0.02) < distanceTruck * (0.42 + 0.31):
            actions.adauga(Action(Configuratie().get_conf()[zi+i]["connections"][(anterior, node, 'pipe')].id,capacity), zi)
            for i in range(connectionPipe.lead_time_days):
                Configuratie().get_conf()[zi+i]["connections"][(anterior, node, 'pipe')].max_capacity -= capacity
            zi += connectionPipe.lead_time_days
            if node != drum[-1]:
                Configuratie().get_conf()[zi]["tanks"][node].max_capacity -= capacity
            else:
                Configuratie().get_conf()[zi]["customers"][node].max_capacity -= capacity

        else:
            for i in range(connectionTruck.lead_time_days):
                Configuratie().get_conf()[zi+i]["connections"][(anterior, node, 'truck')].max_capacity -= capacity
            zi += connectionTruck.lead_time_days
            if node != drum[-1]:
                Configuratie().get_conf()[zi]["tanks"][node].max_capacity -= capacity
            else:
                Configuratie().get_conf()[zi]["customers"][node].max_capacity -= capacity



actions = Actions()
def day(zi, events):
    events.sort(key=lambda x: x[-1])
    for event in events:
        customer = event[0]
        cnt = event[1]
        start = event[3]
        end = event[4]
        penalty_early_client = Configuratie().get_conf()[0]["customers"][customer].early_delivery_penalty
        penalty_late_client = Configuratie().get_conf()[0]["customers"][customer].late_delivery_penalty
        while cnt > 0:
            Y=[]
            for drum in Rute().get_drumuri(customer):
                for i in range(zi+1,43):
                    Y.append(cap_drum_legal(drum,i,start,end,penalty_early_client,penalty_late_client))
                    Y.append(cap_drum_illegal(drum,i,start,end,penalty_early_client,penalty_late_client,cnt))
            minimY = min(Y,key=lambda x: (x[0]/x[1]))
            useY(*minimY)
            cnt -= minimY[0]
    return actions.obtine_zi(zi+1)




# Creează instanța singleton și afișează drumurile
rute_instance = Rute()
drumuri = rute_instance.drumuri

# Afișează drumurile de la rafinării la fiecare client
print("Drumurile de la rafinării la fiecare client:")
for client_id, trasee in drumuri.items():
    print(f"Client {client_id}: Trasee - {trasee}")

