# About the Application

## Overview
This application is developed for performing financial analyses at BanBajío. It integrates various technologies to ensure secure data handling, robust processing, and interactive visualization of financial data.

## Technology Stack
- **Python**: Main programming language for application logic.
- **Streamlit**: Framework used for building the interactive web interface.
- **SQLAlchemy & PostgreSQL**: Used for database connectivity and data storage.
- **Pandas**: Utilized for data manipulation and analysis.
- **Bcrypt**: Provides secure password hashing.
- **YAML & JSON**: Used for configuration management and template population.
- **Matplotlib & Seaborn**: Libraries used for creating data visualizations.

## Key Components
- **User Authentication & Security**:
  - Users log in with credentials stored in a YAML file.
  - The system enforces rate limiting and session timeouts.
  - Security events and errors are logged for auditing purposes.

- **Database Integration**:
  - The application connects to a PostgreSQL database using credentials from environment variables (loaded via a `.env` file).
  - Data is stored and managed using dynamically created tables.

- **File Management**:
  - Users upload Excel files containing financial data (accounts, transactions, promotions).
  - Uploaded files are previewed in the app and then saved into the database.

- **Financial Calculations**:
  - Custom algorithms (e.g., PRIME365, PRIME360) perform detailed financial calculations.
  - Results are used to populate a structured JSON template for comparison.

- **Visualizations and Reporting**:
  - Interactive visualizations include tables, correlation matrices, and graphical heatmaps.
  - The `AnalysisResultsVisualizer` class organizes and displays various sections of the analysis.

## Additional Details
- **Configuration Files**:
  - Environment variables such as `DB_USER`, `DB_PASSWORD`, etc., are stored in a `.env` file.
  - Application configuration is also supported by a configuration file (e.g., located in the `.streamlit` directory).

- **Security and Logging**:
  - All security-related events and critical errors are recorded in `security_events.log`.
  - The application implements robust error handling to ensure reliable operation.
