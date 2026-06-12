import os
import re
from datetime import datetime
#Data
vaild_city = {"mumbai", "delhi", "banglour", "hyderabad", "chennai", "pune"}
FLEET = [
        ("Bike", 0.5, 50, 20),
        ("Van", 8.0, 1000, 15),
        ("Truck", 35.0, 5000, 10),
        ("Trailer", 70.0, 12000, 8),
        ("Container", 120.0, 25000, 5),     
    ]
#shipment details 
class Shipment:
    def __init__(self, shipment_id, destination, volume, weight, priority, timestamp):
        self.shipment_id = shipment_id
        self.destination = destination
        self.volume = volume
        self.weight = weight
        self.priority = priority
        self.timestamp = timestamp
        self.reason =""
#vehicle imformeation
class Vehicle:
    def __init__(self, vehicle_id, vehicle_type, capacity_volume, capacity_weight, destination):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.capacity_volume = capacity_volume
        self.capacity_weight = capacity_weight
        self.destination = destination
        self.shipment = []
        self.loaded_volume = 0.0
        self.loaded_weight = 0.0
        self.status = "open"
    def can_fit(self, shipment):
        return (self.loaded_volume + shipment.volume <= self.capacity_volume and self.loaded_weight + shipment.weight <= self.capacity_weight)
    def add_shipment(self, shipment):
        self.shipment.append(shipment)
        self.loaded_volume += shipment.volume
        self.loaded_weight += shipment.weight
    def utilization(self):
        if self.capacity_volume == 0:
            return 0.0
        return(self.loaded_volume/ self.capacity_volume) * 100.0
#planning of loads 
class Loadplanner:
    def __init__(self):
        self.vaild_shipments =[]
        self.invaild_records =[]
        self.pending_shipment = []
        self.dispatch_manifest =[]
        self.seen_ids = set() 
    def _parse_float(self, value):
        return float(value.strip())
    def validate_process(self, process):
        process = process.strip()
        if not process:
            return None, "Eampty_process"
        parts = process.strip("|")
        if len(parts) != 6:
            return None, "Invalid record found"
        shipment_id, raw_city, raw_volume, raw_weight, priority,timestamp = [r.strip() for r in parts]
        if not shipment_id or not raw_city or not raw_volume or not raw_weight or not priority or not timestamp:
            return None,  "Missing required fields"
        if shipment_id in self.seen_ids:
            return None, "Duplicate shipment_id"
        city = raw_city.lower()
        if city not in self.vaild_citys:
            return None, "Invaild_city"
        try:
            volume = self._parse_float(raw_volume)
        except:
            return None, "information is not vaild"
        try:
            weight = self._parse_float(raw_weight)
        except:
            return None, "Information is not vaild"
        if volume <= 0:
            return None, "Invalid volume value"
        if weight <= 0:
            return None, "Invalid weight value"
        try:
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
        except:
            return None, "timestamp wrong"
        self.seen_ids.add(shipment_id)
        shipment = Shipment(shipment_id, city, volume, weight, priority, timestamp)
        return shipment, None
    def parse_file(self, path_of_file):
        self.valid_shipments = []
        self.invalid_records =[]
        self.pending_shipments = []
        self.dispatch_manifest =[]
        self.seen_ids =set()
        with open(path_of_file, "r", encoding="utf-8") as f:
            process = f.readlines()
        for idx, process in enumerate(process):
            if idx == 0 and "ShipmentID" in process:
                continue
            Shipment, reason = self.validate_process(process)
            if Shipment:
                self.vaild_shipments.append(Shipment)
            else:
                if process.strip():
                    self.invaild_records.append({"record":process.strip(), "reason": reason})
                else:
                    self.invalid_records.append({"record": "", "reason": reason})
    def _vehicle_prefix(self, vehicle_type):
        return {
            "Bike": "BIKE",
            "Van":"VAN",
            "Truck":"TRUCK",
            "Trailer":"TRAILER",
            "Container":"CONTAINER"
        }[vehicle_type]
    def _large_vehicle(self, shipment):
        for vehicle_type, volume_cp, weight_cp, _ in reversed(self.FLEET):
            if shipment.volume <= volume_cp and shipment.weight <= weight_cp:
                return vehicle_type, volume_cp, weight_cp
            return None
    def _open_vehicles(self , distination, shipment):
        vehicle_type_data = self._large_vehicle(shipment)
        if not vehicle_type_data:
            shipment.reason =" reached max no of vehicle"
            self.pending_shipments.append(shipment)
            return None
        vehicle_type, vl_cp, wt_cp = vehicle_type_data
        count = sum(1 for v in self.dispatch_manifest + [ ] if v.vehicle_type == vehicle_type and v.distination == distination) + \
            sum(1 for v in getattr(self, "_open_vehicles",[]) if v.vehicle_type  == vehicle_type and v.distination == distination) +1
        vehicle_id = f"{self._vehicle_prefix(vehicle_type)}-{count:03d}"
        vehicle = Vehicle(vehicle_id, vehicle_type, vl_cp, wt_cp, distination)
        vehicle.add_shipment(Shipment)
        return vehicle
    def load_plans(self):
        self.dispatch_manifest =[]
        self.pending_shipments =[]
        groups = {}
        for s in self.valid_shipments:
            groups.setdefault(s.destination, []).append(s)
        self._open_vehicles = []
        for destination, shipments in groups.items():
            Shipment = sorted(shipments, key=lambda x: x.volume, reverse=True)
            open_vehicles = []
            for shipment in shipments:
                placed = False
                for vehicle in open_vehicles:
                    if vehicle.can_fit(shipment):
                        vehicle.add_shipment(shipment)
                        placed = True
                        break
                    if not placed:
                       Vehicle = self._open_vehicle(destination, shipment)
                    if Vehicle:
                        open_vehicles.append(Vehicle)
                        placed = True  
                    if not placed:
                        if not Shipment.reason:
                            shipment.reason = "No available vehicle"
                        self.pending_shipments.append(shipment)
            for vehicle in open_vehicles:
                util = vehicle.utilization()
                if 92.0 <= util <= 100.0:
                    vehicle.status = "Dispatch"
                    self.dispatch_manifest.append(vehicle)
                else:
                    vehicle.status = "Rejected"
                    for sh in vehicle.shipment:
                        sh.reason = "Vehicle fully loaded"
                        self.Pending_shipments.append(sh) 
    def run(self, path_of_file):
        self.parse_file(path_of_file)
        self.load_plans()
        return {
            "valid_records": len(self.valid_shipments),
            "invalid_records": len(self.invalid_records),
            "dispatched_vehicles": len(self.dispatch_manifest),
            "pending": len(self.pending_shipments),
            "dispatch_manifest": self.dispatch_manifest,
            "pending_shipments": self.pending_shipments,
            "rejections": self.invalid_records
        }
class ReportGenerator:
    def summary_text(self, result):
        process = []
        process.append("===Dispatched item=======")
        for v in result["dispatch_manifest"]:
            process.append(f"Vehicle: {v.vehicle_id} | Type: {v.vehicle_type} | Destination: {v.destination.title()} |" f"Utilization: {v.utilization():.2f}% | Shipment count: {len(v.shipments)}")
        process.append("===Pending shipments=====")
        for s in result["pending_shipments"]:
            process.append(f"Shipment ID: {s.shipment_id}, Reason: {s.reason}")
        process.append("===summary===")
        process.append(f"valid records: {result['valid_records']} | Invalid records: {result['invalid_records']} | " f"Dispatched vehicles: {result['dispatched_vehicles']} | Pending shipments: {result['pending_shipments']}")
        return "\n".join(process) 