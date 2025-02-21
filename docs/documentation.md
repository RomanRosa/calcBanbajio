# Application Documentation

## Code Structure
The application is organized into several key components:

- **Security and Session Management**:  
  - **SecurityLogger**: Handles logging of security events.  
  - **RateLimiter**: Implements rate limiting to prevent brute-force attacks.  
  - **SessionManager**: Manages session activity and timeouts.  
  - **UserRoleManager**: Provides role-based access control.

- **User Authentication and Input Validation**:  
  - Functions like `validate_input`, `authenticate`, and `verify_password` ensure secure and sanitized user input.  
  - The `login_page` function provides the login interface with custom styling and error handling.

- **Database Integration**:  
  - `connect_to_database`: Connects to a PostgreSQL database using SQLAlchemy.  
  - Functions imported from `utils.py` (such as `create_table_if_not_exists` and `insert_data_into_table`) manage database operations.

- **Data Processing and Analysis**:  
  - The app loads Excel files for accounts, transactions, and promotions, and then combines them for processing.
  - Financial calculations are performed by custom classes (`FinancialCalculationPRIME` and `FinancialCalculationPRIME360`).
  - The `populate_template` function fills a JSON template with the calculated data.

- **Visualization**:  
  - The `AnalysisResultsVisualizer` class defines various methods to display results like general information, interest calculations, and graphical representations (e.g., heatmaps).

## Key Functions and Their Purposes

### `init_session_state()`
Initializes session state variables needed for authentication, data storage, and role management.

### `setup_app_config()`
Loads environment variables and configuration settings, ensuring that the application can connect to the required database.

### `load_users(file_path)`
Securely loads user credentials from a YAML file.

### `authenticate(username, password, users)`
Verifies user credentials using bcrypt for secure password handling.

### `connect_to_database(config)`
Establishes a connection with the PostgreSQL database using SQLAlchemy and returns the connection engine.

### `populate_template(template, calculations)`
Populates a JSON template with the financial calculation results, ensuring proper formatting and precision.

## Custom Styling and Layout
- **Global Styles**: Defined in the `set_global_styles()` function to inject custom CSS.
- **Logo Integration**: The logo is displayed using the `get_logo_img()` function (which uses a PNG image), integrated into both the sidebar and login page.
- **Enhanced Sidebar and Login Page**: Custom HTML and CSS are used in `setup_sidebar()` and `login_page()` to create a user-friendly interface.

## Error Handling and Logging
- **Security Logging**: All security events and errors are logged to `security_events.log` for auditing.
- **Robust Error Handling**: The application uses try/except blocks throughout to handle and log errors, ensuring stability and traceability.
