import time
import json
from datetime import datetime

from unicodedata import normalize
from bs4 import BeautifulSoup
 
from utils import config as cfg
from data_model import db_model

from modules.base_extractor import BaseExtractor


class OfferExtractor(BaseExtractor):
        
    def get_offers_page(self, url):
        self.driver.get(url)

        time.sleep(0.5)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        results = soup.find(class_="dir-property-list")
        if results:

            job_elements = results.find_all("div", class_="property ng-scope")

            offers = []
            for job_element in job_elements:
                link = job_element.find("a", class_="title")
                locality = job_element.find("span", class_="locality ng-binding")
                price = job_element.find("span", class_="norm-price ng-binding")
                splitted = link.attrs['ng-href'].split('/')

                offer_raw = {
                    "id": splitted[6],
                    "type": splitted[3],
                    "rooms": splitted[4],
                    "link": link.attrs['ng-href'],
                    "locality": locality.contents[0],
                    "price": normalize('NFKD', price.contents[0]),
                }

                self.update_offer_table(offer_raw['id'])
                self.save_raw_offer_to_db(offer_raw)

                offers.append(offer_raw)
            return offers
        else:
            return None
    
    def get_offers(self):
        nr_total = self.get_number_of_offers()
        print(f"Found {nr_total} offers.")
        self.offer_list = {}
        for i in range(1,10):
            url = cfg.URL_BASE + f'?strana={i}'
            print('Scraping: ',url)
            offers_page = self.get_offers_page(url)
            if not offers_page: # try again in case of consent error
                print(f'Failed to scrape page {i}! Trying again...')
                offers_page = self.get_offers_page(url)

            self.offer_list[i] = offers_page

    def get_number_of_offers(self):
        """Return number of relevant offers to scrape."""
        self.driver.get(cfg.URL_BASE)

        time.sleep(0.5)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        results = soup.find(class_="dir-property-list")

        if not results:
            results = soup.find(class_="dir-property-list")

        if results:
            info_data = results.find_all("span", class_="numero ng-binding")
            return int(normalize('NFKD', info_data[1].contents[0]).replace(" ",""))
        else:
            return None

    
    @staticmethod
    def save_to_json(data):
        with open('out/results.json', 'w') as f:
            json.dump(data, f)

    def update_offer_table(self, offer_id):
        """Creates record in Offers table (or updates existing)."""
        # check if id is already in the databse
        offers_query = self.session.query(db_model.Offers).filter(db_model.Offers.id_offer == offer_id)
        offers_updates_data = offers_query.all()
        # Check if we already have offer id in the DB
        if len(offers_updates_data) > 0:
            updates = offers_updates_data[0].updates
            self.session.query(db_model.Offers).filter(db_model.Offers.id_offer == offer_id).update(
                {
                    db_model.Offers.updates: updates+1,
                    db_model.Offers.updated_on: datetime.now()
                }, synchronize_session = False)
            
        # Add new offer ID to the Offers table
        else:
            offer_add = db_model.Offers(
                id_offer=offer_id, 
                updates=1, 
                details=False,
                created_on=datetime.now(),
                updated_on=datetime.now()
                )
            self.session.add(offer_add)
        self.session.commit()

    def save_raw_offer_to_db(self, offer_raw):
        """Saves raw offer record to database."""
        offer_raw_add = db_model.OffersRaw(
            id_offer = offer_raw['id'],
            offer_raw = offer_raw,
            timestamp = datetime.now()
        )
        self.session.add(offer_raw_add)
        self.session.commit()
