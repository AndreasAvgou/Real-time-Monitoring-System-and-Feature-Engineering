# Real time Monitoring System & Feature Engineering

## 📌 Overview
This project provides a robust and scalable API developed using the **FastAPI** framework to manage a complex feature engineering process. The service is designed for high performance and includes comprehensive monitoring and reporting capabilities.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **API Framework:** FastAPI
* **Web Server:** Gunicorn with Uvicorn workers for high-performance execution
* **Load Balancer:** NGINX to distribute incoming requests efficiently across service replicas
* **Database:** SQLite with WAL (Write-Ahead Logging) mode enabled for optimized concurrent access
* **Monitoring:** Grafana for real-time visualization of metrics
* **Testing:** Postman for performance baseline and stress testing

## 📁 Project Structure

The application follows a modular and scalable architecture designed for high availability and robust data processing:

```text
├── app/
│   ├── main.py            # API endpoints, monitoring middleware, and app initialization
│   ├── models.py          # SQLAlchemy ORM models with performance indexes and RFC3339 support
│   ├── schemas.py         # Pydantic models implementing strict validation and income tier rules
│   ├── database.py        # Database configuration with SQLite WAL mode and performance tuning
│   ├── utils.py           # Utility functions for CPU/RAM metrics and feature engineering logic
│   └── logger_config.py   # Custom logging implementation following %-5p standardized patterns
├── tests/
│   └── test_main.py       # Automated Unit Tests for validation logic and endpoint health
├── data/                  # Persistent storage directory for SQLite database files
├── data_combine/
│    └── test_main.py       # Persistent combine json_data for postman
├── nginx.conf             # Load balancing configuration for distributing traffic to API replicas
├── docker-compose.yml     # Orchestration for NGINX, API replicas (x2), Testing, and Grafana
├── Dockerfile             # Multi-stage build for the FastAPI application
└── README.md              # Technical documentation and project overview
```

## 🔍 Key Features

### 1. Advanced Data Validation

Every request undergoes strict schema validation based on the following rules:
* **Customer ID:** Must be 10-20 characters long and contain only ASCII characters.
* **Loan Amount:** Values must be between 100 and 1000.
* **Loan Fee:** Values must be between 10 and 50.
* **Income Tiers:** Automatically validates that the total credited amount (Amount + Fee) does not exceed limits based on the customer's annual income tier.

### 2. Monitoring & Metrics

The service captures and stores key performance indicators for every single request:
* **Request Latency:** Measured in milliseconds for every API call.
* **Failure Indicators:** Automated tracking of failed requests via HTTP status codes (e.g., 422 for validation errors).
* **Feature Metrics:** Real-time count of features with zero values within the dataset.
* **Resource Usage:** Continuous tracking of CPU and Memory usage percentages.


### 3. Infrastructure & Scalability

* **Load Balancing**: NGINX is utilized to distribute traffic across multiple API replicas.
* **Worker Management**: Gunicorn utilizes Uvicorn workers to maximize asynchronous throughput.
* **Deployment**: The entire application is containerized using Docker for consistent environment management.

## 🚦 API Endpoints

* **`GET /health`**: Returns `{"status": "UP"}` to verify the API is up and running.
* **`POST /feature-engineering`**: Validates input data, stores results in the DB, and returns engineered features in JSON format.
* **`GET /customer/{cid}/history/transactional`**: Retrieves historic raw transactional data for a specific customer.
* **`GET /customer/{cid}/history/features`**: Retrieves historic feature engineering outputs for a specific customer.
* **`DELETE /customer/{cid}`**: Purges customer records from both transactional and feature engineering databases.

## 📈 Performance Testing

Scalability and performance were verified using **Postman** to simulate real-time execution scenarios:
* **10,000 requests**: Executed to provide an initial view of service performance.
<img width="865" height="389" alt="image" src="https://github.com/user-attachments/assets/1fcfe32e-eb04-4c41-9178-389bbdb9e46b" />

