from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    orange = "\x1b[38;5;209m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: orange + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(gray){asctime}(reset) (levelcolor){levelname:<8}(reset) {message}"
        format = format.replace("(gray)", self.gray + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("Scrapping")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
logger.addHandler(console_handler)


def acceptCGU(page) -> None:
    btn = page.get_by_role("button", name="Tout accepter")
    btn.wait_for()
    btn.click()


def fillSearchBar(page, content: str) -> None:
    searchBar = page.locator("input#searchboxinput")
    searchBar.wait_for()
    searchBar.fill(content)
    time.sleep(.5)
    loupe = page.locator("button#searchbox-searchbutton")
    loupe.click()
    time.sleep(1)
    page.locator("h1.fontTitleLarge.IFMGgb").wait_for()


def Scrolling(page, countFactor: int = 5) -> None:
    page.mouse.move(150, 150)
    counts = []
    scrolling = True
    while scrolling:
        page.mouse.wheel(0, 10000)
        htlmElems = page.inner_html("div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd")
        counts.append(
            len(
                BeautifulSoup(htlmElems, "html.parser").find_all(
                    "div", {"class": ["Nv2PK", "THOPZb", "CpccDe"]}
                )
            )
        )
        if len(counts) >= countFactor and len(set(counts[-countFactor:])) == 1:
            scrolling = False
        elif len(set(counts[-2:])) == 1 and len(counts) > 1:
            time.sleep(1)
        time.sleep(0.25)


def getData(html:str,source:str) :

    def testNone(x): 
        return x.text if x != None else None


    json = {}
    soup = BeautifulSoup(html,"html.parser")

    json["link"] = source
    json["image"] = soup.find("img")["src"]
    json["nom"] = testNone(soup.find("h1",{"class": "DUwDvf lfPIob"}))
    json["note"] = testNone(soup.find("div",{"class": "F7nice"}))
    json["prix"] = testNone(soup.find("span",{"aria-label": "Prix: Abordable"}))
    json["adresse"] = testNone(soup.find("div",{"class": "AeaXub"}))
    json["info"] = str(soup.find_all("div",{"class": "Io6YTe fontBodyMedium kR99db"}))

    heures = soup.find("div",{"class": ["t39EBf","GUrTXd"]})
    if heures != None: 
        json["heures"] = heures["aria-label"].split(".")[0].split(";")
    else : 
        json["heures"] = None

    json["services"] = testNone(soup.find("div",{"class": "E0DTEd"}))
    json["type"] = testNone(soup.find("button",{"class": "DkEaL"}))
    return json


def saveHTML(html:str) -> None: 
    with open("htmlSample2.html","w",encoding="utf-8") as file : 
        file.write(html)

def split_list(input_list, size: int = 10) -> list:
    return [input_list[i : i + size] for i in range(len(input_list), size)]


if __name__ == "__main__":
    rechercheContent = "restaurants 59000"
    with sync_playwright() as p :
        logger.info("start")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.fr/maps")
        logger.info("goto https://www.google.fr/maps")
        
        # Acceptation des CGU
        acceptCGU(page=page)
        logger.info("CGU validé")

        # Remplissage de la barre de recherche
        fillSearchBar(page=page, content=rechercheContent)
        logger.info("Barre de recherche completé")

        # Scroll vers le bah pour plus de contenu 
        Scrolling(page=page)
        logger.info("Scroll Terminé")

        result = []
        elems = page.locator("a.hfpxzc").all()

        logger.info(f"{len(elems)} éléments trouvés")
        last =""
        for e in elems[:25]:
            e.click()
            while page.locator("div.bJzME.Hu9e2e.tTVLSc").inner_html() == last :
                logger.debug("wait")
                time.sleep(.1)
            elemhtml = page.locator("div.bJzME.Hu9e2e.tTVLSc").inner_html()
            result.append(getData(elemhtml,e.get_attribute("href")))
            time.sleep(.5)

        time.sleep(1)
        browser.close()
        logger.info("données collecté")

        data = pd.DataFrame(result)
        data.reset_index(inplace=True)
        data.to_json("data.json")
        logger.info("données enregistré")
        logger.info("end")

