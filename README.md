# Explore_Webscraper
Webscraping financial data to help in predicting bankrupcy.

## Technical set-up
Ubuntu: 18.04<br/>
Python: 3.8.5<br/>
scrapy: 1.6.0<br/>
Firefox Browser: 85.0 (64-bit)<br/>
Gecko Driver: v0.28.0-linux64 

### Note on drivers
I use firefix so I used the firefox bowser along with the gecko driver defined above. You can find more information about selenium drivers [here](https://selenium-python.readthedocs.io/installation.html#drivers), if you want to use other drivers. The download page for the driver I used (I think there is an updated version) [here](https://github.com/mozilla/geckodriver/releases).

## Running the spiders
Make sure that when you are going to run a spider you are two directories above the spider folder. You should be in the following directory:

*/Explore_Webscraper/explore_webscraper

## Throttling
Throttling is used to reduce the number of calls to a single domain. If there are too many requests then the server will not be able to handle the requests fast enough and it will return errors. This will cause a loss of data. The throttling parameters can be found in the the settings file. Throttling was used for all spiders

## Pipelines
Pipelines were used when collecting the financial and status information because it allowed them to run smoothly in parallel. When running the companies_filtering and board spiders please ensure that ITEM_PIPELINE is commented out in the settings file. It must be uncommented out when running the driver file. Also make sure when running the driver file that the files you are writting to in the pipeline are correct for you.

## Company names and id collection
First disable the ITEM_PIPELINES middleware by commenting it out in the settings file. It is commented out by default.

Run the following command to start and run the companies_filtering.py spider:

```bash
$ scrapy crawl companies_filtering 
```

If you want to store your data in a file run the following command:

```bash
$ scrapy crawl companies_filtering -o path_to_file/file.(csv, json)
```

You need to specify either a .csv or .json file extension.

## Financials and status collection
First enable the ITEM_PIPELINES middleware by uncommenting it out in the settings file. Also ensure that throttling is enabled. Set the throttling parameters to what will maximise the speed and minimize the 503 errors over your network. Also make sure that the pipelines code is writing to the file that you want to write to.

Use the following command to run the financials and status spiders in parallel:

```bash
python3 driver
```

## Board collection
First disable the ITEM_PIPELINES middleware by commenting it out in the settings file. Also ensure that throttling is enabled. Set the throttling parameters to what will maximise the speed and minimize the 503 errors over your network.

Run the following command to start and run the board.py spider:

```bash
$ scrapy crawl board 
```

If you want to store your data in a file run the following command:

```bash
$ scrapy crawl board -o path_to_file/file.(csv, json)
```

You need to specify either a .csv or .json file extension.

## Notebooks

### Name and ID Collection Notebook
The notebook in this folder is used to merge the ID and name batch data into one full dataset with all the IDs and names of the companies. It also filters out the companies with XXXX in the IDs as most of them do not have financials.

### Cleaning Notebooks
These notebooks are used to merge and clean the financials, status and board datasets into the full feature dataset. There are a number of notebooks in this directory but the ones labeled with (1), (2) and (3) correspond to the final notebooks used to clean the data. These notebooks should also be used in that order. The other notebooks were used in intermediate steps. Notebooks (1) and (2) were used to create the dataset prior to adding the board information. Notebook (3) added the board dataset that created the final dataset.

### Modeling Notebooks
These notebooks were used to create some basic models and investigate methods that worked best. The three notebooks correspond to modeling done at slightly different times in the data collection process. 'Testing methods on how to deal with unbalanced data.ipynb' was used to test how different and default model performed on unbalanced data, using only the status and financial information. 'Board_data_modeling.ipynb' was used to assess the predictive power of the board features in isolation from the other financial and status information. 'Modeling with new features.ipynb' first assess models run without board information and then with board information to see how the board features add to the predictive power of the models.