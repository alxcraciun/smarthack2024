import pandas as pd
from dataclasses import dataclass
from typing import List
from enum import Enum
from pathlib import Path


class NodeType(Enum):
    CUSTOMER = "CUSTOMER"
    REFINERY = "REFINERY"
    TANK = "STORAGE_TANK"


class ConnectionType(Enum):
    PIPELINE = "PIPELINE"
    TRUCK = "TRUCK"


@dataclass
class Customer:
    id: str
    name: str
    max_input: int
    over_input_penalty: float
    late_delivery_penalty: float
    early_delivery_penalty: float
    node_type: NodeType

    def __str__(self) -> str:
        return (f"Customer ID: {self.id}, Name: {self.name}\n"
                f"  Max Input: {self.max_input}\n"
                f"  Penalties (Over/Late/Early): {self.over_input_penalty}/{self.late_delivery_penalty}/{self.early_delivery_penalty}\n"
                f"  Node Type: {self.node_type.value}\n"
                f"---")


@dataclass
class Demand:
    id: str
    customer_id: str
    quantity: int
    post_day: int
    start_delivery_day: int
    end_delivery_day: int

    def __str__(self) -> str:
        return (f"Demand ID: {self.id}\n"
                f"  Customer ID: {self.customer_id}\n"
                f"  Quantity: {self.quantity}\n"
                f"  Post Day: {self.post_day}\n"
                f"  Delivery Window: {self.start_delivery_day} - {self.end_delivery_day}\n"
                f"---")


@dataclass
class Connection:
    id: str
    from_id: str
    to_id: str
    distance: int
    lead_time_days: int
    connection_type: ConnectionType
    max_capacity: int
    costPerDistanceAndVolume: float = 0.0
    co2PerDistanceAndVolume: float = 0.0
    overUsePenaltyPerVolume: float = 0.0

    def __post_init__(self):
        if self.connection_type == ConnectionType.PIPELINE:
            self.costPerDistanceAndVolume = 0.05
            self.co2PerDistanceAndVolume = 0.02
            self.overUsePenaltyPerVolume = 1.13
        elif self.connection_type == ConnectionType.TRUCK:
            self.costPerDistanceAndVolume = 0.42
            self.co2PerDistanceAndVolume = 0.31
            self.overUsePenaltyPerVolume = 0.73

    def __str__(self) -> str:
        return (f"Connection from {self.from_id} to {self.to_id}:\n"
                f"  Connection ID: {self.id}\n"
                f"  Distance: {self.distance}, Lead Time: {self.lead_time_days} days\n"
                f"  Type: {self.connection_type.value}, Max Capacity: {self.max_capacity}\n"
                f"---")


@dataclass
class Refinery:
    id: str
    name: str
    capacity: int
    max_output: int
    production: int
    overflow_penalty: float
    underflow_penalty: float
    over_output_penalty: float
    production_cost: float
    production_co2: float
    initial_stock: int
    node_type: NodeType

    def __str__(self) -> str:
        return (f"Refinery ID: {self.id}, Name: {self.name}\n"
                f"  Capacity: {self.capacity}, Max Output: {self.max_output}\n"
                f"  Production: {self.production}, Initial Stock: {self.initial_stock}\n"
                f"  Penalties (Overflow/Underflow/Over Output): {self.overflow_penalty}/{self.underflow_penalty}/{self.over_output_penalty}\n"
                f"  Production Cost: {self.production_cost}, CO2: {self.production_co2}\n"
                f"  Node Type: {self.node_type.value}\n"
                f"---")


@dataclass
class Tank:
    id: str
    name: str
    capacity: int
    max_input: int
    max_output: int
    overflow_penalty: float
    underflow_penalty: float
    over_input_penalty: float
    over_output_penalty: float
    initial_stock: int
    node_type: NodeType

    def __str__(self) -> str:
        return (f"Tank ID: {self.id}, Name: {self.name}\n"
                f"  Capacity: {self.capacity}\n"
                f"  Max Input/Output: {self.max_input}/{self.max_output}\n"
                f"  Initial Stock: {self.initial_stock}\n"
                f"  Penalties (Overflow/Underflow/Over Input/Over Output): {self.overflow_penalty}/{self.underflow_penalty}/{self.over_input_penalty}/{self.over_output_penalty}\n"
                f"  Node Type: {self.node_type.value}\n"
                f"---")


