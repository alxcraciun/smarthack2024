from data import DataLoader
from calls import GameAPIClient
from collections import defaultdict
from queue import PriorityQueue
import json


class DailySummary:
    def __init__(self, day, migrations, response):
        self.day = day
        self.migrations_count = len(migrations)
        self.demands_count = len(response.get('demand', []))
        self.daily_cost = response['deltaKpis']['cost']
        self.daily_co2 = response['deltaKpis']['co2']
        self.total_cost = response['totalKpis']['cost']
        self.total_co2 = response['totalKpis']['co2']

        # Store as JSON for potential later use
        self.summary = {
            "day": day,
            "migrations": {
                "count": self.migrations_count
            },
            "demands": {
                "count": self.demands_count
            },
            "kpis": {
                "daily": {
                    "cost": round(self.daily_cost, 2),
                    "co2": round(self.daily_co2, 2)
                },
                "total": {
                    "cost": round(self.total_cost, 2),
                    "co2": round(self.total_co2, 2)
                }
            }
        }

    def __str__(self):
        return (
            f"\nDay {self.day}:\n"
            f"Migrations sent: {self.migrations_count}\n"
            f"New demands received: {self.demands_count}\n"
            f"Daily KPIs - Cost: {self.daily_cost:.2f}, CO2: {self.daily_co2:.2f}\n"
            f"Total KPIs - Cost: {self.total_cost:.2f}, CO2: {self.total_co2:.2f}"
        )

    def __repr__(self):
        return self.__str__()


class GameSimulator:
    def __init__(self):
        self.loader = DataLoader()
        self.client = GameAPIClient()
        self.setup_data()
        self.logger = []

    def setup_data(self):
        self.customers = {c.id: c for c in self.loader.load_customers()}
        self.refineries = {r.id: r for r in self.loader.load_refineries()}
        self.tanks = {t.id: t for t in self.loader.load_tanks()}
        self.connections = self.loader.load_connections()
        self.inventory = defaultdict(int)

        # Initialize inventory
        for r in self.refineries.values():
            self.inventory[r.id] = r.initial_stock
        for t in self.tanks.values():
            self.inventory[t.id] = t.initial_stock

        self.active_demands = []

    def compute_migrations(self, day: int, new_demands: list) -> list:
        migrations = []

        # Add new demands to active demands list
        self.active_demands.extend(new_demands)

        # Sort demands by urgency (closest deadline first)
        # TODO nu stiu de ce, am comentat linia asta si a dat un pic mai bine scorul
        self.active_demands.sort(key=lambda x: x['endDay'])

        # 1. First, handle moving product from refineries to tanks
        # TODO oare daca exista tankuri fara conexiune la vreo rafinarie, o sa ramana goale?
        for refinery_id, refinery in self.refineries.items():
            if self.inventory[refinery_id] <= 0:
                continue

            for tank_id, tank in self.tanks.items():
                if self.inventory[tank_id] >= tank.capacity * 0.5:
                    continue

                connection_key = (refinery_id, tank_id, "ConnectionType.PIPELINE")
                if connection_key not in self.connections:
                    continue

                connection = self.connections[connection_key]

                available = min(
                    self.inventory[refinery_id],
                    refinery.max_output,
                    connection.max_capacity,
                    tank.capacity - self.inventory[tank_id]
                )

                if available > 0:
                    migrations.append({
                        "from_id": refinery_id,
                        "to_id": tank_id,
                        "amount": int(available),
                        "connection_type": "PIPELINE"
                    })
                    self.inventory[refinery_id] -= available

        # 2. Then handle customer demands
        for demand in self.active_demands[:]:
            customer_id = demand['customerId']
            amount_needed = demand['amount']

            # TODO hmm, nu stiu
            if day < demand['startDay']:
                continue
            # TODO idee de optimizare: luat tankurile care au conexiune de cost minim
            tank_pq = PriorityQueue()
            for tank_id, tank in self.tanks.items():
                if self.inventory[tank_id] <= 0:
                    continue

                connection_key = (tank_id, customer_id, "ConnectionType.TRUCK")
                if connection_key not in self.connections:
                    continue

                connection = self.connections[connection_key]

                delivery_time = day + connection.lead_time_days
                # TODO oare sa tratam cazul cand niciun tank nu poate trimite la timp?
                if delivery_time > demand['endDay']:
                    continue

                available = min(
                    self.inventory[tank_id],
                    connection.max_capacity,
                    amount_needed,
                    self.customers[customer_id].max_input
                )
                if available > 0:
                    tank_pq.put((-available / connection.distance, (tank_id, available)))
                    # migrations.append({
                    #     "from_id": tank_id,
                    #     "to_id": customer_id,
                    #     "amount": int(available),
                    #     "connection_type": "TRUCK"
                    # })
                    # self.inventory[tank_id] -= available
                    # amount_needed -= available
                    # if amount_needed <= 0:
                    #     self.active_demands.remove(demand)
                    #     break
            while not tank_pq.empty():
                factor, (tank_id, available) = tank_pq.get()
                # print(factor)
                if available > amount_needed:
                    available = amount_needed
                migrations.append({
                    "from_id": tank_id,
                    "to_id": customer_id,
                    "amount": int(available),
                    "connection_type": "TRUCK"
                })
                self.inventory[tank_id] -= available
                amount_needed -= available
                if amount_needed <= 0:
                    self.active_demands.remove(demand)
                    break
            if amount_needed > 0:
                updated_demand = demand
                updated_demand["amount"] = amount_needed
                self.active_demands.remove(demand)
                self.active_demands.append(updated_demand)
        return migrations

    def run(self):
        print("Starting game simulation")

        session_id = self.client.start_session()
        if not session_id:
            print("Failed to start session")
            return

        try:
            new_demands = []
            for day in range(43):
                # Update refinery inventory with daily production
                for refinery in self.refineries.values():
                    self.inventory[refinery.id] += refinery.production

                # Compute migrations for the day
                migrations = []
                if day > 0:  # On day 0, we just observe
                    migrations = self.compute_migrations(day, new_demands)

                # Send migrations and get response
                response = self.client.play_round(day=day, movements=migrations)

                if not response:
                    print(f"Failed to get response for day {day}")
                    continue

                daily_summary = DailySummary(day, migrations, response)
                print(daily_summary)
                self.logger.append(daily_summary)

                # Update active demands and add new ones
                new_demands = response.get('demand', [])
                # TODO nu stiu daca ar trebui sa aruncam demand-urile intarziate - Paul. Am rulat si fara, dar nu e diferenta de scor
                self.active_demands = [d for d in self.active_demands if d['endDay'] >= day]

        finally:
            self.client.end_session()
            print("\nGame simulation completed")

        return self.logger


def main():
    simulator = GameSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
