# Application Overview

## Overview
This application is a secure financial analysis tool designed for BanBajío. It is built using Python, Streamlit, and several supporting libraries. The app allows users to upload, process, and analyze financial data (accounts, transactions, promotions) from Excel files. It also offers interactive visualizations and detailed statistical analyses of the financial information.

## Key Features
- **User Authentication**: Secure login with rate limiting and session management.
- **Data Upload and Processing**: Users can upload Excel files for accounts, transactions, and promotions. The data is then combined and processed for financial analysis.
- **Database Integration**: Stores and retrieves data from a PostgreSQL database using SQLAlchemy.
- **Financial Calculations**: Executes specialized financial calculations using custom algorithms (e.g., PRIME365, PRIME360).
- **Interactive Visualizations**: Presents data analysis results via tables, correlation matrices, and charts.
- **Role-Based Access**: Supports different user roles (admin, analyst, viewer) with tailored permissions.
- **Security Logging**: Tracks login attempts, errors, and significant events for enhanced auditing.

## How It Works
1. **Login**: The user logs in using secure credentials. The system implements rate limiting and session timeout controls.
2. **File Upload & Storage**: Excel files containing financial data are uploaded, previewed, and stored in the database.
3. **Data Processing & Analysis**: The app combines data from different files, performs financial calculations, and populates a structured template.
4. **Results Display**: Analysis results are interactively visualized, with options for further statistical exploration.
