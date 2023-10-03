import time
from datetime import datetime
import re
from unicodedata import normalize
from bs4 import BeautifulSoup

from modules.base_extractor import BaseExtractor
from utils import config as cfg
from data_model import db_model


class DetailsExtractor(BaseExtractor):   
        
    def get_offers_details(self):

        offers_to_process = self.load_offers_from_db()
        print(f'Loaded {len(offers_to_process)} offers from DB.')
        remaining = len(offers_to_process)
        
        for offer_id, url in offers_to_process.items():
            print(f'Getting details for: {url}. Remaining: {remaining}')
            details = self.get_offer_details(url)
            if not details: # try again (consent error)
                print('Getting details failed! Trying again...')
                details = self.get_offer_details(url)
            # update database
            self.update_offer_details(offer_id)
            self.save_raw_offer_details_to_db(offer_id, details)

            remaining -= 1


    def get_offer_details(self, url):
        url = 'https://www.sreality.cz' + url
        
        
        self.driver.get(url)
        time.sleep(0.5)

        #cerate soup object
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        try:

            info = self.extract_info(soup)
            description = self.extract_description(soup)
            params = self.extract_params(soup)
            maps_link = self.extract_maps_link(soup)
            if maps_link and description and params and info:
                coordinates = self.parse_coordinates(maps_link)
                return {
                    "info": info, "description": description, "parameters": params,
                    "maps_link": maps_link, "coordinates": coordinates
                }
            else:
                return None
        except:
            print('Failed!')
            return None
    
    def load_offers_from_db(self):
        """Load offers without details from database."""
        offers_query = self.session.query(db_model.OffersRaw).join(db_model.Offers).filter(db_model.Offers.details == False)
        offers_to_process = {}
        for offer in offers_query.all():
            offers_to_process[offer.id_offer] = offer.offer_raw['link']
        return offers_to_process
    
    def update_offer_details(self, offer_id):
        """Creates record in Offers table (or updates existing)."""
        # check if id is already in the databse
        offers_query = self.session.query(db_model.Offers).filter(db_model.Offers.id_offer == offer_id)
        offers_updates_data = offers_query.all()
        # Check if we already have offer id in the DB
        if len(offers_updates_data) > 0:
            self.session.query(db_model.Offers).filter(db_model.Offers.id_offer == offer_id).update(
                {
                    db_model.Offers.details: True,
                }, synchronize_session = False)
            
        else:
            print(f'Failed to update {offer_id}!')
        self.session.commit()

    def save_raw_offer_details_to_db(self, offer_id, offer_details_raw):
        """Saves raw offer record to database."""
        offer_details_add = db_model.OffersDetailsRaw(
            id_offer = offer_id,
            offer_details_raw = offer_details_raw,
            timestamp = datetime.now()
        )
        self.session.add(offer_details_add)
        self.session.commit()

    @staticmethod
    def extract_params(soup_object):
        """Extracts parameters of the offer."""
        results = soup_object.find(class_="property-detail ng-scope")

        if results:
            job_elements = results.find_all("li", class_="param ng-scope")
            params = {}
            for job_element in job_elements:
                item = job_element.contents[0].contents[0]
                val_find = job_element.find("span", class_="ng-binding ng-scope")
                val = val_find.contents if val_find is not None else None
                if not val: # not a value -> true or false icons
                    # look for true icon
                    true_find = job_element.find("span", class_="icof icon-ok ng-scope")
                    if true_find and true_find.attrs['ng-if'] == "item.type == 'boolean-true'":
                        params[item] = True
                        continue
                    # look for false icon
                    false_find = job_element.find("span", class_="icof icon-cross ng-scope")
                    if false_find and false_find.attrs['ng-if'] == "item.type == 'boolean-false'":
                        params[item] = False
                        continue
                    # otherwise return none
                    params[item] = None
                else:
                    params[item] = val[0]
            return params
        else:
            return None
    
    @staticmethod
    def extract_description(soup_object):
        """Extracts the description of the offer."""
        results = soup_object.find(class_="description ng-binding")

        if results:
            job_elements = results.find_all("p")
            description = []
            for job_element in job_elements:
                if len(job_element.contents) > 0 and isinstance(job_element.contents[0], str):
                    description.append(job_element.contents[0])
            return '\n'.join(description)
        else:
            return None
        
    @staticmethod
    def extract_maps_link(soup_object):
        """Extracts gps coordinates of the offer"""
        results = soup_object.find(class_="hud")

        if results:
            job_elements = results.find_all("a")
            for job_element in job_elements:
                if 'href' in job_element.attrs and 'mapy' in job_element.attrs['href']:
                    return job_element.attrs['href']
            return None
        else:
            return None
        
    @staticmethod
    def extract_info(soup_object):
        """Extracts the description of the offer."""
        results = soup_object.find(class_="property-title")

        if results:
            name = results.find("span", class_ = "name ng-binding")
            location = results.find("span", class_ = "location-text ng-binding")
            price = results.find("span", class_ = "norm-price ng-binding")
            ee_type = results.find("span", class_ = "energy-efficiency-rating__type ng-binding")
            ee_text = results.find("span", class_ = "energy-efficiency-rating__text ng-binding")

            info = {
                "Name": normalize('NFKD',name.contents[0]),
                "Location": location.contents[0],
                "Price": normalize('NFKD',price.contents[0]),
                "Energy Efficiency Type": ee_type.contents[0] if ee_type is not None else None,
                "Energy Efficiency Text": ee_text.contents[0] if ee_text is not None else None
            }
            return info
        else:
            return None
        
    @staticmethod
    def parse_coordinates(maps_link):
        """Returns x and y coordinates from maps.cz link."""
        regex = r'x=([-+]?\d*\.\d+|\d+)&y=([-+]?\d*\.\d+|\d+)'

        match = re.search(regex, maps_link)
        if match:
            x_coordinate = match.group(1)
            y_coordinate = match.group(2)
            return (x_coordinate, y_coordinate)
        else:
            print('Failed to parse coordinates!')
            return None
