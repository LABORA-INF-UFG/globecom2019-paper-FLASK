#ifndef TOURIST_POI_CONTAINER_H_
#define TOURIST_POI_CONTAINER_H_

#include <iostream>
#include <vector>

#include "tourist/POI.h"

using namespace std;

class POIContainer {
 public:
  explicit POIContainer();

  int GetNumOfPOIs() { return num_of_pois_; }
  POI* GetPOIById(int poi_id) { return pois_[poi_id]; }
  void AddPoi(POI* p);
  double GetDistanceBetweenPOIs(int p1_id, int p2_id) {
    return distance_[p1_id][p2_id];
  }
  double GetTimeBetweenPOIs(int p1_id, int p2_id, string travelMethod);
  void SetDistanceBetweenPOIs(int p1_id, int p2_id, double value);

 private:
  int num_of_pois_;
  std::vector<POI*> pois_;
  std::vector<std::vector<double> > distance_;
};

#endif