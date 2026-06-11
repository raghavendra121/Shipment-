import streamlit as st
import tempfile 
import os
from vehicle import Loadplanner, ReportGenerator
#code start
st.set_page_config(page_title="Smart load planning", layout="wide")
st.title("Smart load planning and optimization dashboard")
upload = st.file_uploader("Upload Shipment data file", type=["log", "txt"])
if upload is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        tmp.write(upload.read())
        tmp_path = tmp.name
    planner = Loadplanner()
    report = planner.run(tmp_path)
    reporter = ReportGenerator()
    st.subheader("Summary")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Valid Records", report["valid_records"])
    a2.metric("Invalid Records", report["invalid_records"])
    a4.metric("Pending Shipments", len(report["pending_shipments"]))
    a3.metric("Dispatched Vehicles", report["dispatched_vehicles"])
    st.subheader("Dispatch Manifest")
    dispatch_rows = []
    for v in report["dispatch_manifest"]:
        for sh in v.shipment:
            dispatch_rows.append({
                "Vehicle_id": v.vehicle_id,
                "Vehicle_type": v.vehicle_type,
                "Destination": v.distination,
                "Utilization": round(v.utilization(), 2),
                "Shipment count": len(v.shipments)
            })
            st.dataframe(dispatch_rows, use_container_width=True)
            st.subheader("Pending Shipments")
            pending_rows = []
            for s in report["pending_shipments"]:
                pending_rows.append({
                    "Shipment_id": s.shipment_id,
                    "Destination": s.destination,
                    "Weight": s.weight,
                    "Volume": s.volume,
                    "Reason": s.reason
                })
            st.dataframe(pending_rows, use_container_width=True)
            st.subheader("Invalid Records")
            st.dataframe(report["invalid_records"], use_container_width=True)
            st.subheader("Utilization Summary")
            chart_data = []
            for v in report["dispatch_manifest"]:
                chart_data[v.vehicle_id] = v.utilization()
            if chart_data:
                st.bar_chart(chart_data)
            os.unlink(tmp_path)
        else:
            st.info("Updload the scanner log file to begin")