| Metric | Value | Reference / Observation |
| ---------- | ---------- | ---------- |
| Total Iterations | 10,000 | Full dataset stress test. |
| Successful Requests (200 OK) | 5,002 | Data passing all validation rules. |
| Validation Failures (422 Error) | 5,004 | Requests rejected (Income Tiers/ID rules). |
| Internal API Latency (Mean) | 4.49 ms | Successfully met the <20ms target. |
| Postman Avg. Response Time | 33 ms | Total time including NGINX & Network. |
| System Errors (500/Socket) | 0 | System demonstrated 100% stability (Robustness). |
| Avg. CPU Usage | 1.65% | Highly efficient resource management. |
| Avg. RAM Usage | 8.98% | Stable memory footprint under load. |
| Features with Zero Values | 0 | No zero-value features in the current test run. |

* **100,000 requests**: Executed as a stress test to ensure system stability and scalability under heavy load.

<img width="746" height="339" alt="image" src="https://github.com/user-attachments/assets/dac0f760-7cf1-4d83-97f4-760c1ee7f5eb" />

| Metric | Value | Reference / Observation |
| ---------- | ---------- | ---------- |
| Total Iterations | 100,006 | Massive scale stress test completed successfully. |
| Successful Requests (200 OK) | 50,004 | Valid loan applications passing all business rules. |
| Validation Failures (422 Error) | 50,002 | Correct rejection of invalid data (Validation Robustness). |
| Internal API Latency (Mean) | 4.72 ms | Well below the <20ms target. |
| Postman Avg. Response Time | ~35 ms | Total time including network overhead and NGINX proxying. |
| System Errors (500/Socket) | 0 | 100% Stability: Zero infrastructure or database failures. |
| Avg. CPU Usage | 1.46% | Highly efficient async processing even under 100k load. |
| Avg. RAM Usage | 9.05% | Predictable and stable memory footprint. |
| Zero Value Count | 0 | Data quality check: No empty/zero features detected. |

## 🚀 How to Run

**1. Infrastructure Setup**

   Build and launch the API replicas, NGINX load balancer, and monitoring tools using Docker:
   ```bash
   docker-compose up --build
   ```
   * **API Entry Point:** http://localhost:8080 (Load balanced via NGINX).
   * **Monitor System:** Access the Grafana Dashboard at http://localhost:3000.
     
**2. Data Preparation**

   Before running the performance tests, you must generate the Postman-ready dataset using the provided Python utility:
   1.  Ensure your raw JSON samples are placed in the ```./data``` folder.
   2.  Run the transformation script to bundle samples into a master file:
  
   ```bash
      python3 postman.py
   ```

   3. The script will generate ```master_postman_data.json``` in the ```./postman_ready``` directory, containing the formatted payloads for the test iterations.

**3. Executing Stress Tests (Postman)**

Follow these steps to simulate real-time execution of 10,000 or 100,000 requests:

1. **Import Collection:** Open Postman and import the project's collection file.
2. **Configure Request:** Ensure the POST /feature-engineering request body is set to raw JSON using the variable {{raw_body}}.
3. **Open Runner:** Click on the Collection and select Run collection.
4. **Load Data:** Click Select File and choose the generated master_postman_data.json.
   * Set Iterations to 10000 or 100000.
5. **Run:** Execute the test and monitor the Validation Summary and Latency in real-time via the Grafana Dashboard.


## 📜 Logging Specifications

The system implements a standardized logging pattern: ```%-5p,%d{yyyy-MM-dd HH:mm:ss,SSS} (%t) [%c] %m [%M:%L]%n```.

* **DEBUG:** Detailed information, typically of interest only when diagnosing problems
* **INFO:** Confirms standard business processes.
* **WARN:** Indicates unexpected events or potential future problems.
* **ERROR/CRITICAL:** Reports serious issues preventing functional execution.
