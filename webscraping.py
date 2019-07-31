from bs4 import BeautifulSoup
import urllib.request, requests, re, datetime, time

# MADE BY SHASHWAT KATHURIA
# 3RD YEAR UNDERGRADUATE
# FOR VERITECH INTERNSHIP ASSIGNMENT
# WEB SCAPER FOR BOMBAY HIGH COURT WEBSITE COURT CASES

baseUrl = "https://bombayhighcourt.nic.in/"

targetUrl = "https://bombayhighcourt.nic.in/casequery_action.php"

offInfoUrl = "offinfo.php"                     # URL 1
connMatterUrl = "conmatter.php"                # URL 2
appCasesUrl = "appcases.php"                   # URL 3
miscInfoUrl = "csubjectinfo.php"               # URL 4
caseObjectionUrl = "caseobjinfo.php"           # URL 5
casePaperIndexUrl = "cindexinfo.php"           # URL 6
lowerCourtUrl = "lowercourtdetails.php"        # URL 7
listingDatesAndOrdersUrl = "adjournlist1.php"  # URL 8

benchDict = {
    "Bombay" : "01",
    "Aurangabad" : "02",
    "Nagpur" : "03"
}
sideDict = {
    "Civil" : "C",
    "Criminal" : "CR",
    "Original" : "OS"
}
stampRegnDict = {
    "Register" : "R",
    "Stamp" : "S"
}

DatePattern = re.compile("^[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]$")
InputPattern = re.compile("^[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]$")

# SAMPLE INPUT
# bench = "Bombay"
# side = "Civil"
# stampregn = "Register"
# startDate = "01-01-2018"
# endDate = "01-02-2018"

