import httpx
from tz.api_utils import get_api_paths
from tz.processing_utils import get_sample_df

def foobar():
    return "foobar"

def main():
    print("Hello, World!")

    r = httpx.get("https://staging.api.feo.transitionzero.org/v2/openapi.json")

    paths = '\n'.join(get_api_paths(r))

    print(f"API paths:\n{paths}")

    print("\n\n")

    print(f"Sample data:\n{get_sample_df()}")

if __name__ == "__main__":
    main()