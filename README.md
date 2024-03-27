To run the experiment scripts, you need to install the following Python packages:
pysat
networkx
To run the CSV Merger, you need to install:
pandas
To run the Instance scraper, you need to install:
bs4 (beautifulsoup4)

To start the experiment, just run experiment.py.

The instances used in the experiment are in the .col format and should be placed in the instance folder. 
These instances are sourced from [COLOR08](https://mat.tepper.cmu.edu/COLOR08/).
Please note that not all instances from this website are used in our experiment.
The CSV files generated by our experiment are included in the repository for reference.

Merging result CSV's:
The CSV files generated by the experiment script should be placed in the csv folder. 
The merger script merges these CSV files and creates a new CSV file containing the average of all the data.

The scraper script downloads all the instances from [COLOR08](https://mat.tepper.cmu.edu/COLOR08/).