def main():
        # Extracting global variables
        global startDate, endDate, bench, side, stampregn

        # Taking inputs and correspondingly checking them if they are correct or not
        startDate = input("Enter Start Date in (DD-MM-YYYY) Format : ").strip(" ")
        if not InputPattern.match(startDate):
            print("Incorrect input.")
            return
        if not dateInputChecker(startDate):
            print("Incorrect date")
            return

        print(" ")

        endDate = input("Enter End Date in (DD-MM-YYYY) Format : ").strip(" ")
        if not InputPattern.match(endDate):
            print("Incorrect input.")
            return
        if not dateInputChecker(startDate):
            print("Incorrect date")
            return

        print(" ")

        [print(key, end = "  ") for key in benchDict]
        print(" ")
        bench = input("\nEnter a bench city from the above list in exact wording : ").strip(" ").lower().capitalize()
        if not bench in benchDict:
            print("Incorrect input.")
            return

        print(" ")

        [print(key, end = " ") for key in sideDict]
        print(" ")
        side = input("\nEnter a side from the above list in exact wording : ").strip(" ").lower().capitalize()
        if not side in sideDict:
            print("Incorrect input.")
            return

        print(" ")

        [print(key, end = " ") for key in stampRegnDict]
        print(" ")
        stampregn = input("\nEnter a stamp/regn from the above list in exact wording : ").strip(" ").lower().capitalize()
        if not stampregn in stampRegnDict:
            print("Incorrect input.")
            return

        print(" ")

        sideCopy = side
        side = sideDict[side]

        # Adjusting city specific values which are different for each city
        if bench == "Bombay":
            if sideCopy == "Criminal":
                type = "APPSC"
            elif sideCopy == "Original":
                type = "ADMS"
            elif sideCopy == "Civil":
                type = "AO"
        elif bench == "Aurangabad":
            side = "A" + side
            if sideCopy == "Criminal":
                side = "AR"
                type = "ABA"
            elif sideCopy == "Original":
                print("No original records are there in Aurangabad.")
                return
            elif sideCopy == "Civil":
                type = "AO"
        elif bench == "Nagpur":
            side = "N" + side
            if sideCopy == "Criminal":
                type = "ABA"
                side = "NR"
            elif sideCopy == "Original":
                print("No original records are there in Aurangabad.")
                return
            elif sideCopy == "Civil":
                type = "AO"

        # Post data to send to targetUrl
        mainSearchQueryData = {
                "m_hc": benchDict[bench],
                "m_sideflg": side,
                "m_sr": stampRegnDict[stampregn],
                "m_skey": type,
                "m_no": "" ,
                "m_yr": "" ,
                "frmdate": startDate,
                "todate": endDate,
                "submit11": "List By Case Type"
            }

        # Getting scraper from post request result
        casesScraper = postRequestAndGetScraper(targetUrl, mainSearchQueryData)

        # Printing progress
        print("=====================")
        print("SCRAPING")
        print("=====================")

        # Scraping for each case in search results
        casesRowData = casesScraper.find_all('tr')

        # Returning if no records are found
        if len(casesRowData) <= 8:
            print("No records found.")
            return

        print("=========================================================================================================")
        # Scraping for each case
        for caseRow in range(8, len(casesRowData), 2):

            try:
                # Scraping case headings visible in the search results
                caseNumber = casesRowData[caseRow].a.string
                partyHTMLList = casesRowData[caseRow].contents[3].contents
                party = partyHTMLList[0][4:] + " " + partyHTMLList[2] + " " + partyHTMLList[4][:-2]
                caseUrl = baseUrl + casesRowData[caseRow].a['href']

                # Getting case specific scraper
                caseSpecificScraper, receivedUrl = getRequestAndGetScaper(caseUrl)

                # Checking if token had expired
                isExpired = isTokenExpired(receivedUrl, caseUrl)

                # Requesting again if token expires
                while isExpired == True:
                    print("TOKEN HAD EXPIRED : REGENERATING TOKEN")
                    casesScraper = postRequestAndGetScraper(targetUrl, mainSearchQueryData)
                    casesRowData = casesScraper.find_all('tr')
                    caseUrl = baseUrl + casesRowData[caseRow].a['href']

                    caseSpecificScraper, receivedUrl = getRequestAndGetScaper(caseUrl)

                    isExpired = isTokenExpired(receivedUrl, caseUrl)


                # Printing the case headings visible in the search results
                print(caseUrl)
                print("CASE                         : " + str(caseNumber))
                print("PARTY                        : " + str(party), end = "\n")

                # Scraping main page of case
                scrapeCaseMainPage(caseSpecificScraper)
                # Extracting hidden inputs for additional sub headings scraping
                data = getHiddenInputsPostData(caseSpecificScraper)
                # Scraping offInfoUrl = "offinfo.php"                     # URL 1
                scrapeUrl1(data)
                # Scraping connMatterUrl = "conmatter.php"                # URL 2
                scrapeUrl2(data)
                # Scraping appCasesUrl = "appcases.php"                   # URL 3
                scrapeUrl3(data)
                # Scraping miscInfoUrl = "csubjectinfo.php"               # URL 4
                scrapeUrl4(data)
                # Scraping caseObjectionUrl = "caseobjinfo.php"           # URL 5
                scrapeUrl5(data)
                # Scraping casePaperIndexUrl = "cindexinfo.php"           # URL 6
                scrapeUrl6(data)
                # Scraping lowerCourtUrl = "lowercourtdetails.php"        # URL 7
                scrapeUrl7(data)
                # Scraping listingDatesAndOrdersUrl = "adjournlist1.php"  # URL 8
                scrapeUrl8(data)
            except:
                print("ABNORMAL FORMAT.COULD NOT SCRAPE THIS RECORD.")

            print("=========================================================================================================")

def isTokenExpired(receivedUrl, caseUrl):
    """Function to check if the token had expired."""

    return receivedUrl != caseUrl

def postRequestAndGetScraper(targetUrl, data):
        """Function to send a post request to targetUrl with data and return a BeautifulSoup scraper of the result of the same."""

        response = requests.post(url = targetUrl, data = data)
        Scraper = BeautifulSoup(str(response.content.decode()), "html.parser")
        response.close()

        # Returning scraper
        return Scraper

def getRequestAndGetScaper(targetUrl):
        """Function to send a get request to targetUrl and return a BeautifulSoup scraper of the result of the same."""

        response = requests.get(targetUrl)
        Scraper = BeautifulSoup(str(response.content.decode()), "html.parser")

        # Returning scraper
        return Scraper, response.url