class DataLoader:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = Path(data_folder)

    def load_customers(self) -> List[Customer]:
        df = pd.read_csv(self.data_folder / "customers.csv", sep=";")
        return [Customer(
            id=str(row.id),
            name=str(row.name),
            max_input=int(row.max_input),
            over_input_penalty=float(row.over_input_penalty),
            late_delivery_penalty=float(row.late_delivery_penalty),
            early_delivery_penalty=float(row.early_delivery_penalty),
            node_type=NodeType(row.node_type)
        ) for _, row in df.iterrows()]

    # def load_demands(self) -> List[Demand]:
    #     df = pd.read_csv(self.data_folder / "demands.csv", sep=";")
    #     return [Demand(
    #         id=str(row.id),
    #         customer_id=str(row.customer_id),
    #         quantity=int(row.quantity),
    #         post_day=int(row.post_day),
    #         start_delivery_day=int(row.start_delivery_day),
    #         end_delivery_day=int(row.end_delivery_day)
    #     ) for _, row in df.iterrows()]

    def load_connections(self) -> dict:
        df = pd.read_csv(self.data_folder / "connections.csv", sep=";")
        return {
            (str(row.from_id), str(row.to_id), str(ConnectionType(row.connection_type))): Connection(
                id=str(row.id),
                from_id=str(row.from_id),
                to_id=str(row.to_id),
                distance=int(row.distance),
                lead_time_days=int(row.lead_time_days),
                connection_type=ConnectionType(row.connection_type),
                max_capacity=int(row.max_capacity)
            )
            for _, row in df.iterrows()
        }

    def load_refineries(self) -> List[Refinery]:
        df = pd.read_csv(self.data_folder / "refineries.csv", sep=";")
        return [Refinery(
            id=str(row.id),
            name=str(row.name),
            capacity=int(row.capacity),
            max_output=int(row.max_output),
            production=int(row.production),
            overflow_penalty=float(row.overflow_penalty),
            underflow_penalty=float(row.underflow_penalty),
            over_output_penalty=float(row.over_output_penalty),
            production_cost=float(row.production_cost),
            production_co2=float(row.production_co2),
            initial_stock=int(row.initial_stock),
            node_type=NodeType(row.node_type)
        ) for _, row in df.iterrows()]

    def load_tanks(self) -> List[Tank]:
        df = pd.read_csv(self.data_folder / "tanks.csv", sep=";")
        return [Tank(
            id=str(row.id),
            name=str(row.name),
            capacity=int(row.capacity),
            max_input=int(row.max_input),
            max_output=int(row.max_output),
            overflow_penalty=float(row.overflow_penalty),
            underflow_penalty=float(row.underflow_penalty),
            over_input_penalty=float(row.over_input_penalty),
            over_output_penalty=float(row.over_output_penalty),
            initial_stock=int(row.initial_stock),
            node_type=NodeType(row.node_type)
        ) for _, row in df.iterrows()]


if __name__ == "__main__":
    loader = DataLoader()
    try:
        customers = loader.load_customers()
        # demands = loader.load_demands()
        connections = loader.load_connections()
        refineries = loader.load_refineries()
        tanks = loader.load_tanks()

        print("\n=== Customers ===")
        print(f"Total customers: {len(customers)}")
        for customer in customers:
            print(customer)

        # print("\n=== Demands ===")
        # print(f"Total demands: {len(demands)}")
        # for demand in demands:
        #     print(demand)

        print("\n=== Connections ===")
        print(f"Total connections: {len(connections)}")
        for conn in connections.values():
            print(conn)

        print("\n=== Refineries ===")
        print(f"Total refineries: {len(refineries)}")
        for refinery in refineries:
            print(refinery)

        print("\n=== Tanks ===")
        print(f"Total tanks: {len(tanks)}")
        for tank in tanks:
            print(tank)

    except FileNotFoundError as e:
        print(f"Error: Could not find CSV file - {e}")
    except Exception as e:
        print(f"Error loading data: {e}")
