from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import sys
import re


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
    time.sleep(0.5)
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


def testNone(x):
    return x.text if x is not None else None


def getData(html: str, elemsource: str):
    sourceSoup = BeautifulSoup(elemsource.inner_html(), "html.parser")

    json = {}
    soup = BeautifulSoup(html, "html.parser")

    json["gmapLink"] = sourceSoup.find("a", {"class": "hfpxzc"})["href"]
    json["image"] = soup.find("img")["src"]
    json["name"] = testNone(soup.find("h1", {"class": "DUwDvf lfPIob"}))
    json["googleMapRating"] = testNone(soup.find("div", {"class": "F7nice"}))
    json["price"] = testNone(soup.find("span", {"aria-label": "Prix: Abordable"}))
    json["address"] = testNone(soup.find("div", {"class": "AeaXub"}))
    json["info"] = str(soup.find_all("div", {"class": "Io6YTe fontBodyMedium kR99db"}))

    heures = soup.find("div", {"class": ["t39EBf", "GUrTXd"]})
    if heures is not None:
        json["heures"] = heures["aria-label"].split(".")[0].split(";")
    else:
        json["heures"] = None

    json["services"] = testNone(soup.find("div", {"class": "E0DTEd"}))
    json["restaurantTypes"] = testNone(soup.find("button", {"class": "DkEaL"}))
    return json


def getDataAbout(html: str):
    data = dict()
    soup = BeautifulSoup(html, "html.parser")

    for e in soup.find_all("div", {"class": "iP2t7d fontBodyMedium"}):
        elems = []
        for li in e.find_all("li", {"class": "hpLkke"}):
            elems.append(
                [li.find("span").text, li.find("img", {"class": "grnAab"})["src"]]
            )
        data[e.find("h2").text] = elems
    return {"restaurantService": data}


def saveHTML(html: str) -> None:
    with open("htmlSample2.html", "w", encoding="utf-8") as file:
        file.write(html)


def split_list(input_list, size: int = 10) -> list:
    return [input_list[i : i + size] for i in range(len(input_list), size)]


def waitChange(elem, page, timeS=0.1, occurence=0, maxOccurence=6):
    soupE = BeautifulSoup(elem.inner_html(), "html.parser")
    elemtitle = soupE.find("div", {"class": "NrDZNb"}).text

    soupElemScrap = BeautifulSoup(
        page.locator("div.bJzME.Hu9e2e.tTVLSc").inner_html(), "html.parser"
    )
    elemScrapTitle = soupElemScrap.find("h1", {"class": "DUwDvf lfPIob"})

    elemScrapTitle = "" if elemScrapTitle is None else elemScrapTitle.text

    elemtitle = elemtitle.upper().replace(" ", "")
    elemScrapTitle = elemScrapTitle.upper().replace(" ", "")

    if elemtitle == elemScrapTitle:
        return True
    elif occurence >= maxOccurence:
        logger.warning("Max occurence")
        return False
    else:
        time.sleep(timeS)
        if occurence > 1:
            elem.click()

        return waitChange(
            elem=elem, page=page, timeS=timeS * 2, occurence=occurence + 1
        )


if __name__ == "__main__":
    rechercheContent = "restauration 59000"
    test = "-t" in sys.argv
    with sync_playwright() as p:
        logger.info("start")

        browser = p.chromium.launch(headless=not test)

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
        if not test:
            Scrolling(page=page)
            logger.info("Scroll Terminé")

        result = []
        elems = page.locator("a.hfpxzc").all()
        elems = page.locator("div.bfdHYd.Ppzolf.OFBs3e").all()
        # bfdHYd.Ppzolf.OFBs3e
        elems = page.locator("div.Nv2PK.THOPZb.CpccDe").all()

        logger.info(f"{len(elems)} éléments trouvés")

        elems = elems[:5] if test else elems
        for e in elems:
            e.click()
            if waitChange(e, page):
                elemhtml = page.locator("div.bJzME.Hu9e2e.tTVLSc").inner_html()
                json1 = getData(elemhtml, e)
                time.sleep(1)
                page.get_by_role("tab", name=re.compile("Informations")).click()
                time.sleep(2)

                elemhtml = page.get_by_role(
                    "region", name=re.compile(".*Informations sur.*")
                ).inner_html()
                json2 = getDataAbout(elemhtml)

                items = list(json1.items())
                items.extend(json2.items())
                json = {key: value for key, value in items}

                result.append(json)
                time.sleep(0.5)
            else:
                logger.error("Fatal error: elem and scrap data not equal")
                break

        time.sleep(1)
        browser.close()
        logger.info("données collecté")

        data = pd.DataFrame(result)
        data.reset_index(inplace=True)
        logger.debug(data.shape)
        data.to_json("data.json", orient="records", indent=True, index=False)
        logger.info("données enregistré")
        logger.info("end")