def scrapeCaseMainPage(caseSpecificScraper):
        """Function to scrape case main page."""

        # Scraping td elements
        caseSpecificRowData = caseSpecificScraper.find_all('td')[4:]

        # Scraping bench and PresentationDate
        Bench = caseSpecificScraper.find('td', {'width' : "90%", "align" : "center"}).find('b').text[9:]

        try:
            PresentationDate = caseSpecificScraper.find('td', {'colspan' : '4', 'align' : 'left'}).text
        except:
            PresentationDate = ""

        try:
            arr = caseSpecificScraper.find_all('td', {'width' : "15%"})
            newArr = []
            for i in arr:
                if i.text != '':
                    newArr.append(i.text)

            newArr[0] = newArr[0][2:]
            [StampNumber, RegistrationNumber] = newArr
        except:
            [StampNumber] = newArr
            RegistrationNumber = ""

        try:
            arr = caseSpecificScraper.find_all('td', {'width' : "10%"})
            newArr = []
            for i in arr:
                if DatePattern.match(i.text):
                    newArr.append(i.text)
            [FilingDate, RegistrationDate] = newArr
        except:
            [FilingDate] = newArr
            RegistrationDate = ""

        # Scraping statuss
        Status = caseSpecificScraper.find_all("font")[0].text.strip(" ")

        # Scraping NextDate, LastDate, RejectedDate, DisposedDate
        arr = caseSpecificScraper.find_all('td', {'width' : "35%"})
        newArr = []
        for i in arr:
            if DatePattern.match(i.text):
                newArr.append(i.text)

        if Status == "Pre-Admission":
            try:
                [NextDate, LastDate] = newArr
                RejectedDate = ""
                DisposedDate = ""
            except:
                [LastDate] = newArr
                NextDate = ""
                RejectedDate = ""
                DisposedDate = ""
        elif Status == "Rejected":
            if len(newArr) == 1:
                [RejectedDate] = newArr
                NextDate = ""
                LastDate = ""
            elif len(newArr) == 2:
                [RejectedDate, LastDate] = newArr
                NextDate = ""
            elif len(newArr) == 3:
                [RejectedDate, NextDate, LastDate] = newArr
            DisposedDate = ""
        elif Status == "Disposed":
            if len(newArr) == 2:
                [DisposedDate, LastDate] = newArr
                NextDate = ""
            elif len(newArr) == 3:
                [DisposedDate, NextDate, LastDate] = newArr
            RejectedDate = ""

        # Scraping status and acts
        tdTexts = [i.text.strip(" ").strip("\n") for i in caseSpecificScraper.find_all('td', {'width' : '35%'})]
        extractedActs = []
        Stages = []

        for i in range(len(tdTexts)):

            if DatePattern.match(tdTexts[i]):
                Stages.append(tdTexts[i+1])
                extractedActs = tdTexts[i+2 : ][:]

        Acts = extractedActs[:]

        # Scraping Petitioner, Respondent and PetitionAdv
        Petitioner = [i.text for i in caseSpecificScraper.find_all('select', {'name' : 'm_petno'})[0].contents[1:]]
        Respondent = [i.text for i in caseSpecificScraper.find_all('select', {'name' : 'm_resno'})[0].contents[1:]]
        PetitionAdv = [i.text for i in caseSpecificScraper.find_all('select', {'name' : 'm_padv'})[0].contents[1:]]

        # Scraping District and BenchType
        District = caseSpecificScraper.find_all('td', {'width' : "80%"})[0].text
        BenchType = caseSpecificScraper.find_all('table', {'width':'100%', 'align':'center', 'border':'0'})[3].find('td', {'width' : "35%"}).text

        # Scraping Corams
        corams = [i.text for i in caseSpecificScraper.find_all('td', {'width' : '80%'})[1:]]
        if Status == "Pre-Admission":
            try:
                [Coram, LastCoram] = corams
            except:
                [LastCoram] = corams
            DisposedBy = ""
        elif Status == "Rejected":
            Coram = ""
            LastCoram = ""
            DisposedBy = ""
        elif Status == "Disposed":
            if len(corams) == 2:
                [DisposedBy, LastCoram] = corams
            elif len(corams) !=2:
                corams = list(set(corams))
                DisposedBy = corams[:]
                LastCoram = corams[:]
            Coram = ""

        # Printing scraped results
        print("Bench                        :  " + Bench)
        print("PresentationDate             :  " + PresentationDate)
        print("StampNumber                  :  " + StampNumber)
        print("FilingDate                   :  " + FilingDate)
        print("RegistrationNumber           :  " + RegistrationNumber)
        print("RegistrationDate             :  " + RegistrationDate)
        print("Petitioner                   :  " + str(Petitioner))
        print("Respondent                   :  " + str(Respondent))
        print("PetitionAdv                  :  " + str(PetitionAdv))

        print("District                     :  " + District)
        print("BenchType                    :  " + BenchType)
        print("Status                       :  " + Status)
        if Status == "Pre-Admission":
            if NextDate != "":
                print("LastDate                     :  " + LastDate)
                print("NextDate                     :  " + NextDate)
                print("Coram                        :  " + Coram)
                print("LastCoram                    :  " + LastCoram)
            else:
                print("LastDate                     :  " + LastDate)
                print("LastCoram                    :  " + LastCoram)
        elif Status == "Rejected":
            print("RejectedDate                 :  " + RejectedDate)
        elif Status == "Disposed":
            print("Disposed Date                :  " + DisposedDate)
            if "NextDate" != "":
                print("NextDate                     :  " + NextDate)
            print("LastDate                     :  " + LastDate)
            print("LastCoram                    :  " + str(LastCoram))
            print("DisposedBy                   :  " + str(DisposedBy))

        print("Stages(For Respective Dates) :  " + str(Stages))
        print("Acts                         :  " + str(Acts))

