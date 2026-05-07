import requests
import json

url = 'http://localhost:5000/api/generate/questions'
headers = {'Content-Type': 'application/json'}
data = {
    "question_counts": {"2": 2, "5": 1},
    "query": "Generate questions about programming"
}

output_file = 'api_response.json'

try:
    print("Sending request to:", url)
    print("Request data:", json.dumps(data, indent=2))
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("\nStatus Code:", response.status_code)
    
    try:
        response_data = response.json()
        with open(output_file, 'w') as f:
            json.dump(response_data, f, indent=2)
        print(f"\nFull response saved to: {output_file}")
        
        if 'questions' in response_data:
            print(f"\nGenerated {len(response_data['questions'])} questions:")
            for i, q in enumerate(response_data['questions'], 1):
                print(f"\nQuestion {i}:")
                print(f"  Text: {q.get('question_text', 'N/A')}")
                print(f"  Marks: {q.get('marks', 'N/A')}")
                print(f"  Type: {q.get('question_type', 'N/A')}")
                print(f"  COs: {', '.join(map(str, q.get('co_mapping', ['N/A'])))}")
                print(f"  POs: {', '.join(map(str, q.get('po_mapping', ['N/A'])))}")
        else:
            print("\nNo questions in response. Full response:")
            print(json.dumps(response_data, indent=2))
            
    except json.JSONDecodeError:
        print("\nFailed to decode JSON response. Raw response:")
        print(response.text)
        
except Exception as e:
    print("\nError:", str(e))
