import requests

BASE_URL = "http://127.0.0.1:8000"
headers = {"X-User-UID": "usr_demo5_arjun"}

def test_clear_endpoint():
    # 1. Clear Arjun's invoices
    r = requests.post(f"{BASE_URL}/api/user/invoices/clear", headers=headers)
    assert r.status_code == 200
    print("[PASS] Clear API endpoint returned HTTP 200 OK:", r.json())

    # 2. Verify Arjun now has 0 invoices
    r_invs = requests.get(f"{BASE_URL}/api/user/invoices", headers=headers)
    invs = r_invs.json()["invoices"]
    assert len(invs) == 0
    print("[PASS] Verified 0 invoices remaining for user Arjun.")

if __name__ == "__main__":
    test_clear_endpoint()
