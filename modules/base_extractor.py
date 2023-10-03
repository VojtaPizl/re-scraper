from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options


from selenium.webdriver.chrome.service import Service as BraveService
from webdriver_manager.core.os_manager import ChromeType

from utils import config as cfg


class BaseExtractor:
    """Base extractor class"""
    def __init__(self, db_session):
        self.session = db_session
        if cfg.BROWSER == 'firefox':
            options = Options()
            options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=options,
                service=FirefoxService(GeckoDriverManager().install())
            )
        if cfg.BROWSER == 'chrome':
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install())
                )
        if cfg.BROWSER == 'brave':
            self.driver = webdriver.Chrome(
                service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install())
            )
