from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, TIMESTAMP, text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import INTEGER


Base = declarative_base()
metadata = Base.metadata

class Offers(Base):
    __tablename__ = 'offers'

    id_offer = Column(String(255), primary_key = True)
    updates = Column(INTEGER(5))
    details = Column(Boolean)
    created_on = Column(TIMESTAMP, nullable=False)
    updated_on = Column(TIMESTAMP, nullable=False)


class OffersRaw(Base):
    __tablename__ = 'offers_raw'

    id = Column(INTEGER(11), primary_key = True, autoincrement=True)
    id_offer = Column(String(255), ForeignKey(Offers.id_offer), nullable=False)
    offer_raw = Column(JSON)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

class OffersDetailsRaw(Base):
    __tablename__ = 'offers_details_raw'

    id = Column(INTEGER(11), primary_key = True, autoincrement=True)
    id_offer = Column(String(255), ForeignKey(Offers.id_offer), nullable=False)
    offer_details_raw = Column(JSON)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

