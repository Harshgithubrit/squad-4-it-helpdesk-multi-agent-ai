from tools.knowledge_search import search_knowledge

def test_search_returns_relevant_doc():
    docs = search_knowledge("laptop Wi-Fi internet not working")
    assert docs
    assert docs[0]["category"] == "network"
