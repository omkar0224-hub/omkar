import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Travel Tracker",
    page_icon="🚲",
    layout="wide"
)

# Initialize session state
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'travel_data' not in st.session_state:
    st.session_state.travel_data = []
if 'current_day' not in st.session_state:
    st.session_state.current_day = 0

# Title
st.title("🚲 Weekly Travel Tracker")
st.markdown("Track your daily travel, costs, and carbon emissions")

# Sidebar for user information
with st.sidebar:
    st.header("👤 User Information")
    
    name = st.text_input("Enter your name:", value=st.session_state.user_info.get('name', ''))
    age = st.number_input("Enter your age:", min_value=1, max_value=120, value=st.session_state.user_info.get('age', 25))
    vehicle = st.text_input("Enter your bike model:", value=st.session_state.user_info.get('vehicle', ''))
    city = st.text_input("Enter your city name:", value=st.session_state.user_info.get('city', ''))
    
    if st.button("Save User Info"):
        st.session_state.user_info = {
            'name': name,
            'age': age,
            'vehicle': vehicle,
            'city': city
        }
        st.success("User information saved!")

# Main content
if st.session_state.user_info:
    st.subheader(f"Welcome, {st.session_state.user_info['name']}! 👋")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📅 Daily Entry", "📊 Summary", "📈 Analytics"])
    
    with tab1:
        st.header("Daily Travel Entry")
        
        # Day selection
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_day = st.selectbox("Select Day:", days)
        
        with col2:
            if st.button("Clear All Data", type="secondary"):
                st.session_state.travel_data = []
                st.rerun()
        
        # Check if day already exists
        existing_entry = next((entry for entry in st.session_state.travel_data if entry['day'] == selected_day), None)
        
        if existing_entry:
            st.info(f"Data for {selected_day} already exists. You can update it below.")
        
        st.markdown(f"### WOW!! Today is {selected_day} 🎉")
        
        # Travel form
        with st.form(f"travel_form_{selected_day}"):
            col1, col2 = st.columns(2)
            
            with col1:
                did_travel = st.radio("Did you travel today?", ["Yes", "No"], key=f"travel_{selected_day}")
            
            if did_travel == "Yes":
                with col2:
                    destination = st.text_input("Where did you travel?", value=existing_entry['destination'] if existing_entry else "")
                
                travel_km = st.number_input(
                    "How many km did you travel?", 
                    min_value=0, 
                    max_value=1000, 
                    value=existing_entry['travel_km'] if existing_entry else 0
                )
                
                # Calculate costs and emissions
                km_cost = travel_km * 75
                km_emission = travel_km * 125
                
                # Display calculations
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Distance", f"{travel_km} km")
                with col2:
                    st.metric("Estimated Cost", f"₹{km_cost}")
                with col3:
                    st.metric("Carbon Emission", f"{km_emission}g")
                
                submitted = st.form_submit_button("Save Travel Data", type="primary")
                
                if submitted and travel_km > 0:
                    # Remove existing entry if updating
                    st.session_state.travel_data = [entry for entry in st.session_state.travel_data if entry['day'] != selected_day]
                    
                    # Add new entry
                    st.session_state.travel_data.append({
                        'day': selected_day,
                        'destination': destination,
                        'travel_km': travel_km,
                        'cost': km_cost,
                        'emission': km_emission,
                        'traveled': True
                    })
                    
                    st.success(f"✅ Travel data for {selected_day} saved successfully!")
                    st.balloons()
            else:
                st.success("🌱 That's great! You saved money and reduced carbon emission.")
                
                submitted = st.form_submit_button("Save No-Travel Day", type="primary")
                
                if submitted:
                    # Remove existing entry if updating
                    st.session_state.travel_data = [entry for entry in st.session_state.travel_data if entry['day'] != selected_day]
                    
                    # Add no-travel entry
                    st.session_state.travel_data.append({
                        'day': selected_day,
                        'destination': 'No travel',
                        'travel_km': 0,
                        'cost': 0,
                        'emission': 0,
                        'traveled': False
                    })
                    
                    st.success(f"✅ No-travel day for {selected_day} recorded!")
    
    with tab2:
        st.header("📊 Weekly Summary")
        
        if st.session_state.travel_data:
            # Create DataFrame
            df = pd.DataFrame(st.session_state.travel_data)
            
            # Display summary table
            st.subheader("Travel Summary Table")
            
            # Format display DataFrame
            display_df = df.copy()
            display_df['Cost (₹)'] = display_df['cost'].apply(lambda x: f"₹{x}")
            display_df['Emission (g)'] = display_df['emission'].apply(lambda x: f"{x}g")
            display_df['Distance (km)'] = display_df['travel_km'].apply(lambda x: f"{x} km")
            
            st.dataframe(
                display_df[['day', 'destination', 'Distance (km)', 'Cost (₹)', 'Emission (g)']],
                column_config={
                    'day': 'Day',
                    'destination': 'Destination',
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Calculate totals
            travel_days = df[df['traveled'] == True]
            
            if not travel_days.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Distance", f"{travel_days['travel_km'].sum()} km")
                
                with col2:
                    st.metric("Total Cost", f"₹{travel_days['cost'].sum()}")
                
                with col3:
                    st.metric("Total Emissions", f"{travel_days['emission'].sum()}g")
                
                with col4:
                    st.metric("Travel Days", f"{len(travel_days)}/7 days")
                
                # Min/Max emissions
                if len(travel_days) > 0:
                    st.subheader("📈 Emission Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Maximum Daily Emission", f"{travel_days['emission'].max()}g")
                    
                    with col2:
                        st.metric("Minimum Daily Emission", f"{travel_days['emission'].min()}g")
                    
                    with col3:
                        avg_emission = travel_days['emission'].mean()
                        st.metric("Average Daily Emission", f"{avg_emission:.1f}g")
            else:
                st.info("🌱 Great! No travel emissions recorded this week!")
        else:
            st.info("📝 No travel data entered yet. Use the 'Daily Entry' tab to start tracking!")
    
    with tab3:
        st.header("📈 Travel Analytics")
        
        if st.session_state.travel_data:
            df = pd.DataFrame(st.session_state.travel_data)
            travel_df = df[df['traveled'] == True]
            
            if not travel_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Daily distance chart
                    fig_distance = px.bar(
                        travel_df, 
                        x='day', 
                        y='travel_km',
                        title='Daily Travel Distance',
                        labels={'travel_km': 'Distance (km)', 'day': 'Day'},
                        color='travel_km',
                        color_continuous_scale='Blues'
                    )
                    fig_distance.update_layout(showlegend=False)
                    st.plotly_chart(fig_distance, use_container_width=True)
                
                with col2:
                    # Emissions pie chart
                    fig_pie = px.pie(
                        travel_df,
                        values='emission',
                        names='day',
                        title='Carbon Emissions by Day'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Combined metrics chart
                fig_combined = go.Figure()
                
                fig_combined.add_trace(go.Scatter(
                    x=travel_df['day'],
                    y=travel_df['cost'],
                    mode='lines+markers',
                    name='Cost (₹)',
                    line=dict(color='green'),
                    yaxis='y'
                ))
                
                fig_combined.add_trace(go.Scatter(
                    x=travel_df['day'],
                    y=travel_df['emission'],
                    mode='lines+markers',
                    name='Emissions (g)',
                    line=dict(color='red'),
                    yaxis='y2'
                ))
                
                fig_combined.update_layout(
                    title='Cost vs Emissions Trend',
                    xaxis_title='Day',
                    yaxis=dict(title='Cost (₹)', side='left'),
                    yaxis2=dict(title='Emissions (g)', side='right', overlaying='y'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_combined, use_container_width=True)
                
                # Environmental impact
                st.subheader("🌍 Environmental Impact")
                total_emission = travel_df['emission'].sum()
                trees_needed = total_emission / 21000  # Approximate CO2 absorption per tree per year
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Weekly CO2 Equivalent", f"{total_emission/1000:.2f} kg")
                with col2:
                    st.metric("Trees Needed to Offset", f"{trees_needed:.2f}")
                with col3:
                    fuel_saved = (7 - len(travel_df)) * 2  # Assuming 2L fuel saved per no-travel day
                    st.metric("Fuel Saved (L)", f"{fuel_saved}")
            else:
                st.info("🌱 No travel data to analyze. Great for the environment!")
        else:
            st.info("📊 Enter some travel data to see analytics!")

else:
    st.info("👈 Please fill in your information in the sidebar to get started!")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit | Track responsibly, travel sustainably! 🌱")