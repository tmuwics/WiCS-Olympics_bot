#check if there is a record in sheets
from urllib.parse import quote
import re
import asyncio
from datetime import datetime, timezone
import requests
from config import SHEETDB_URL

#check if there is a record in sheets
def find_in_DB(key: str):
    encoded_key = quote(key, safe="")
    #prolly change mostof these to a global variable
    url = f"{SHEETDB_URL}/search?Student_Email={encoded_key}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

async def find_in_DB_async(key: str):
    return await asyncio.to_thread(find_in_DB, key)

def submission_exists(student_email: str, exec_role: str) -> bool:
    """
    Returns True if a submission already exists for this
    (student_email + exec_role), otherwise False.
    """

    rows = find_in_DB(student_email)
    target = normalize(exec_role)

    for row in rows:
        existing_roles = [
            normalize(r)
            for r in row.get("Exec_Role", "").split(" - ")
            if r.strip()
        ]

        if target in existing_roles:
            return True

    return False

def update_db(student_email, points_to_add, exec_role, new_loc, new_ig, new_image_url):
    rows = find_in_DB(student_email)
    current_points = int(rows[0].get("Points", 0))
    new_total = current_points + points_to_add
    sheetdb_update_user(student_email, new_total, exec_role, new_loc, new_ig, new_image_url)
    return new_total, False  

async def update_db_async(student_email, points_to_add, exec_role, new_loc, new_ig, new_image_url):
    return await asyncio.to_thread(update_db, student_email, points_to_add, exec_role, new_loc, new_ig, new_image_url)

def sheetdb_update_user(student_email, new_points, new_role, new_loc, new_ig, image_url):
    encoded_email = quote(student_email, safe="")
    url = f"{SHEETDB_URL}/Student_Email/{encoded_email}"

    rows = find_in_DB(student_email)
    existing_roles = rows[0].get("Exec_Role", "")
    existing_location = rows[0].get("Location", "")
    existing_url = rows[0].get("Image_URL", "")

    # avoid duplicate role entries
    roles = [r.strip() for r in existing_roles.split(" - ") if r.strip()]
    if new_role not in roles:
        roles.append(new_role)

    locations = [r.strip() for r in existing_location.split(" - ") if r.strip()]
    if new_loc not in locations:
        locations.append(new_loc)

    image_urls = [r.strip() for r in existing_url.split(" \n ") if r.strip()]
    if image_url and image_url not in image_urls:
        image_urls.append(image_url)

    payload = {
        "Location": " - ".join(locations),
        "Points": new_points,
        "Exec_Role": " - ".join(roles),
        "Instagram": new_ig,
        "Image_URL": " \n ".join(image_urls),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

    r = requests.patch(url, json=payload, timeout=10)
    r.raise_for_status()

#appaned the row to sheet db
def sheetdb_append(row: dict):
    payload = {"data": [row]}
    r = requests.post(SHEETDB_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()
async def sheetdb_append_async(row: dict):
    return await asyncio.to_thread(sheetdb_append, row)

#normalize string text
def normalize(text: str) -> str:
    t = text.strip().lower()
    # normalize comma spacing: "a, b", "a ,b", "a,b" -> "a, b"
    t = re.sub(r"\s*,\s*", ", ", t)
    # collapse any remaining whitespace
    t = " ".join(t.split())
    return t