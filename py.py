from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
#Import Playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.google.fr/maps")
    # Cookies
    btn = page.get_by_role("button", name="Tout accepter")
    btn.wait_for()
    btn.click()

    # Search
    searchBar = page.locator("input#searchboxinput")
    searchBar.wait_for()
    searchBar.fill("restaurants 62100")
    loupe = page.locator("button#searchbox-searchbutton")
    loupe.click()

    # scrollZone = page.get_by_role("feed")
    # scrollZone.wait_for()
    # scrollZone.scroll_into_view_if_needed()
    page.mouse.move(100,500)
    for i in range(20): #make the range as long as needed

        page.locator("div.qjESne.veYFef")
        page.mouse.wheel(0, 10000000)
        time.sleep(1)
    time.sleep(5)

    
    htlmElems = page.inner_html("div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd")


    soup = BeautifulSoup(htlmElems,"html.parser")
    elemsNames = soup.find_all("div",{"class":["qBF1Pd","fontHeadlineSmall"]})
    print(len(elemsNames))
    print([e.text for e in elemsNames])

    # print(page.content())
    browser.close()