def scrapeUrl1(data):
        """Function to scrape Url1 => offInfoUrl = "offinfo.php". Input is post data to be sent."""

        print("\n----------\nOFF INFO\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + offInfoUrl, data)

        # Scraping required elements
        dateArr = [i.text.strip(" ").strip("\n") for i in subHeadingScraper.find_all('td', {'width' : '10%'})][:-1]
        tdTexts2 = [i.text.strip(" ").strip("\n") for i in subHeadingScraper.find_all('td', {'width' : '40%'})][:-2]
        descriptionArr = []
        remarkArr = []
        for i in range(len(tdTexts2)):
            if i % 2 == 0:
                descriptionArr.append(tdTexts2[i])
            else:
                remarkArr.append(tdTexts2[i])

        offInfoArr = list(zip(descriptionArr, dateArr, remarkArr))[1:]

        # Printing scraped results
        if offInfoArr == []:
            print("No off info.")
        else:
            for info in offInfoArr:
                print("Description : " + info[0])
                print("Date : " + info[1])
                print("Remark : " + info[2])

def scrapeUrl2(data):
        """Function to scrape Url2 => connMatterUrl = "conmatter.php". Input is post data to be sent."""

        print("\n----------\nCONNECTED MATTERS\n----------")
        # Getting Scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + connMatterUrl, data)

        # Scraping required elements
        arr = [i.text.strip("\r").strip("\n").strip(" ") for i in subHeadingScraper.find_all('td', {'width' : '45%'})]
        arr1 = []
        for i in arr:
            if i != "":
                arr1.append(i)
        arr1 = arr1[2:][:]
        stampNoArr = []
        regNoArr = []
        for i in range(len(arr1)):
            if i % 2 == 0:
                stampNoArr.append(arr1[i])
            else:
                regNoArr.append(arr1[i])

        finalArr = list(zip(stampNoArr, regNoArr))

        # Printing scraped results
        if finalArr == []:
            print("No connected matters.")

        else:
            for element in finalArr:
                print("Stamp No  : " + str(element[0]))
                print("Reg No    : " + str(element[1]))

def scrapeUrl3(data):
        """Function to scrape Url3 => appCasesUrl = "appcases.php". Input is post data to be sent."""

        print("\n----------\nAPP CASES\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + appCasesUrl, data)

        # Scraping required elements
        stampAndRegNoArr = [i.text.strip("\r").strip("\n").strip(" ") for i in subHeadingScraper.find_all('td', {'width' : '25%'})][2:]
        categoryArr = [i.text.strip("\r").strip("\n").strip(" ") for i in subHeadingScraper.find_all('td', {'width' : '30%'})][1:]
        statusArr = [i.text.strip("\r").strip("\n").strip(" ") for i in subHeadingScraper.find_all('td', {'width' : '10%'})][1:]
        stampNoArr = []
        regNoArr = []
        for i in range(len(stampAndRegNoArr)):
            if i % 2 == 0:
                stampNoArr.append(stampAndRegNoArr[i])
            else:
                regNoArr.append(stampAndRegNoArr[i])

        appCasesArr = zip(stampNoArr, regNoArr, categoryArr, statusArr)

        # Printing scraped results
        if appCasesArr == []:
            print("No app cases.")
        else:
            for element in appCasesArr:
                print("\n")
                print("Stamp No : " + element[0])
                print("Reg No   : " + element[1])
                print("Category : " + element[2])
                print("Status   : " + element[3])

def scrapeUrl4(data):
        """Function to scrape Url4 => miscInfoUrl = "csubjectinfo.php". Input is post data to be sent."""

        print("\n----------\nMISC INFO\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + miscInfoUrl, data)

        # Scraping required elements
        subCatArr = [i.text for i in subHeadingScraper.find_all('td', {'width' : '10%'})]
        tableDetailsArr = [i.text for i in subHeadingScraper.find_all('td')]
        VPEntries = []
        AffidavitEntries = []
        if 'VP Entires Not Found' in tableDetailsArr:
            VPEntries = []
            if 'Affidavit Entires Not Found' in tableDetailsArr:
                AffidavitEntries = []
            else:
                for i in range(len(tableDetailsArr)):
                    if DatePattern.match(tableDetailsArr[i]):
                        AffidavitEntries.append(tableDetailsArr[i - 3 : i + 1][:])
        else:
            if 'Affidavit Entires Not Found' in tableDetailsArr:
                AffidavitEntries = []
                for i in range(len(tableDetailsArr)):
                    if DatePattern.match(tableDetailsArr[i]):
                        VPEntries.append(tableDetailsArr[i - 3 : i + 1][:])
            else:

                for i in range(len(tableDetailsArr)):
                    if DatePattern.match(tableDetailsArr[i]):
                        if tableDetailsArr.index('Affidavit Details')  > i:
                            VPEntries.append(tableDetailsArr[i - 3 : i + 1][:])
                        else:
                            AffidavitEntries.append(tableDetailsArr[i - 3 : i + 1][:])

        # Printing scraped results
        try:
            print("Subject Category  : " + str(subCatArr[1].strip("Sub. Cat.:-")))
        except:
            print("No Subject Category.")

        if VPEntries == []:
            print("No VP Entries.")
        else:
            print("\nVP DETAILS\n")
            for entry in VPEntries:
                print("VP No     : " + str(entry[0]))
                print("Filed For : " + str(entry[1]))
                print("Filed By  : " + str(entry[2]))
                print("Date      : " + str(entry[3]))
                print("\n")

        if AffidavitEntries == []:
            print("No Affidavit Entries.")
        else:
            print("\nAFFIDAVIT DETAILS\n")
            for entry in AffidavitEntries:
                print("Aff No    : " + str(entry[0]))
                print("Filed For : " + str(entry[1]))
                print("Filed By  : " + str(entry[2]))
                print("Date      : " + str(entry[3]))
                print("\n")

def scrapeUrl5(data):
        """Function to scrape Url5 => caseObjectionUrl = "caseobjinfo.php". Input is post data to be sent."""

        print("\n----------\nOBJECTIONS\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + caseObjectionUrl, data)

        # Scraping required elements
        objectionsArray = [i.text for i in subHeadingScraper.find_all('b')][4:]

        # Printing results
        if objectionsArray == []:
            print("No Objections.")
        else:
            for i in range(0, len(objectionsArray), 3):
                print("\n")
                print("Objection   : " + objectionsArray[i])
                print("Raised On   : " + objectionsArray[i + 1])
                print("Removed On   : " + objectionsArray[i + 2])

def scrapeUrl6(data):
        """Function to scrape Url6 => casePaperIndexUrl = "cindexinfo.php". Input is post data to be sent."""

        print("\n----------\nCASE PAPERS\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + casePaperIndexUrl, data)

        # Scraping required elements
        tdArray = [i.text for i in subHeadingScraper.find_all('td')]
        casePapersIndexArray = []
        for i in range(len(tdArray)):
            if DatePattern.match(tdArray[i]):
                casePapersIndexArray.append(tdArray[i - 1 : i + 4][:])

        # Printing results
        if casePapersIndexArray == []:
            print("No case papers.")
        else:
            for paper in casePapersIndexArray:
                print("\n")
                print("Document     : " + str(paper[0]))
                print("Filing Date  : " + str(paper[1]))
                print("Start Page   : " + str(paper[2]))
                print("End Page     : " + str(paper[3]))
                print("No of Pages  : " + str(paper[4]))

def scrapeUrl7(data):
        """Function to scrape Url7 =>lowerCourtUrl = "lowercourtdetails.php". Input is post data to be sent."""

        print("\n----------\nLOWER COURT DETAILS\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + lowerCourtUrl, data)

        # Scraping required elements
        tdArray = [i.text for i in subHeadingScraper.find_all('td', {'width' : '70%'})]

        lowerCourtDetailsArray = []
        for i in range(len(tdArray)):
            if DatePattern.match(tdArray[i]):
                lowerCourtDetailsArray.append(tdArray[i - 4 : i + 2][:])

        if lowerCourtDetailsArray == []:
            print("No lower court details.")
        else:
            lowerCourt = lowerCourtDetailsArray[0]

            print("\n")
            print("Court               : " + str(lowerCourt[0]))
            print("District            : " + str(lowerCourt[1]))
            print("Case No             : " + str(lowerCourt[2]))
            print("Judge Designation   : " + str(lowerCourt[3]))
            print("Decision Date       : " + str(lowerCourt[4]))
            print("Judgement Language  : " + str(lowerCourt[5]))

def scrapeUrl8(data):
        """Function to scrape Url8 =>listingDatesAndOrdersUrl = "adjournlist1.php". Input is post data to be sent."""

        print("\n----------\nLISTING DATES/ORDERS DETAILS\n----------")
        # Getting scraper
        subHeadingScraper = postRequestAndGetScraper(baseUrl + listingDatesAndOrdersUrl, data)

        # scraping required elements
        tdArray = [i.text.strip('\r').strip('\n').strip(' ') for i in subHeadingScraper.find_all('td')]
        judgementTableArray = []
        cmisTableArray = []
        try:
            otherTableIndex = tdArray.index('1')
            for i in range(len(tdArray)):
                if DatePattern.match(tdArray[i]) and i < otherTableIndex :
                    judgementTableArray.append(tdArray[i: i + 5][:])
                elif DatePattern.match(tdArray[i].strip('*')) and i >= otherTableIndex :
                    cmisTableArray.append(tdArray[i])
        except:
            for i in range(len(tdArray)):
                if DatePattern.match(tdArray[i])  :
                    judgementTableArray.append(tdArray[i: i + 5][:])

        # Printing results
        if judgementTableArray == []:
            print("No judgements.")
        else:
            print("\nJUDGEMENT TABLE\n\n")
            for judgement in judgementTableArray:
                print("\n")
                print("Date               : " + str(judgement[0]))
                print("Coram              : " + str(judgement[1]))
                print("Action             : " + str(judgement[3]))
                print("Order/Judgement    : " + str(judgement[4]))

        if cmisTableArray == []:
            print("\nNo cmis table.")
        else:
            print("\n\nCMIS TABLE\n\n")
            print("\'*\' Denotes Actual Court Listing/Heard Dates")
            for i in range(len(cmisTableArray)):
                print(" ")
                print("Sr.No.    : " + str(i) + " CMIS Date : " + str(cmisTableArray[i]))

def getHiddenInputsPostData(caseSpecificScraper):
        """Function to extract out hidden inputs and return them as a data dict to be sent as post data to server."""

        # Extracting all the hidden data inputs
        hiddenInputs = caseSpecificScraper.find_all('input', {'type' : 'hidden'})
        data = {}
        for input in hiddenInputs:
            data[input['name']] = input['value']

        data['m_petno'] = ""
        data['m_resno'] = ""
        data["m_padv"] = ""

        # returning data dict
        return data

def dateInputChecker(date):
    """Function to check if the date is inputed correctly."""
    dateArr = date.split("-")
    dateArr[0] = int(dateArr[0])
    dateArr[1] = int(dateArr[1])
    dateArr[2] = int(dateArr[2])

    # Returning false if incorrect, true if correct
    return (dateArr[0] <= 31) and (dateArr[1] <= 12) and (dateArr[2] <= datetime.datetime.now().year)

if __name__ == "__main__":
    main()
