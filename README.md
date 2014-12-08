BP-diagrams
===========

Goal
----
Visualize BP (British Petroleum) Statistical Review of the World.
Choose between resource usage per capita, 
relative share of energy consumption and total energy consumption.

[View result](http://ivarref.github.io/bp-diagrams/).

About the data
--------------
The data is available as a TSV (Tab Separated Values) file [here](https://github.com/ivarref/bp-diagrams/blob/master/data/data.tsv). This file contains BP energy data mapped to World Bank population data.

The data is generated based on the [Mazama Science BP data set](http://mazamascience.com/OilExport/data.html) and the [okfn World Bank population data set](http://data.okfn.org/data/core/population).
Mapping between the World Bank countries and BP groups is specified in [gen_data.py](https://github.com/ivarref/bp-diagrams/blob/master/gen_data.py).

Notes
--------
* Coal production data available since 1980.
* Gas production data available since 1970.

Features
--------

* Compare countries or group of countries.
* Toggle resources (coal, oil, gas, nuclear, hydro and other renewables).
* Permalinks (normal and printer friendly).
* Show actual numbers option.
* Choose year to show actual numbers.
* Show production data.
* Net import/export show.

Plans for new features
----------------------

* GDP/PPP as alternative left y-axis.

TODOs
----------------------

* Clean up data filtering.
* Remove config variable?

Acknowledgements
----------------
[Mazama Science](http://mazamascience.com/OilExport/) for BP data set.

[okfn](http://data.okfn.org/data/core/population) for World Bank data set.

[Rune Likvern / Fractional Flow](http://fractionalflow.com/) for inspirings diagrams as well as feedback.


Comments
--------
refsdal.ivar@gmail.com

