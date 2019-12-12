# n5GTour - GLOBECOM 2019

n5GTour is a framework for the optimized design of recommending personalized multi-user itineraries. n5G considers:

* Tourist preferences
* Efficient allocation of edge cloud resources
* Advanced aplications' performance

For more information about how n5GTour operates, please refer to the work that gave origin to it, named **Personalized Travel Itineraries with Multi-access Edge Computing Touristic Services**, which can be accessed [here](https://github.com/LABORA-INF-UFG/globecom2019-paper-FLASK)

# Getting started

Phase A of nG5Tour, responsible for generating itineraries, is written in **C++** and is located at `espprc` folder. Please ensure that you have [boost](https://www.boost.org/) library installed before executing the makefile

Phase B, reponsilbe for allocationg resources, is written in **Python** and is the file `n5GTour.py` located at root. Please ensure that CPLEX is present and that you have the following libraries installed:

* networkx
* docplex

# Contribute

Contributions are welcome, the process is as simple as cloning, making changes and submitting a pull request

# Citing this work

If you make use of n5GTour or of its dataset, please cite the following work:

```
@inproceedings{fonseca:hal-02285929,
  TITLE = {{Personalized Travel Itineraries with Multi-access Edge Computing Touristic Services}},
  AUTHOR = {Fonseca, Felipe and Mamatas, Lefteris and Carneiro Viana, Aline and Correa, Sand L and Cardoso, Kleber V},
  URL = {https://hal.inria.fr/hal-02285929},
  BOOKTITLE = {{Accepted for publication: IEEE Globecom}},
  ADDRESS = {Big Island, Hawaii, United States},
  YEAR = {2019},
  MONTH = Dec,
  KEYWORDS = {5g ; Personalized Travel Itineraries ; Multi-access Edge Computing ; Network Slicing},
  PDF = {https://hal.inria.fr/hal-02285929/file/main.pdf},
  HAL_ID = {hal-02285929},
  HAL_VERSION = {v1},
}
```

# Contact the authors

* fonsecafel@gmail.com
* kleber@inf.ufg.br
* sand@inf.ufg.br

Research group website: https://labora.inf.ufg.br