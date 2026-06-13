from vehicle import Loadplanner, ReportGenerator
planner = Loadplanner()
report= planner.run(r"C:\Users\Raghavendra Rao\OneDrive\Music\Shipment-\data\shipment_data.txt")
reporter = (ReportGenerator().summary_text(report))