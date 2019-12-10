import flickr_api
import json
import os
import logging
import datetime
from collections import defaultdict

logging.basicConfig()

API_KEY = u""
API_SECRET = u""
RUNNING_DIR = os.path.dirname(os.path.abspath(__file__))


class Photo:
    def __init__(self, photo_id, user_id, lat, long, date_taken):
        self.photo_id = photo_id
        self.user_id = user_id
        self.lat = lat
        self.long = long
        self.date_taken = date_taken


def serialize(obj):
    return obj.__dict__


flickr_api.set_keys(api_key=API_KEY, api_secret=API_SECRET)

# Ids for London, Madrid, Barcelona, Athens and Rio de Janeiro
places_info = [
    {"id": "RcWoHEVTUb4U88DIPw", "name": "london"},
    {"id": "tbbWAcFQULxlR.kpfA", "name": "madrid"},
    {"id": "ryk5Tt5QULwqbhVKIw", "name": "barcelona"},
    {"id": "k7Im6tpQUL9bun6_ig", "name": "athens"},
]

for place in places_info:
    os.chdir("{}/../data/{}".format(RUNNING_DIR, place["name"]))
    photos = []
    date = datetime.datetime(2016, 12, 31)
    duplicates = 0
    photo_hash = {}
    photo_hash = defaultdict(lambda: -1, photo_hash)
    days_processed = 0

    while str(date.date()) != "2019-01-01":
        days_processed += 1
        date += datetime.timedelta(days=1)
        print("Processing for date {}".format(date.date()))
        while True:
            try:
                flickr_photos = flickr_api.Photo.search(
                    has_geo=1,
                    place_id=place["id"],
                    content_type=1,
                    per_page=100,
                    page=1,
                    min_taken_date=date.date(),
                    max_taken_date=(date + datetime.timedelta(days=1)).date(),
                    extras="geo, date_taken",
                )
                for photo in flickr_photos:
                    photos.append(
                        Photo(
                            photo.id,
                            photo.owner.id,
                            photo.latitude,
                            photo.longitude,
                            photo.datetaken,
                        )
                    )
                    if photo_hash[photo.id] == "stored":
                        print("Repeated photo {} in the set".format(photo.id))
                        duplicates += 1
                    else:
                        photo_hash[photo.id] = "stored"
                break
            except Exception as e:
                print("Exception {}".format(e))
                continue

        num_pages = flickr_photos.info.pages
        print(flickr_photos.info.total)

        for photo in flickr_photos:
            photos.append(
                Photo(
                    photo.id,
                    photo.owner.id,
                    photo.latitude,
                    photo.longitude,
                    photo.datetaken,
                )
            )

        for cur_page in range(2, num_pages + 1):
            print(
                "processing page {} out of {} for city {}".format(
                    cur_page, num_pages, place["name"]
                )
            )

            while True:
                try:
                    flickr_photos = flickr_api.Photo.search(
                        has_geo=1,
                        place_id=place["id"],
                        content_type=1,
                        per_page=100,
                        page=cur_page,
                        min_taken_date=date.date(),
                        max_taken_date=(date + datetime.timedelta(days=1)).date(),
                        extras="geo, date_taken",
                    )
                    for photo in flickr_photos:
                        photos.append(
                            Photo(
                                photo.id,
                                photo.owner.id,
                                photo.latitude,
                                photo.longitude,
                                photo.datetaken,
                            )
                        )
                        if photo_hash[photo.id] == "stored":
                            print("Repeated photo {} in the set".format(photo.id))
                            duplicates += 1
                        else:
                            photo_hash[photo.id] = "stored"
                    break
                except Exception as e:
                    print("Exception {}".format(e))
                    continue

    json_out_file = open("photo_info.json", "w")
    json.dump(photos, json_out_file, default=serialize, indent=2)
    json_out_file.close()

    json_out_file = open("processing_info.json", "w")
    json.dump(
        {"processed_photos": len(photos), "duplicates": duplicates},
        json_out_file,
        default=serialize,
        indent=2,
    )
    json_out_file.close()
