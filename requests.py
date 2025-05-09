import requests

url = "https://example.com/api/data"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    # Process the successful response
    data = response.json()
    print("Data received:", data)

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")
    # Handle general request errors (connection errors, timeouts, etc.)

except requests.exceptions.HTTPError as e:
    print(f"HTTP error occurred: {e}")
    # Handle specific HTTP errors (e.g., 404 Not Found, 500 Internal Server Error)
    if response is not None:
        print(f"Response status code: {response.status_code}")
        try:
            error_data = response.json()
            print("Error details:", error_data)
        except ValueError:
            print("Could not decode error response as JSON.")

except requests.exceptions.ConnectionError as e:
    print(f"Connection error occurred: {e}")
    # Handle errors like network issues or the server being unreachable

except requests.exceptions.Timeout as e:
    print(f"Timeout error occurred: {e}")
    # Handle cases where the request took too long

except requests.exceptions.URLRequired as e:
    print(f"Invalid URL provided: {e}")
    # Handle cases where the URL is malformed

except requests.exceptions.TooManyRedirects as e:
    print(f"Too many redirects occurred: {e}")
    # Handle cases where the server redirects the request too many times

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Catch any other unexpected exceptions
