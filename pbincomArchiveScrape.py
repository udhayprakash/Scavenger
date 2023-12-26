import time
import datetime
import os
import requests
from bs4 import BeautifulSoup, SoupStrainer
import classes.utility
from colorama import Fore, Style
import secrets

iterator = 1
tools = classes.utility.ScavUtility()
session = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0"}
searchTerms = tools.loadSearchTerms()


def getjuicystuff(tmpresponse):
    existscounter = 0
    for link in BeautifulSoup(tmpresponse, 'html.parser', parse_only=SoupStrainer('a')):
        if "HTML" not in link:
            if link.has_attr('href'):
                if len(link["href"]) == 9 and link["href"][0] == "/" and link["href"] != "/messages" and link["href"] \
                        != "/settings" and link["href"] != "/scraping":
                    if os.path.exists("data/raw_pastes" + link["href"]):
                        existscounter += 1
                        continue
                    print(
                        Fore.YELLOW + str(datetime.datetime.now()) + ": [*] Crawling " + link["href"] + Style.RESET_ALL)
                    binresponse = session.get("https://pastebin.com/raw" + link["href"], headers=headers, timeout=5)
                    binresponse = binresponse.text
                    try:
                        foundpassword = 0
                        foundsensitivedata = 0
                        sensitivevalue = ""

                        file_ = open("data/raw_pastes" + link["href"], "wb")
                        file_.write(binresponse.encode('utf-8').strip())
                        file_.close()

                        f = open("data/raw_pastes" + link["href"], "r")
                        ficontent = f.readlines()
                        f.close()

                        for line in ficontent:
                            line = line.strip()
                            if "@" in line and ":" in line:
                                line = line.split(":")
                                if len(line) == 2:
                                    line[0] = line[0].strip()
                                    line[1] = line[1].strip()
                                    if "@" in line[0]:
                                        if tools.check(line[0]) == 1:
                                            password = line[1].split(" ")[0]
                                            password = password.split("|")[0]
                                            if password == "" or len(password) < 4 or len(password) > 40:
                                                continue
                                            else:
                                                foundpassword = 1
                                        else:
                                            continue
                                    else:
                                        continue
                                else:
                                    continue

                            for searchItem in searchTerms:
                                if searchItem in line:
                                    foundsensitivedata = 1
                                    sensitivevalue = searchItem

                        if foundpassword == 1:
                            print(Fore.GREEN + str(
                                datetime.datetime.now()) + ": [+] Found credentials. Saving to "
                                                           "data/files_with_passwords/" + Style.RESET_ALL)
                            os.system("cp data/raw_pastes" + link["href"] + " data/files_with_passwords/.")
                        elif foundsensitivedata == 1:
                            print(Fore.GREEN + str(
                                datetime.datetime.now()) + ": [+] Found other sensitive data (" + sensitivevalue +
                                  "). Saving to data/otherSensitivePastes/" + Style.RESET_ALL)
                            os.system("cp data/raw_pastes" + link[
                                "href"] + " data/otherSensitivePastes/" + sensitivevalue + "_" + link["href"].replace(
                                "/", ""))

                        time.sleep(secrets.SystemRandom().randint(5, 10))
                    except Exception as eErr:
                        print(str(datetime.datetime.now()) + ": [-] " + Fore.RED + str(eErr) + Style.RESET_ALL)
                        continue
    print(Fore.RED + str(datetime.datetime.now()) + ": [-] Skipped " + str(
        existscounter) + " pastes (reason: already crawled)" + Style.RESET_ALL)


print(str(datetime.datetime.now()) + ": [#] Using slow website scraping to gather pastes")
print()
while 1:
    print(str(datetime.datetime.now()) + ": [#] Archiving pastes...")
    tools.archivepastes("data/raw_pastes")
    print(str(datetime.datetime.now()) + ": [#] " + str(iterator) + ". iterator:")
    iterator += 1
    try:
        response = session.get("https://pastebin.com/archive", headers=headers, timeout=5)
        response = response.text
        time.sleep(5)
        getjuicystuff(response)
        print(str(datetime.datetime.now()) + ": [#] Waiting 300 seconds...")
        print()
        time.sleep(300)
    except Exception as e:
        print(Fore.RED + str(datetime.datetime.now()) + ": CRITICAL ERROR" + Style.RESET_ALL)
        print(Fore.RED + str(datetime.datetime.now()) + ": [-] " + str(e) + Style.RESET_ALL)
        time.sleep(300)
        continue
