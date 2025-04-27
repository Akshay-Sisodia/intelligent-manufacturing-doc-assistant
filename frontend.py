import os
import streamlit as st
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Manufacturing Document Assistant", layout="wide")
st.title("🦾 Manufacturing Document Assistant")

# --- Sidebar: Admin Knowledge Base Management ---
st.sidebar.header("Knowledge Base Admin")
admin_token = st.sidebar.text_input("Admin Token", type="password")

# --- Reindex Button and Progress ---
reindex_status = st.sidebar.empty()
if st.sidebar.button("Reindex Knowledge Base", key="reindex_btn"):
    import sseclient, requests
    reindex_status.info("Reindexing started...")
    try:
        # Stream progress from backend SSE endpoint
        with requests.get(f"{API_URL}/admin/reindex-sse", headers={"Authorization": f"Bearer {admin_token}"} if admin_token else {}, stream=True, timeout=120) as r:
            client = sseclient.SSEClient(r)
            for event in client.events():
                if event.event == "progress":
                    reindex_status.info(event.data)
                elif event.event == "done":
                    reindex_status.success("Reindexing complete!")
                    st.experimental_rerun()
                    break
                elif event.event == "error":
                    reindex_status.error(event.data)
                    break
    except Exception as e:
        reindex_status.error(f"Error: {e}")

def get_headers():
    return {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

def list_documents():
    try:
        r = requests.get(f"{API_URL}/admin/documents", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json().get("documents", [])
        else:
            st.sidebar.error(f"Failed to fetch documents: {r.text}")
            return []
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        return []

def upload_document():
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file and st.sidebar.button("Upload", key="upload_btn"):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        r = requests.post(f"{API_URL}/admin/upload", headers=get_headers(), files=files)
        if r.status_code == 200:
            st.sidebar.success(f"Uploaded: {uploaded_file.name}")
            st.experimental_rerun()
        else:
            st.sidebar.error(f"Upload failed: {r.text}")

def delete_document(documents):
    doc_to_delete = st.sidebar.selectbox("Delete Document", ["-"] + documents)
    if doc_to_delete and doc_to_delete != "-" and st.sidebar.button("Delete", key="delete_btn"):
        doc_id = doc_to_delete.rsplit(".", 1)[0]
        r = requests.delete(f"{API_URL}/admin/document/{doc_id}", headers=get_headers())
        if r.status_code == 200:
            st.sidebar.success(f"Deleted: {doc_to_delete}")
            st.experimental_rerun()
        else:
            st.sidebar.error(f"Delete failed: {r.text}")

with st.sidebar:
    docs = list_documents()
    st.markdown("**Knowledge Base Files:**")
    for d in docs:
        st.write(f"- {d}")
    upload_document()
    delete_document(docs)

# --- Main Panel: Q&A ---
st.header("Ask a Manufacturing Question")
question = st.text_input("Your question:")
top_k = st.slider("Top-K Results", min_value=1, max_value=10, value=5)
if st.button("Ask") and question:
    with st.spinner("Retrieving answer..."):
        resp = requests.post(f"{API_URL}/query", json={"question": question, "top_k": top_k})
        if resp.status_code == 200:
            data = resp.json()
            st.markdown(f"### Answer\n{data['answer']}")
            st.markdown("#### Sources:")
            for s in data["sources"]:
                st.write(f"- Source: `{s['source']}` — Score: {s['score']:.2f}")
                # Optionally show a snippet of the content:
                # st.caption(s['content'][:200] + "..." if len(s['content']) > 200 else s['content'])
            st.caption(f"Latency: {data['latency_ms']} ms")
        else:
            st.error(f"Query failed: {resp.text}")
