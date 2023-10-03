from datetime import datetime

from utils import config as cfg
from utils.db_adapter import DBAdapter

from data_model.db_model import Offers
from modules.offer_extractor import OfferExtractor
from modules.details_extractor import DetailsExtractor


if __name__ == '__main__':

    local_db = DBAdapter(
            database_name = cfg.DB_NAME,
            host = cfg.DB_HOST,
            user = cfg.DB_USER,
            password = cfg.DB_PASS,
            port= cfg.DB_PORT
            )
    db_session = local_db.get_session()



    extractor = OfferExtractor(db_session)
    extractor.get_offers()



    detail_extractor = DetailsExtractor(db_session)
    detail_extractor.get_offers_details()


    print('stop')

