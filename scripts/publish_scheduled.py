#!/usr/bin/env python3
"""
Webflow Scheduled Publisher

Reads schedule.json and publishes articles when their publish_date matches today.
Designed to run daily via GitHub Actions.
"""

import json
import os
import requests
from datetime import datetime, date
from pathlib import Path


def load_schedule():
    """Load the schedule from schedule.json"""
    schedule_path = Path(__file__).parent.parent / "schedule.json"
    with open(schedule_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_todays_articles(schedule):
    """Get articles scheduled for today"""
    today = date.today().isoformat()  # Format: YYYY-MM-DD

    articles_to_publish = []
    for article in schedule["articles"]:
        if article["publish_date"] == today and not article.get("published", False):
            articles_to_publish.append(article)

    return articles_to_publish


def publish_items(collection_id: str, item_ids: list, api_token: str) -> dict:
    """Publish items to Webflow via API"""
    url = f"https://api.webflow.com/v2/collections/{collection_id}/items/publish"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    payload = {
        "itemIds": item_ids
    }

    response = requests.post(url, headers=headers, json=payload)

    # Webflow returns 200 or 202 (Accepted) for successful publish operations
    if response.status_code in (200, 202):
        return {"success": True, "data": response.json()}
    else:
        return {"success": False, "error": response.text, "status_code": response.status_code}


def publish_site(site_id: str, api_token: str) -> dict:
    """Publish the entire site to make changes live"""
    url = f"https://api.webflow.com/v2/sites/{site_id}/publish"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    response = requests.post(url, headers=headers)

    # Webflow returns 200 or 202 (Accepted) for successful publish operations
    if response.status_code in (200, 202):
        return {"success": True, "data": response.json()}
    else:
        return {"success": False, "error": response.text, "status_code": response.status_code}


def update_schedule_status(schedule, published_ids):
    """Mark published articles in the schedule"""
    for article in schedule["articles"]:
        if article["item_id"] in published_ids:
            article["published"] = True
            article["published_at"] = datetime.now().isoformat()

    schedule_path = Path(__file__).parent.parent / "schedule.json"
    with open(schedule_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)

    return schedule


def main():
    print(f"=== Webflow Scheduled Publisher ===")
    print(f"Date: {date.today().isoformat()}")
    print()

    # Get API token from environment (set as GitHub Secret)
    api_token = os.environ.get("WEBFLOW_API_TOKEN")
    if not api_token:
        print("ERROR: WEBFLOW_API_TOKEN environment variable not set")
        return 1

    # Load schedule
    try:
        schedule = load_schedule()
        print(f"Loaded schedule with {len(schedule['articles'])} articles")
    except Exception as e:
        print(f"ERROR: Could not load schedule.json: {e}")
        return 1

    # Get today's articles
    articles = get_todays_articles(schedule)

    if not articles:
        print("No articles scheduled for today. Nothing to publish.")
        return 0

    print(f"\nArticles to publish today: {len(articles)}")
    for article in articles:
        print(f"  - {article['name']} (Collection: {article['collection']})")

    # Group articles by collection
    by_collection = {}
    for article in articles:
        coll_id = article["collection_id"]
        if coll_id not in by_collection:
            by_collection[coll_id] = []
        by_collection[coll_id].append(article)

    # Publish each collection's items
    all_published_ids = []
    errors = []

    for collection_id, coll_articles in by_collection.items():
        item_ids = [a["item_id"] for a in coll_articles]
        collection_name = coll_articles[0].get("collection", "Unknown")

        print(f"\nPublishing {len(item_ids)} items to {collection_name}...")
        result = publish_items(collection_id, item_ids, api_token)

        if result["success"]:
            print(f"  SUCCESS: Published {len(item_ids)} items")
            all_published_ids.extend(item_ids)
        else:
            print(f"  ERROR: {result.get('error', 'Unknown error')}")
            errors.append({
                "collection": collection_name,
                "error": result.get("error")
            })

    # Publish the site to make changes live
    if all_published_ids:
        site_id = schedule.get("site_id")
        if site_id:
            print(f"\nPublishing site to make changes live...")
            result = publish_site(site_id, api_token)
            if result["success"]:
                print("  SUCCESS: Site published")
            else:
                print(f"  WARNING: Could not publish site: {result.get('error')}")

        # Update schedule to mark as published
        # Note: This only works locally. For GitHub Actions, we'd need to commit the change.
        # For now, we just log it.
        print(f"\nPublished {len(all_published_ids)} articles successfully!")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for err in errors:
            print(f"  - {err['collection']}: {err['error']}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
