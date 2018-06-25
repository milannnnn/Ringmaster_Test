import requests
import xml.etree.ElementTree as ET
import pandas as pd
import logging
import json
from io import BytesIO

# logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

class Parser:

    def __init__(self, xml_url=None, csv_url=None, json_url=None):

        self.logger = logging
        self.xml_url = xml_url or 'https://data.cityofnewyork.us/api/views/kku6-nxdu/rows.xml?accessType=DOWNLOAD'
        self.csv_url = csv_url or 'https://data.ny.gov/api/views/juva-r6g2/rows.csv?accessType=DOWNLOAD'
        self.json_url = json_url or 'https://data.ny.gov/api/views/ieqx-cqyk/rows.json?accessType=DOWNLOAD'

    def get_xml_df(self):
        file = self.download_file(self.xml_url)
        if file:
            return self.parse_xml_to_df(file)
        else:
            return None

    def get_csv_df(self):
        file = self.download_file(self.csv_url)
        if file:
            return self.parse_csv_to_df(file)
        else:
            return None

    def get_json_df(self):
        file = self.download_file(self.json_url)
        if file:
            return self.parse_json_to_df(file)
        else:
            return None

    @staticmethod
    def download_file(url):

        # Try to download the file:
        try:
            data = requests.get(url)

            # If download is successful (code=200) - return the file
            if data.status_code == 200:
                logging.info("File downloaded successfully!")
                return data.content

            # If unsuccessful - throw an exception:
            else:
                raise Exception(str(data.status_code))

        # Handle possible exceptions:
        except requests.ConnectionError:
            logging.error('Connection error occurred - Please check your connection and provided URL!')
        except Exception as e:
            logging.error('Download error ' + str(e) + ' occurred - Please check the provided URL!')
        return None

    @staticmethod
    def parse_xml_to_df(file):

        # If the XML file is already downloaded - start parsing:
        if file:

            # Read in the XML file:
            try:
                xml_tree = ET.XML(file)
            except Exception:
                logging.error('Given XML file is corrupt - please check if downloaded properly!')
                return None

            # Extract data from xml (data is located in the 2nd root):
            data = []
            for a in xml_tree:
                for b in a:
                    # Append the data to list:
                    data.append({c.tag: float(c.text) for c in b})

            # Parse the extracted data to Pandas DF:
            df = pd.DataFrame(data)
            logging.info("XML successfully parsed to Pandas DF!")

            if df.isnull().values.any():
                logging.warning("NAN values found in DF!")

            return df

        # If not - throw a file not found exception:
        else:
            logging.error('XML file not found - please check if downloaded properly!')
            return None

    @staticmethod
    def parse_csv_to_df(file):

        # Try to parse the raw CSV file to DF:
        try:
            df = pd.read_csv(BytesIO(file))
            return df
        except Exception:
            logging.error('Provided CSV file is corrupt - please check if downloaded properly!')
            return None

    @staticmethod
    def parse_json_to_df(file):

        # Try to parse the raw CSV file to DF:
        try:
            data = json.load(BytesIO(file))

            # Extract column names and description from json meta:
            col_names = {}
            col_descs = {}
            for i, col in enumerate(data['meta']['view']['columns']):

                if col['position']:
                    col_names[i] = col['name']
                    col_descs[i] = col['description']

            # Print column names and their descriptions (to mark required columns):
            # for key in col_names:
            #     print(key, '-', col_names[key])
            #     print(col_descs[key], '\n')

            # Select just columns of interest (county, zip and services):
            index_list = [16, 14] + list(range(18, 34))

            df = []

            # Extract required data from the json:
            for datapoint in data['data']:
                df.append([datapoint[i] for i in index_list])

            # Convert to pandas df:
            df = pd.DataFrame(df, columns=[col_names[i] for i in index_list], dtype=int)

            # Convert 'Y' and 'N' characters to 1 and 0 (for easier manipulation)
            df.iloc[:, 2:] = (df.iloc[:, 2:] == 'Y').astype(int)

            return df

        except Exception:
            logging.error('Provided JSON file is corrupt - please check if downloaded properly!')
            return None


if __name__ == '__main__':

    df = Parser().get_xml_df()
    print(df.head())
