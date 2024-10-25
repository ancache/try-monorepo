import httpx

def get_api_paths(r: httpx.Response):
    response = r.json()
    return response['paths'].keys()