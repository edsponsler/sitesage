
import google.cloud.firestore
import requests
import os

def main():
    """
    Main function to find OPRD campgrounds and save them to Firestore using the new Places API.
    """
    # --- Environment Setup ---
    try:
        PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
        MAPS_API_KEY = os.environ["MAPS_API_KEY"]
    except KeyError as e:
        raise RuntimeError(f"Required environment variable {e} not set. Please source your .env file.") from e

    # --- Client Initialization ---
    print(f"Connecting to Firestore project: {PROJECT_ID}")
    db = google.cloud.firestore.Client(project=PROJECT_ID)

    # --- Data Ingestion Logic (using Places API - New) ---
    query = "campgrounds managed by Oregon Parks and Recreation Department"
    print(f"Searching for: '{query}' using Places API (New)...")

    # Define the new API endpoint and headers
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": MAPS_API_KEY,
        # FieldMask specifies which fields to return
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount"
    }
    data = {
        "textQuery": query
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        places_result = response.json()

        results = places_result.get("places", [])
        if not results:
            print("Success: The query returned zero results. No data to ingest.")
            return

        print(f"Found {len(results)} potential campgrounds.")

        # Process and save each result to Firestore
        batch = db.batch()
        for place in results:
            # Note the change from 'place_id' to 'id' in the new API response
            place_id = place["id"]
            doc_ref = db.collection("campgrounds").document(place_id)
            data = {
                # Note the change from 'name' to 'displayName'
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "location": google.cloud.firestore.GeoPoint(
                    place.get("location", {}).get("latitude", 0),
                    place.get("location", {}).get("longitude", 0)
                ),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount"),
                "place_id": place_id
            }
            batch.set(doc_ref, data)

        batch.commit()
        print(f"Success: Successfully wrote {len(results)} records to the 'campgrounds' collection in Firestore.")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error occurred: {err}")
        print(f"Response body: {err.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
