# Euro-Park Waiting Times Forecast 🚀  

## Overview  
**Euro-Park Waiting Times Forecast** is a data-driven solution designed to optimize guest experience by predicting waiting times and providing actionable insights for capacity management. Developed during a hackathon by **Gong Hei Fat Choy Consulting (Team #4)**, this project leverages machine learning to improve operational efficiency and enhance customer satisfaction.  

## Problem Statement  
Post-COVID, **waiting times have increased significantly** despite a 10% decrease in attendance compared to 2019. This has led to:  
- **Resource inefficiency** (under- or over-utilized staff and ride capacity)  
- **Guest dissatisfaction** (longer queues and negative reviews)  
- **Operational strain** (increased staff workload and safety concerns)  
- **Reduced guest spending** (less time for food, merchandise, and other in-park activities)  

## Solution  
We developed a **dashboard** that displays accurate predictions for waiting times and park attendance, helping park managers make data-driven decisions to optimize operations.  

### Key Features  
✅ **Predictive Modeling**: Uses XGBoost, LSTM, and VAR models to forecast waiting times and attendance.  
✅ **Interactive Dashboard**: Provides real-time insights on peak hours, queue durations, and attraction utilization.  
✅ **Actionable Insights**: Enables strategies such as **capacity optimization, personalized notifications, and queue monetization** to enhance guest experience.  

## Methodology  
Our approach involves:  
1. **Data Cleaning & Preprocessing**: Handling missing values, aligning datasets, and feature engineering.  
2. **Predictive Modeling**: Implementing machine learning models such as **XGBoost, LSTM, and VAR** to forecast waiting times and attendance.  
3. **Dashboard Development**: Creating an interactive visualization tool to monitor trends and optimize park operations.  

### Model Performance  
- **XGBoost**: Achieved high accuracy by incorporating **lag features** and **rolling windows**.  
- **LSTM**: Provided deep learning-based sequence predictions but required additional feature inputs.  
- **VAR**: Captured dependencies between attractions, enabling accurate predictions without external features.  

## Key Insights & Initiatives  
📌 **Optimize Ride Capacity**: Ensure 85% ride utilization for better guest flow and cost management.  
📌 **Personalized Guest Notifications**: Notify guests of attractions with low wait times to improve experience.  
📌 **Monetize Queues**: Deploy food and merchandise carts near high-traffic rides to increase revenue.  

## Results  
🎯 **Reduced average wait times** by predicting peak hours and optimizing ride scheduling.  
🎯 **Improved staff allocation** by balancing operational loads.  
🎯 **Increased guest satisfaction** through better crowd control and personalized experiences.  

## Next Steps  
🔹 **Prototype Development (0-3 months)**: Gather feedback and refine models.  
🔹 **Iteration & Optimization (3-6 months)**: Implement improved forecasting techniques and test financial impact.  
🔹 **Scalability (6+ months)**: Extend solutions to other theme parks and integrate with pricing and marketing strategies.  

## Demo  
Check out the live demo of our dashboard here:  
🔗 [Euro-Park Dashboard](https://crew-malaysia-mambo-routes.trycloudflare.com)  

## Team Members 👥  
- **Prashant Arya** ([LinkedIn](https://www.linkedin.com/in/prashantarya01250502/))  
- **Piangpim Chancharunee** ([LinkedIn](https://www.linkedin.com/in/piangpim-chancharunee/))  
- **Ruxi He** ([LinkedIn](https://www.linkedin.com/in/ruxi-he/))  
- **I-Hsun Lu** ([LinkedIn](https://www.linkedin.com/in/i-hsun-lu/))  
- **Hanqi Yang** ([LinkedIn](https://www.linkedin.com/in/hanqi-yang-0064431b2/))  
- **Bowei Zhao** ([LinkedIn](https://www.linkedin.com/in/bowei-zhao-ph-d-59658a80/))  

## Repository Structure  
📂 euro-park-wait-times
├── 📁 data_cleaning           # Code for data cleaning
├── 📁 modelling          # Code for modelling
├── 📁 dashboard       # Code for interactive visualization (to be uploaded)
├── 📄 README.md       # Project documentation
├── 📄 The Endless Line - Team 4.pdf      # Hackathon final report
