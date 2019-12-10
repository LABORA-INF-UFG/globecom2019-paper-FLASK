from haversine import haversine
import json
import os
import time
from datetime import datetime
from collections import defaultdict


def serialize(obj):
    return obj.__dict__


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.photos = []


class Visit:
    # def __init__(self, seq_id, poi_id, )
    pass


class Sequence:
    def __init__(self, seq_id, start_time):
        self.seq_id = seq_id
        self.photos = []
        self.start_time = start_time

    # def add_visit(self, visit):
    # 	self.duration += visit.duration
    # 	if self.duration <= 28800:
    # 		self.visits.append
    # 		return True
    # 	ese:
    # 		self.duration -= visit.duration

    def add_photo(self, photo):
        start_dt = datetime.strptime(self.start_time, DATE_MASK)
        end_dt = datetime.strptime(photo["date_taken"], DATE_MASK)
        if (end_dt - start_dt).total_seconds() <= 28800:
            self.photos.append(photo)
            return True
        else:
            return False


class Photo:
    def __init__(self, poi_id, timestamp):
        self.poi_id = poi_id
        self.timestamp = timestamp


RUNNING_DIR = os.path.dirname(os.path.abspath(__file__))

cities = ["london", "barcelona", "madrid", "athens"]

user_ids = {}

DATE_MASK = "%Y-%m-%d %H:%M:%S"


def pair_photos_to_pois():
    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city))
        photos_file = open("photo_info.json")
        pois_file = open("poi_info.json")

        photos_data = json.load(photos_file)
        photos_processed = []
        pois_data = json.load(pois_file)

        photos_file.close()
        pois_file.close()
        photo_num = 1

        photo_hash = {}
        photo_hash = defaultdict(lambda: -1, photo_hash)

        for photo in photos_data:
            # if photo["user_id"] not in user_ids:
            # 	user_ids[photo["user_id"]] = []

            # print "Processing photo {} of {}".format(photo_num, len(photos_data))
            photo["timestamp"] = time.mktime(
                datetime.strptime(photo["date_taken"], DATE_MASK).timetuple()
            )
            if photo_hash[photo["photo_id"]] == "stored":
                continue
            else:
                photo_hash[photo["photo_id"]] = "stored"

            poi_distances = []

            for poi in pois_data:
                photo_lat = float(photo["lat"])
                photo_long = float(photo["long"])
                poi_lat = float(poi["latitude"])
                poi_long = float(poi["longitude"])

                distance = haversine((photo_lat, photo_long), (poi_lat, poi_long))
                poi_distances.append((int(poi["id"]), distance))

            poi_distances.sort(key=lambda x: x[1])
            if (poi_distances[0][1] * 1000) <= 200:
                photo["poi_id"] = poi_distances[0][0]
            else:
                photo["poi_id"] = -1

            photo_num = photo_num + 1
            photos_processed.append(photo)

        print(
            "Processed {} and removed {} duplicates, leaving {} photos".format(
                len(photos_data),
                len(photos_data) - len(photos_processed),
                len(photos_processed),
            )
        )
        photos_processed = list(filter(lambda x: x["poi_id"] != -1, photos_processed))
        photos_processed.sort(key=lambda x: (x["user_id"], x["timestamp"]))

        json_out_file = open("photo_info_processed.json", "w")
        json.dump(photos_processed, json_out_file, indent=2)
        json_out_file.close()


def make_sequences():
    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city))

        photos_file = open("photo_info_processed.json")
        photos_data = json.load(photos_file)
        photos_file.close()

        seqs_processed = []

        next_seq_id = 1

        for photo in photos_data:
            # if photo["user_id"] not in user_ids:
            # 	user_ids[photo["user_id"]] = []

            if next_seq_id == 1:
                seq = Sequence(next_seq_id, photo["date_taken"])
                seq.add_photo(photo)
                next_seq_id += 1
            elif photo["user_id"] != old_photo["user_id"]:
                seqs_processed.append(seq)
                seq = Sequence(next_seq_id, photo["date_taken"])
                seq.add_photo(photo)
                next_seq_id += 1
            else:
                if seq.add_photo(photo) == False:
                    seqs_processed.append(seq)
                    seq = Sequence(next_seq_id, photo["date_taken"])
                    seq.add_photo(photo)
                    next_seq_id += 1

            old_photo = photo

        for seq in seqs_processed:
            seq.repeated_visit = False
            seq.null_visit = False
            seq.short_seq = False
            visited = [0] * 31
            old_photo = seq.photos[0]
            for photo in seq.photos:
                if old_photo["poi_id"] != photo["poi_id"]:
                    if visited[int(photo["poi_id"])] > 0:
                        seq.repeated_visit = True
                visited[int(photo["poi_id"])] += 1
                old_photo = photo

            visited_pois = 0
            for i in range(1, 31):
                if visited[i] == 1:
                    seq.null_visit = True
                if visited[i] > 0:
                    visited_pois += 1

            if visited_pois < 3:
                seq.short_seq = True

        seqs_processed = filter(lambda x: x.repeated_visit != True, seqs_processed)
        seqs_processed = filter(lambda x: x.null_visit != True, seqs_processed)
        # seqs_processed = filter(lambda x: x.short_seq != True, seqs_processed)

        users_dict = {}
        users_dict = defaultdict(lambda: False, users_dict)

        users_visits = {}
        users_visits = defaultdict(lambda: 0, users_visits)

        for seq in seqs_processed:
            users_visits[seq.photos[0]["user_id"]] += 1
            if seq.short_seq == False:
                users_dict[seq.photos[0]["user_id"]] = True

        aux = 0

        for user in users_dict:
            if users_visits[user] >= 2:
                aux += 1

        print(aux)

        json_out_file = open("sequences_processed.json", "w")
        json.dump(seqs_processed, json_out_file, default=serialize, indent=2)
        json_out_file.close()
        print("Num seqs {}".format(len(seqs_processed)))


def generate_user_visits_file():
    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city))

        sequences_file = open("sequences_processed.json")
        user_visits_file = open("user_visits.in", "w")
        sequences_data = json.load(sequences_file)
        sequences_file.close()

        for seq in sequences_data:
            for visit in seq["photos"]:
                # visit_timestamp = time.mktime(datetime.strptime(visit["date_taken"], DATE_MASK).timetuple())
                user_visits_file.write(
                    "{} {} {} {}\n".format(
                        visit["user_id"],
                        visit["timestamp"],
                        visit["poi_id"],
                        seq["seq_id"],
                    )
                )

        user_visits_file.close()


def main():
    pair_photos_to_pois()
    make_sequences()
    generate_user_visits_file()
    for city in cities:
        os.chdir("{}/../data/{}".format(RUNNING_DIR, city))

        sequences_file = open("sequences_processed.json")
        sequences_data = json.load(sequences_file)
        sequences_file.close()
        users_visits = {}
        users_visits = defaultdict(lambda: 0, users_visits)

        for seq in sequences_data:
            users_visits[seq["photos"][0]["user_id"]] += 1

        aux = 0
        for user in users_visits:
            if users_visits[user] > 1:
                aux += 1

        print(aux)


if __name__ == "__main__":
    main()
