\# 🚇 London Transport Intelligence Platform



A data-driven transport analytics platform for monitoring, analysing and forecasting public transport demand across London.



The project combines \*\*live Transport for London (TfL) data\*\*, historical transport datasets, \*\*PostgreSQL\*\*, machine learning and an interactive \*\*Streamlit dashboard\*\* to provide insights into network performance, passenger demand, station activity and service disruptions.



\## 📌 Project Overview



London's public transport network generates large volumes of operational and passenger-demand data. This project brings multiple transport datasets together into a single analytical platform.



The platform currently covers:



\- London Underground

\- London Buses

\- Elizabeth line

\- London Overground

\- DLR



It combines historical analysis with live operational information and machine-learning-based demand forecasting.



\## ✨ Key Features



\### 🚦 Live Network Monitoring



The platform retrieves current TfL operational information, including:



\- Line status

\- Service disruptions

\- Live bus arrivals

\- Live rail arrivals

\- Lift disruptions

\- Station and stop information



A separate Python data collector can retrieve live TfL information and store snapshots in PostgreSQL for subsequent analysis.



\### 🚌 Live Bus Intelligence



Users can search for a London bus stop and view:



\- Upcoming buses

\- Route numbers

\- Expected arrival times

\- Destinations

\- Vehicle information

\- Stop location

\- Arrival patterns



\### 🚉 Station Intelligence



The station interface provides:



\- Station location

\- Transport mode

\- Active lines

\- Live arrivals

\- Destinations

\- Vehicle information

\- Arrival-time visualisation



\### ♿ Lift Disruption Monitoring



Accessibility information is presented through:



\- Affected stations

\- Disrupted lifts

\- Current disruption messages

\- Station-level disruption summaries

\- Accessibility insights



\### 📊 Historical Network Analytics



Historical TfL data is used to analyse:



\- Tube and bus demand

\- Daily passenger journeys

\- Long-term demand trends

\- Station entry and exit activity

\- Weekday and weekend behaviour

\- Peak travel patterns

\- Station demand profiles



The historical journey dataset covers \*\*2,798 days from 2019 to August 2026\*\*.



\## 🤖 Machine Learning Demand Forecasting



Several forecasting approaches were evaluated for predicting total daily network demand.



| Model | MAE | RMSE | R² |

|---|---:|---:|---:|

| 7-Day Seasonal Baseline | 446,718 | 757,960 | 0.5955 |

| Linear Regression | 395,691 | 598,336 | 0.7480 |

| Random Forest | 227,872 | 362,910 | 0.9073 |

| LightGBM | 222,110 | 348,128 | 0.9147 |

| \*\*XGBoost\*\* | \*\*208,955\*\* | \*\*335,575\*\* | \*\*0.9207\*\* |



\*\*XGBoost achieved the strongest predictive performance with an R² of 0.9207.\*\*



The forecasting model uses calendar, lag and rolling-demand features, including:



\- Day of week

\- Day of year

\- Week of year

\- Month and year

\- Weekend indicator

\- 1-day lag

\- 7-day lag

\- 14-day lag

\- 28-day lag

\- 7-day rolling mean

\- 28-day rolling mean



The Streamlit application supports recursive future demand forecasts for a user-selected forecast horizon.



\## 🏗️ Platform Architecture



```text

Historical TfL Data                 Live TfL API

&#x20;      │                                 │

&#x20;      └──────────────┬──────────────────┘

&#x20;                     │

&#x20;                Python ETL

&#x20;                     │

&#x20;                     ▼

&#x20;                PostgreSQL

&#x20;                     │

&#x20;             ┌───────┴────────┐

&#x20;             │                │

&#x20;             ▼                ▼

&#x20;      Historical Analysis   Live Analytics

&#x20;             │                │

&#x20;             └───────┬────────┘

&#x20;                     │

&#x20;                     ▼

&#x20;            Machine Learning

&#x20;                     │

&#x20;                     ▼

&#x20;            Streamlit Dashboard

```



\## 🛠️ Technology Stack



\*\*Programming \& Data Processing\*\*

\- Python

\- Pandas

\- NumPy



\*\*Machine Learning\*\*

\- XGBoost

\- LightGBM

\- Random Forest

\- Linear Regression

\- Scikit-learn



\*\*Database\*\*

\- PostgreSQL

\- SQL



\*\*Data Visualisation\*\*

\- Streamlit

\- Plotly

\- Power BI



\*\*Data Engineering\*\*

\- TfL Unified API

\- REST APIs

\- Python ETL pipelines



\*\*Development\*\*

\- Jupyter Notebook

\- Git

\- GitHub



\## 🗄️ Data Sources



The project uses publicly available transport datasets and live API data from \*\*Transport for London (TfL)\*\*.



Historical data includes:



\- Journey demand data

\- Station footfall

\- NUMBAT station demand profiles

\- PTAL data

\- Annualised station statistics



Live data includes:



\- TfL line status

\- Bus arrivals

\- Rail arrivals

\- Lift disruptions

\- Station and stop information



\## 📂 Repository Structure



```text

london-transport-intelligence-platform/

│

├── app/

│   └── app.py

│

├── data/

│   └── processed/

│

├── image/

│   └── bannerimage.png

│

├── models/

│   └── xgboost\_network\_demand\_model.pkl

│

├── collect\_live\_data.py

├── postgres.sql

├── README.md

└── .gitignore

```



Large raw datasets and local database files are intentionally excluded from the repository.



\## ⚙️ Running the Application



\### 1. Clone the repository



```bash

git clone https://github.com/poudelkeshav/london-transport-intelligence-platform.git

cd london-transport-intelligence-platform

```



\### 2. Install dependencies



```bash

pip install -r requirements.txt

```



\### 3. Configure PostgreSQL



Create a PostgreSQL database and use the provided SQL file where appropriate:



```text

postgres.sql

```



Database credentials should be stored as environment variables and should \*\*never be committed to GitHub\*\*.



For example:



```text

DB\_PASSWORD=your\_database\_password

```



\### 4. Run the Streamlit application



```bash

streamlit run app/app.py

```



\## 📡 Live Data Collection



Live TfL operational snapshots can be collected using:



```bash

python collect\_live\_data.py

```



The collector retrieves current operational information and stores it in PostgreSQL for use by the dashboard.



\## 📈 Dashboard Modules



The Streamlit application contains dedicated interfaces for:



1\. Dashboard

2\. Line Status

3\. Bus Arrivals

4\. Station Information

5\. Lift Disruptions

6\. Demand Forecasting

7\. Network Analytics

8\. About



\## 🎯 Project Purpose



The project demonstrates an end-to-end data workflow rather than only a standalone machine-learning model.



It brings together:



\*\*API ingestion → data engineering → SQL → historical analytics → machine learning → live monitoring → interactive visualisation\*\*



This architecture demonstrates how transport data can be transformed into practical information for understanding demand patterns and network conditions.



\## 🔮 Future Development



Potential extensions include:



\- Automated cloud-based live data collection

\- FastAPI service layer

\- Docker containerisation

\- Cloud deployment

\- Additional anomaly detection

\- Weather and event-data integration

\- Spatial demand forecasting

\- Historical disruption modelling when sufficient labelled data becomes available



\## 👤 Author



\*\*Keshav Poudel\*\*



Data Science | Data Analytics | Machine Learning | Python | SQL | Power BI



GitHub: \[poudelkeshav](https://github.com/poudelkeshav)



\---



\*Built as a personal data science and transport analytics project focused on London's public transport network.\*

