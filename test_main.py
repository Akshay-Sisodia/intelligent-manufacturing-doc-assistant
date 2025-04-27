import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_env():
    os.environ["ADMIN_TOKEN"] = "admin_secret"
    os.environ["TOP_K"] = "2"
    yield

# Mocking is recommended for LLM and DB calls in real world, but here we test integration

def test_query_endpoint(setup_env):
    response = client.post("/query", json={"question": "How to calibrate X-axis encoder?", "top_k": 2})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "latency_ms" in data
    assert isinstance(data["sources"], list)

def test_admin_reindex_unauthorized():
    response = client.post("/admin/reindex")
    assert response.status_code == 401

def test_admin_reindex_authorized(setup_env):
    response = client.post("/admin/reindex", headers={"Authorization": "Bearer admin_secret"})
    assert response.status_code == 200
    assert response.json()["status"] == "reindexed"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "query_count" in response.text

# --- KB Management ---
def test_admin_upload_and_list_documents(tmp_path, setup_env):
    # Create a dummy PDF file
    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n%...dummy pdf...\n%%EOF")
    with open(dummy_pdf, "rb") as f:
        response = client.post(
            "/admin/upload",
            headers={"Authorization": "Bearer admin_secret"},
            files={"file": ("dummy.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
    # List documents
    response = client.get("/admin/documents", headers={"Authorization": "Bearer admin_secret"})
    assert response.status_code == 200
    docs = response.json()["documents"]
    assert any("dummy.pdf" in d for d in docs)

def test_admin_delete_document(setup_env):
    # You must have uploaded a doc with doc_id 'dummy' for this to pass
    response = client.delete(
        "/admin/document/dummy",
        headers={"Authorization": "Bearer admin_secret"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
