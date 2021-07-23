from bs4 import BeautifulSoup
import requests
import math
import sys
import time
from datetime import datetime


def getNumberOfPages(searchWord, anyPage):
    url = f"https://disboard.org/search?keyword={searchWord}&sort=-member_count&page={anyPage}"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'lxml')
    f = soup.find("div", "listing-summary")
    allNumbers = f.text.split(' ')
    return math.ceil(int(allNumbers[5]) / int(allNumbers[3]))


def detailedSearch(keyword, numberOfPages, tagArray, flag, rule="OR"):
    found = False
    for numberOfPage in range(1, int(numberOfPages) + 1):
        print("=========================================================================")
        print(f"Searching for servers on page {numberOfPage}... (Press CTRL+C to interrupt)")
        try:
            if found is not True:
                found = searchForServerAtPage(keyword, numberOfPage, tagArray, flag, rule)
            time.sleep(2)
        except KeyboardInterrupt:
            print('\n\n==================================================')
            print('Interrupted.')
            return

    if found is False:
        print(f"Servers with '{keyword}' as search result and '{tagArray}' or '{flag}' as tag array couldn't be found!")


def saveToFile(keyword, finalText):
    with open(f"{currentTime} {keyword}.txt", "a+", encoding="utf-8") as file:
        file.write(finalText)


def printResult(serverDetail, keyword=None):
    finalText = "\n==================================================\n"
    finalText += f"{serverDetail.find('div', 'server-name').text} ({serverDetail.find('span', 'server-online').text} " \
                 f"online)\n"
    finalText += f"Description: {serverDetail.find('div', 'server-description').text}\n"
    finalText += f"Found on: https://disboard.org{serverDetail.find('a', 'button-join').get('href')}\n"
    print(finalText)
    if keyword is not None:
        saveToFile(keyword, finalText)


def searchForServerAtPage(keyword, numPage, tagArray, flags, rule="OR"):
    found = False
    url = f"https://disboard.org/search?keyword={keyword}&sort=-member_count&page={numPage}"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'lxml')
    serverDetails = soup.findAll("div", "listing-card")

    for serverDetail in serverDetails:
        correctFlag = None
        if flags[0] != "":
            for flag in flags:
                correctFlag = serverDetail.find("span", f"flag-icon-{flag}")
                if correctFlag is not None:
                    break
            if rule.lower() == "or" and correctFlag is not None:
                printResult(serverDetail, keyword)
                found = True
                continue

        correctTag = None
        if tagArray[0] != "":
            for anyTag in tagArray:
                texts = serverDetail.findAll("span", "name")
                for text in texts:
                    readyTag = text.text.rstrip().replace('\n', '')
                    if readyTag == anyTag:
                        correctTag = readyTag
                        break

        if correctFlag is not None and correctTag is not None:
            printResult(serverDetail, keyword)
            found = True
    return found


def withoutInputSetup(keywordInput, howManyInput, tagArrayInput, flagsInput, rule="OR", numPages=None):
    keywordInput = keywordInput.replace(" ", "+")
    if numPages is None:
        numPages = getNumberOfPages(keywordInput, 1)

    if howManyInput != "":
        if numPages > int(howManyInput) > 0:
            numPages = howManyInput

    tagArrayInput = tagArrayInput.split(", ")
    flagsInput = flagsInput.split(", ")

    if tagArrayInput[0] == "" and flagsInput[0] == "":
        print("ERROR: You didn't specify any tags and flags")
        return

    detailedSearch(keywordInput, numPages, tagArrayInput, flagsInput, rule)


def mainLoop():
    global currentTime
    currentTime = datetime.today().strftime('(%Y-%m-%d) (%H-%M-%S)')
    print("=========================")
    print("Enter your search query:")
    keyword = input()

    if keyword == "":
        print("ERROR: No input entered")
        return

    numberOfPages = getNumberOfPages(keyword, 1)
    print(f"Found {numberOfPages} pages. How many pages do you want to scrap? (Enter exact number or leave it empty "
          f"to search every page).")
    howMany = input()

    print("Enter tag or tags each splitted with ',' or you can leave it empty (in that case, it will search only the "
          "flags):")
    tagArray = input()

    print("Enter a language flag or flags spllited with ',' shortcut (pl, en, etc.) or leave it empty (if you leave "
          "it empty it will search only "
          "the tags):")
    flags = input()

    print("Enter 'or' to search for servers with flags OR tags or enter 'and' to search for servers with flags AND "
          "tags (if you leave it empty it will search with 'or'):"
          )
    rule = input()
    if rule == "":
        withoutInputSetup(keyword, howMany, tagArray, flags, numPages=numberOfPages)
    else:
        withoutInputSetup(keyword, howMany, tagArray, flags, rule=rule, numPages=numberOfPages)

print("========================================")
print("Simple Disboard Scraposearcher v. 1.0.0\n")

print("Created by TheMatiaz0\nThanks to:\n- Disboard: https://disboard.org\n- BeautifulSoup (Leonard Richardson): https://pypi.org/project/beautifulsoup4\n- "
      "Requests (Kenneth Reitz): https://pypi.org/project/requests")
# Args: 1 - keyword, 2 - numberOfPages, 3 - tags, 4 - flags, 5 - rule
if len(sys.argv) == 6:
    args = sys.argv
    withoutInputSetup(args[1], args[2], args[3], args[4], args[5])

elif len(sys.argv) == 5:
    args = sys.argv
    withoutInputSetup(args[1], args[2], args[3], args[4])
while True:
    try:
        mainLoop()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
