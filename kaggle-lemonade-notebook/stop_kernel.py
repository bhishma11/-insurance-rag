import requests
import json
import os

kaggle_path = r"C:\Users\khett\Desktop\kaggle-lemonade-notebook\kaggle.json"
with open(kaggle_path, 'r') as f:
    creds = json.load(f)
    api_key = creds['key']

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("🔍 Trying to stop kernel via Kaggle API...")

# Try multiple possible endpoints
endpoints = [
    ('POST', 'https://www.kaggle.com/api/v1/kernels/stop'),
    ('POST', 'https://www.kaggle.com/api/i/kernels.KernelsService/StopKernel'),
    ('POST', 'https://www.kaggle.com/api/i/kernels.KernelsService/StopKernelSession'),
]

for method, url in endpoints:
    try:
        print(f"\n📡 Trying: {method} {url}")
        if method == 'POST':
            response = requests.post(
                url,
                headers=headers,
                json={'kernel': 'bhishmakhettri/lemonade-insurance-rag-model'},
                timeout=10
            )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200] if response.text else 'empty'}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
            break
    except Exception as e:
        print(f"   Error: {e}")