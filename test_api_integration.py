from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_inventory_lookup_reorder_alert():
    res = client.get("/api/v1/erp/inventory/PKG-01")
    assert res.status_code == 200
    assert res.json()["stock_health"] == "REORDER_REQUIRED"

def test_create_sales_order_valid():
    payload = {
        "so_number": "SO-2026-105",
        "customer_name": "Apex Retail Group",
        "sku": "FG-100",
        "order_qty": 100
    }
    res = client.post("/api/v1/erp/sales-orders", json=payload)
    assert res.status_code == 201
    assert res.json()["allocation_status"] == "Allocated - Ready to Ship"

def test_create_sales_order_invalid_qty():
    payload = {
        "so_number": "SO-2026-106",
        "customer_name": "Bad Payload Corp",
        "sku": "FG-100",
        "order_qty": -50
    }
    res = client.post("/api/v1/erp/sales-orders", json=payload)
    assert res.status_code == 422

def test_ai_assistant_grounded_response():
    res = client.post("/api/v1/assistant/query", json={
        "user_role": "Finance Controller",
        "question": "Check SO-2026-103 and explain 3-way match rules."
    })
    assert res.status_code == 200
    body = res.json()
    assert "Allocated - Ready to Ship" in body["plain_language_summary"]
    assert "Three-Way Match" in body["plain_language_summary"]

if __name__ == "__main__":
    test_health_check()
    test_inventory_lookup_reorder_alert()
    test_create_sales_order_valid()
    test_create_sales_order_invalid_qty()
    test_ai_assistant_grounded_response()
    print("All 5 ERP REST API & Integration UAT tests PASSED!")
