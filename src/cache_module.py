#cache_module.py

# Cache configuration
from collections import deque
QUERY_CACHE_LIMIT = 10
query_cache = deque(maxlen=QUERY_CACHE_LIMIT)

def cache_response(prompt, response, sources, retrieval_params):
    """Add a new query-response pair to the cache."""
    query_cache.append({
        'prompt': prompt, 
        'response': response,
        'sources': sources,
        'retrieval_params': retrieval_params
    })

def check_cache(prompt, current_params):
    """Check if the prompt already has a cached response with matching parameters."""
    for item in query_cache:
        if item['prompt'] == prompt and item['retrieval_params'] == current_params:
            return item['response'], item['sources']
    return None, None