#include "tourist/POIContainer.h"

#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>

#include "tourist/POI.h"

using namespace std;

POIContainer::POIContainer() {
  num_of_pois_ = 0;
  pois_.push_back(new POI(0, "", 0, 0, "", 0));
}

void POIContainer::AddPoi(POI* p) {
  pois_.push_back(p);
  num_of_pois_++;
}

double POIContainer::GetTimeBetweenPOIs(int p1_id, int p2_id,
                                        string travelMethod) {
  if (travelMethod == "walking") {
    return distance_[p1_id][p2_id];
  }
}

void POIContainer::SetDistanceBetweenPOIs(int p1_id, int p2_id, double value) {
  // cout << "inside pc 1 with " << num_of_pois_ << " pois " << endl;
  if (distance_.size() == 0) {
    // cout << "inside pc 1" << endl;
    distance_.resize(num_of_pois_ + 1);
    for (int i = 0; i <= num_of_pois_; i++) {
      distance_[i].resize(num_of_pois_ + 1);
    }
  }

  distance_[p1_id][p2_id] = value;
  distance_[p2_id][p1_id] = value;
}