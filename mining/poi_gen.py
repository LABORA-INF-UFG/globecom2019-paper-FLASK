# -*- coding: utf-8 -*-
import googlemaps
from datetime import datetime
from unidecode import unidecode
import os
import time
import json


def serialize(obj):
    return obj.__dict__


class POI:
    def __init__(self, name, latitude, longitude, avg_rating, num_ratings, type):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.avg_rating = avg_rating
        self.num_ratings = num_ratings
        self.categories = []
        self.type = type

    def __hash__(self):
        return hash((self.name, self.latitude, self.longitude))

    def add_category(self, category):
        self.categories.append(category)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.name == other.name
            and self.latitude == other.latitude
            and self.longitude == other.longitude
        )


categories = [
    "Historical",
    "Cultural",
    "Park",
    "Museum",
    "Shopping",
    "Building",
    "Architectural",
    "Religion",
    "Transport",
    "Structure",
    "Entertainment",
    "Education",
    "Amusement",
    "Beach",
    "Precinct",
    "Sport",
    "Palace",
    "Zoo",
]

cities = [
    "London",
    "Madrid",
    "Barcelona",
    "Athens",
]

city_to_folder = {
    "London": "london",
    "Madrid": "madrid",
    "Barcelona": "barcelona",
    "Athens": "athens",
}

gmaps = googlemaps.Client(key="")
custom_query = "{} point of interest {}"
RUNNING_DIR = os.path.dirname(os.path.abspath(__file__))


def get_pois(city, category):
    pois = []

    request = do_request(custom_query.format(city, category))

    # print request["results"];

    for poi in request["results"]:
        added_pois = [x for x in all_pois[city] if x.name == unidecode(poi["name"])]
        if len(added_pois) == 0:
            pois.append(
                POI(
                    unidecode(poi["name"]),
                    poi["geometry"]["location"]["lat"],
                    poi["geometry"]["location"]["lng"],
                    poi["rating"],
                    poi["user_ratings_total"],
                    poi["types"],
                )
            )
            pois[len(pois) - 1].add_category(category)
        else:
            all_pois[city][all_pois[city].index(added_pois[0])].add_category(category)

    while "next_page_token" in request:
        time.sleep(1)
        request = do_request(
            custom_query.format(city, category), request["next_page_token"]
        )

        for poi in request["results"]:
            added_pois = [x for x in all_pois[city] if x.name == unidecode(poi["name"])]
            if len(added_pois) == 0:
                pois.append(
                    POI(
                        unidecode(poi["name"]),
                        float(poi["geometry"]["location"]["lat"]),
                        float(poi["geometry"]["location"]["lng"]),
                        float(poi["rating"]),
                        int(poi["user_ratings_total"]),
                        poi["types"],
                    )
                )
                pois[len(pois) - 1].add_category(category)
            else:
                all_pois[city][all_pois[city].index(added_pois[0])].add_category(
                    category
                )

    return pois


def do_request(query_, page_token_=None):
    while True:
        try:
            request = gmaps.places(query=query_, page_token=page_token_)
        except Exception as e:
            print(e)
            continue
        break

    return request


all_pois = {}


def gen_pois():
    for city in cities:
        all_pois[city] = []
        for category in categories:
            all_pois[city] = all_pois[city] + get_pois(city, category)

        all_pois[city] = filter(lambda x: x.avg_rating >= 4.0, all_pois[city])
        all_pois[city].sort(key=lambda x: x.num_ratings, reverse=True)

        os.chdir("{}/../data/{}".format(RUNNING_DIR, city_to_folder[city]))
        json_out_file = open("poi_info.json", "w")
        json.dump(all_pois[city][:30], json_out_file, default=serialize, indent=2)
        json_out_file.close()


# gen_pois()


