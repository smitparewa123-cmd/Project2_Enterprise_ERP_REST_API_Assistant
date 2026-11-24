# Enterprise AI Support Assistant & REST API Integration

An asynchronous **FastAPI + Pydantic** enterprise integration service that simulates real-time **ERP system integrations (Order Management & Inventory Lookups)** alongside a grounded **AI Stakeholder Support Assistant** that translates technical ERP statuses and SOP policies into plain-language updates.

---

## Key Features & ERP Alignment
1. **Asynchronous REST API Middleware (`FastAPI`):** Exposes clean REST endpoints (`GET /inventory/{sku}`, `POST /sales-orders`) simulating external e-commerce/CRM integrations pushing orders into an ERP backend.
2. **Strict JSON Schema Validation (`Pydantic`):** Enforces data integrity on inbound order payloads (rejecting negative quantities, missing keys, or invalid SKUs with HTTP `422`/`400` errors before corrupting ERP master tables).
3. **Grounded Stakeholder Assistant (`POST /assistant/query`):** Retrieves live Sales Order statuses and verified SOP rules (P2P Three-Way Match, Cutover Freeze, Backorder SLAs) to give non-technical business stakeholders accurate, hallucination-free updates.
4. **Automated Integration Test Suite (`test_api_integration.py`):** Verifies endpoint contracts, schema validation failures, stock allocation logic, and policy retrieval.

---

## Repository Structure
```text
├── README.md                    # Architecture & API endpoint documentation
├── main.py                      # FastAPI application, Pydantic schemas & ERP integration endpoints
├── test_api_integration.py      # Automated integration & payload validation test suite
├── sample_payloads.json         # Example JSON request bodies for Postman / cURL testing
└── requirements.txt             # Python dependencies
```

---

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. Open interactive Swagger API docs in your browser at `http://127.0.0.1:8000/docs` or run the automated integration tests:
   ```bash
   python test_api_integration.py
   ```
