import folium
import pandas as pd
from streamlit_folium import st_folium

def show_map(data_path="data/karachi_data.csv", search_query=None):
    df = pd.read_csv(data_path)
    m = folium.Map(location=[24.8607, 67.0011], zoom_start=11)

    # Risk Color Mapping for Accidents ONLY
    accident_risk_colors = {
        "High": "red",
        "Medium": "orange",
        "Low": "green"
    }

    # Add Legend with the new split logic
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 180px; height: 130px; 
     border:2px solid grey; z-index:9999; font-size:12px;
     background-color:white; opacity: 0.9; padding: 10px; border-radius:5px;">
     <b>🚨 Map Legend</b><br>
     <i class="fa fa-circle" style="color:blue"></i> Snatching<br>
     <hr style="margin:5px 0">
     <b>⚠️ Accidents:</b><br>
     <i class="fa fa-circle" style="color:red"></i> High Risk Accident<br>
     <i class="fa fa-circle" style="color:orange"></i> Medium Risk Accident<br>
     <i class="fa fa-circle" style="color:green"></i> Low Risk Accident
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    for _, row in df.iterrows():
        # LOGIC:
        # If Snatching -> Always Blue
        # If Accident -> Check Risk_Level (High=Red, Medium=Orange, Low=Green)
        
        if row['Type'] == "Snatching":
            marker_color = "blue"
        else:
            # Get color from dictionary, default to red if not found
            marker_color = accident_risk_colors.get(row['Risk_Level'], "red")
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            popup=f"<b>{row['Area']}</b><br>Type: {row['Type']}<br>Risk: {row['Risk_Level']}",
            color="black", # Black thin border for better contrast
            weight=1,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.8
        ).add_to(m)

    prediction = None
    if search_query:
        match = df[df['Area'].str.contains(search_query, case=False, na=False)]
        if not match.empty:
            prediction = match.iloc[0].to_dict()
        else:
            prediction = "Area not found in Karachi database."

    return m, prediction