def process_distance_matrix():
    edges = []

    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city_to_folder[city]))
        pois_file = open("poi_info.json")
        pois_data = json.load(pois_file)
        pois_file.close()

        for origin in pois_data:
            for destination in pois_data:
                if origin["name"] != destination["name"]:
                    pair_origin = (
                        float(origin["latitude"]),
                        float(origin["longitude"]),
                    )
                    pair_destination = (
                        float(destination["latitude"]),
                        float(destination["longitude"]),
                    )
                    print(pair_origin)
                    print(pair_destination)
                    result = gmaps.distance_matrix(
                        pair_origin, pair_destination, mode="walking"
                    )

                    edge = {
                        "from": origin["id"],
                        "from_name": origin["name"],
                        "to": destination["id"],
                        "to_name": destination["name"],
                        "duration": result["rows"][0]["elements"][0]["duration"][
                            "value"
                        ],
                        "distance": result["rows"][0]["elements"][0]["distance"][
                            "value"
                        ],
                    }
                    print(edge)

                    edges.append(edge)

        json_out_file = open("distance_matrix.json", "w")
        json.dump(edges, json_out_file, default=serialize, indent=2)
        json_out_file.close()


def process_poi_popularity():
    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city_to_folder[city]))

        poi_info_file = open("poi_info.json")
        sequences_file = open("sequences_processed.json")

        poi_info_data = json.load(poi_info_file)
        sequences_data = json.load(sequences_file)

        poi_info_file.close()
        sequences_file.close()

        visits_per_category = {}
        visits = [0] * 31

        for cat in categories:
            visits_per_category[cat] = 0

        for seq in sequences_data:
            for visit in seq["photos"]:
                visits[int(visit["poi_id"])] += 1

        for poi in poi_info_data:
            poi["popularity"] = visits[int(poi["id"])]
            for cat in poi["categories"]:
                visits_per_category[cat] += visits[int(poi["id"])]

        for poi in poi_info_data:
            most_popular = ""
            most_popular_value = -1

            for cat in poi["categories"]:
                if visits_per_category[cat] > most_popular_value:
                    most_popular_value = visits_per_category[cat]
                    most_popular = cat

            poi["most_popular_category"] = most_popular

        json_out_file = open("poi_info.json", "w")
        json.dump(poi_info_data, json_out_file, default=serialize, indent=2)
        json_out_file.close()


def generate_pois_file():
    for city in cities:

        os.chdir("{}/../data/{}".format(RUNNING_DIR, city_to_folder[city]))

        poi_info_file = open("poi_info.json")
        pois_file = open("pois.in", "w")

        poi_info_data = json.load(poi_info_file)
        poi_info_file.close()

        for poi in poi_info_data:
            pois_file.write(
                "{} {} {} {} {} {}\n".format(
                    poi["id"],
                    poi["name"].replace(" ", "_"),
                    poi["latitude"],
                    poi["longitude"],
                    poi["popularity"],
                    poi["most_popular_category"],
                )
            )

        pois_file.close()


def generate_pois_travel_time_file():
    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city_to_folder[city]))

        distance_matrix_file = open("distance_matrix.json")
        pois_travel_time_file = open("pois_travel_time.in", "w")

        distance_matrix_data = json.load(distance_matrix_file)
        distance_matrix_file.close()

        for pair in distance_matrix_data:
            pois_travel_time_file.write(
                "{} {} {}\n".format(pair["from"], pair["to"], pair["duration"])
            )

        pois_travel_time_file.close()


# process_distance_matrix()
"""
for city in cities:
	os.chdir("{}/data/{}".format(RUNNING_DIR, city_to_folder[city]))
	pois_file = open("poi_info.json")
	pois_data = json.load(pois_file)

	count_id = 1
	for poi in pois_data:
		poi["id"] = count_id
		count_id = count_id + 1

	pois_file.close()

	json_out_file = open("poi_info.json", "w")
	json.dump(pois_data, json_out_file, default=serialize, indent=2)
	json_out_file.close()
"""


def main():
    process_poi_popularity()
    generate_pois_file()
    generate_pois_travel_time_file()


if __name__ == "__main__":
    main()
