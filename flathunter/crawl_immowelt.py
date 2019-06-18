import logging
import requests
import re
from bs4 import BeautifulSoup


class CrawlImmowelt:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.immowelt\.de')

    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_results(self, search_url):
        self.__log__.debug("Got search URL %s" % search_url)

        soup = self.get_page(search_url)

        # get data from first page
        entries = self.extract_data(soup)
        self.__log__.debug('Number of found entries: ' + str(len(entries)))

        return entries

    def get_page(self, search_url):
        resp = requests.get(search_url)  # TODO add page_no in url
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'html.parser')

    def extract_data(self, soup):
        entries = []
        soup = soup.find(id="listItemWrapperFixed")
        try:
            title_elements = soup.find_all("h2")
        except AttributeError:
            return entries
        expose_ids=soup.find_all("div", class_="listitem_wrap")


        #soup.find_all(lambda e: e.has_attr('data-adid'))
        #print(expose_ids)
        for idx,title_el in enumerate(title_elements):
			
            tags = expose_ids[idx].find_all(class_="hardfact")
            url = "https://www.immowelt.de/" +expose_ids[idx].find("a").get("href")
            address = expose_ids[idx].find(class_="listlocation")
            address.find("span").extract()
            print(address.text.strip())
            address = address.text.strip()
			
            try:
                print(tags[0].find("strong").text)
                price = tags[0].find("strong").text.strip()
            except IndexError:
                print("Kein Preis angegeben")
                price = "Auf Anfrage"

            try:
                tags[1].find("div").extract()
                print(tags[1].text.strip())
                size = tags[1].text.strip()
            except IndexError:
                size = "Nicht gegeben"
                print("Quadratmeter nicht angegeben")				
				
            try:
                tags[2].find("div").extract()
                print(tags[2].text.strip())
                rooms = tags[2].text.strip()
            except IndexError:
                print("Keine Zimmeranzahl gegeben")
                rooms = "Nicht gegeben"
				
            details = {
                'id': int(expose_ids[idx].get("data-estateid")),
                'url':  url ,
                'title': title_el.text.strip(),
                'price': price,
                'size': size,
                'rooms': rooms ,
                'address': address
                'location': address ,
            }
            entries.append(details)
        
        self.__log__.debug('extracted: ' + str(entries))

        return entries

    def load_address(self, url):
        # extract address from expose itself
        exposeHTML = requests.get(url).content
        exposeSoup = BeautifulSoup(exposeHTML, 'html.parser')
        try:
            street_raw = exposeSoup.find(id="street-address").text
        except AttributeError:
            street_raw=""
        try:
            address_raw = exposeSoup.find(id="viewad-locality").text
        except AttributeError:
            address_raw =""
        address = address_raw.strip().replace("\n","") + " "+street_raw.strip()

        return address
