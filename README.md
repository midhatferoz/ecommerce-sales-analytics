# E-Commerce Sales & Customer Behavior Analytics

An interactive data analytics dashboard built with Python, Pandas, Plotly, and Streamlit to analyze e-commerce sales performance, customer behavior, product categories, geography, and service quality.

## Project Overview

This project analyzes an e-commerce transaction dataset to identify sales trends, customer purchasing patterns, product/category performance, geographical performance, and delivery and rating insights.

The project combines exploratory data analysis with an interactive Streamlit dashboard that allows users to filter the data and explore different business metrics.

## Objectives

- Analyze overall e-commerce sales performance
- Track revenue and order trends over time
- Identify high-performing product categories
- Analyze customer purchasing behavior
- Understand repeat customer patterns
- Segment customers using RFM analysis
- Compare performance across cities and other geographical dimensions
- Analyze device and payment behavior
- Evaluate delivery performance and customer ratings
- Provide an interactive dashboard for business insights

## Key Performance Indicators

The dashboard provides the following major KPIs:

- Total Revenue
- Total Orders
- Number of Customers
- Average Order Value (AOV)
- Repeat Customer Rate
- Average Delivery Time
- Average Customer Rating


## Dashboard Features

### 1. Dashboard

Provides an overall view of e-commerce performance, including:

- Revenue trend over time
- Monthly order trends
- Revenue by product category
- Top geographical locations
- Customer segment distribution
- Orders by device type
- Delivery and rating summary


## Dashboard Screenshots

### Dashboard Overview

![Dashboard Overview](screenshots/dashboard-overview.png)

### Sales, Customer & Behavioral Insights

![Dashboard Insights](screenshots/dashboard-insights.png)


### 2. Product & Category Analysis

Analyzes product category performance using:

- Revenue by category
- Sales/orders by category
- Revenue share
- Category-level performance tables

### 3. Geography Analysis

Allows comparison across geographical levels such as:

- Cities
- States/regions
- Countries, when available

The dashboard provides:

- Revenue comparison
- Order comparison
- Customer comparison
- Average Order Value
- Location performance tables

### 4. Customer Segmentation

Uses RFM (Recency, Frequency, Monetary) analysis to understand customer segments.

The dashboard includes:

- Customers per segment
- Revenue by segment
- Segment-level RFM summaries
- Recency vs Monetary analysis

### 5. Customer Behavior

Analyzes customer behavior across dimensions such as:

- Device type
- Payment method
- Gender
- Age group

It also includes:

- Revenue share
- Average Order Value
- Category × Device revenue analysis
- Orders per customer

### 6. Delivery & Ratings

Analyzes service quality using:

- Delivery time distribution
- Customer rating distribution
- Average rating by delivery time
- Service performance by category, city, or device

## Dataset

The project uses the following dataset:

`ecommerce_customer_behavior_dataset_v2.csv`

The processed version used by the Streamlit dashboard is:

`data/processed/ecommerce_cleaned.csv`

An optional customer segmentation file is:

`data/processed/customer_segments.csv`


## Technologies Used
Python
Pandas
NumPy
Matplotlib
Seaborn
Plotly
Streamlit
Jupyter Notebook
 
 
## Project Structure

```text
ecommerce-sales-analytics/
│
├── data/
│   ├── ecommerce_customer_behavior_dataset_v2.csv
│   └── processed/
│       ├── ecommerce_cleaned.csv
│       ├── customer_segments.csv
│       ├── monthly_sales.csv
│       ├── category_analysis.csv
│       └── city_analysis.csv
│
├── notebooks/
│   └── analysis.ipynb
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore