from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI(
    title="Enterprise ERP Integration & AI Support Assistant API",
    description="REST API middleware simulating ERP Order/Inventory lookups, JSON schema validation, and RAG-grounded stakeholder query resolution.",
    version="1.0.0"
)

ERP_INVENTORY = {
    "FG-100": {"description": "Premium Spirit 750ml", "stock": 950, "reorder_point": 400, "unit_price": 450.0, "warehouse": "BLR-WH1"},
    "FG-200": {"description": "Reserve Blend 750ml", "stock": 420, "reorder_point": 250, "unit_price": 620.0, "warehouse": "BLR-WH1"},
    "PKG-01": {"description": "Glass Bottle 750ml", "stock": 0, "reorder_point": 1000, "unit_price": 28.0, "warehouse": "HYD-WH2"},
}

ERP_ORDERS = {
    "SO-2026-101": {"customer": "Metro Distributors", "sku": "FG-100", "qty": 300, "status": "Shipped & Invoiced", "eta": "Delivered"},
    "SO-2026-103": {"customer": "Star Retail Chain", "sku": "FG-100", "qty": 500, "status": "Allocated - Ready to Ship", "eta": "2026-11-26"},
    "SO-2026-104": {"customer": "Deccan Hospitality", "sku": "FG-200", "qty": 200, "status": "Backordered - Stock Check", "eta": "2026-12-02"},
}

ERP_POLICIES_KB = {
    "p2p_match": "Three-Way Match requires Purchase Order Qty == Goods Receipt Note (GRN) Qty == Vendor Invoice Qty within 2% tolerance before payment release.",
    "cutover": "ERP Cutover freeze begins 48 hours prior to Go-Live. All open POs and Sales Orders must be reconciled in staging before final load.",
    "sla_backorder": "Backordered SKUs trigger an automated Procurement Requisition if Current Stock <= Reorder Point, with standard vendor lead time of 5-7 business days."
}

class SalesOrderPayload(BaseModel):
    so_number: str = Field(..., example="SO-2026-105")
    customer_name: str = Field(..., example="Apex Retail Group")
    sku: str = Field(..., example="FG-100")
    order_qty: int = Field(..., gt=0, example=150)

class StakeholderQuery(BaseModel):
    user_role: str = Field(..., example="Supply Chain Manager")
    question: str = Field(..., example="What is the status of SO-2026-103 and how does 3-way match work?")

@app.get("/")
def health_check():
    return {"status": "online", "service": "Enterprise ERP REST API & AI Assistant", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/erp/inventory/{sku}")
def get_inventory_status(sku: str):
    sku = sku.upper()
    if sku not in ERP_INVENTORY:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' not found in ERP Item Master.")
    item = ERP_INVENTORY[sku]
    alert = "REORDER_REQUIRED" if item["stock"] <= item["reorder_point"] else "HEALTHY"
    return {"sku": sku, **item, "stock_health": alert}

@app.post("/api/v1/erp/sales-orders", status_code=201)
def create_sales_order(payload: SalesOrderPayload):
    sku = payload.sku.upper()
    if sku not in ERP_INVENTORY:
        raise HTTPException(status_code=400, detail=f"Invalid SKU '{sku}'. Cannot create Sales Order.")
    available = ERP_INVENTORY[sku]["stock"]
    if available >= payload.order_qty:
        ERP_INVENTORY[sku]["stock"] -= payload.order_qty
        status = "Allocated - Ready to Ship"
    else:
        status = "Backordered - Insufficient Stock"
    ERP_ORDERS[payload.so_number] = {
        "customer": payload.customer_name,
        "sku": sku,
        "qty": payload.order_qty,
        "status": status,
        "eta": "2026-11-30"
    }
    return {"message": "Sales Order synced to ERP", "so_number": payload.so_number, "allocation_status": status}

@app.post("/api/v1/assistant/query")
def query_erp_assistant(query: StakeholderQuery):
    q_lower = query.question.lower()
    context_hits = []
    for so_id, details in ERP_ORDERS.items():
        if so_id.lower() in q_lower:
            context_hits.append(f"Order {so_id} ({details['customer']}): {details['qty']} units of {details['sku']} | Status: {details['status']} | ETA: {details['eta']}.")
    if "3-way" in q_lower or "three-way" in q_lower or "match" in q_lower or "invoice" in q_lower:
        context_hits.append(f"SOP Policy (P2P): {ERP_POLICIES_KB['p2p_match']}")
    if "cutover" in q_lower or "go-live" in q_lower:
        context_hits.append(f"SOP Policy (Cutover): {ERP_POLICIES_KB['cutover']}")
    if "backorder" in q_lower or "reorder" in q_lower:
        context_hits.append(f"SOP Policy (Inventory): {ERP_POLICIES_KB['sla_backorder']}")
    if not context_hits:
        context_hits.append("No exact order ID matched. Available SOP topics: P2P 3-Way Match, ERP Cutover, Backorder SLA.")
    return {
        "stakeholder_role": query.user_role,
        "verified_erp_context": context_hits,
        "plain_language_summary": " ".join(context_hits),
        "hallucination_guard": "STRICT_GROUNDED_MODE"
    }
