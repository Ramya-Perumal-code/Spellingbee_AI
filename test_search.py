from duckduckgo_search import DDGS

try:
    print("Testing DDGS...")
    results = DDGS().text(keywords="define apple", max_results=1)
    print(f"Results type: {type(results)}")
    print(f"Results: {results}")
    
    if results:
        print(f"Body: {results[0].get('body')}")
    else:
        print("No results found.")
        
except Exception as e:
    print(f"Error: {e}")
