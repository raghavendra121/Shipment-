from vehicle import Loadplanner, ReportGenerator
planner = Loadplanner()
report= planner.run(r"C:\Users\Raghavendra Rao\OneDrive\Music\project_bike\shipment_data.txt")
reporter = (ReportGenerator().summary_text(report))