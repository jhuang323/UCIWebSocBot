# the core functions and classes

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# dependency for the chrome driver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# import exceptions from selenium
from selenium.common.exceptions import NoSuchElementException

# for the processpage funct
import re
from collections import defaultdict

# global vars
submmitbuttonclassname = "banner-width"


# my webdriver class
class WebDriver:
    # the init function
    def __init__(self, agivenurl, givenoptions = None):
        # set up the driver from selenium
        self.driver = webdriver.Firefox()
        self.baseurl = agivenurl

    def getselectvalues(self, anametofind) -> list:
        # get the select list values
        # go to the baseurl
        self.driver.get(self.baseurl)

        # get elem
        theelemfound = self.driver.find_element(By.NAME, anametofind)

        # cast elem as Select
        elemselectlist = Select(theelemfound).options

        # for each webelem get the values
        for i in range(len(elemselectlist)):
            # replace the webelem with its values
            elemselectlist[i] = elemselectlist[i].get_attribute('value')

        # return the Select options
        return elemselectlist

    def getSocpage(self, aselectnamevaluedict: dict):
        # given a diction with key being the name of the Select option and values being the values to select

        # go to the baseurl
        self.driver.get(self.baseurl)

        # inter through dict and select eeach value for its respective Select option
        for aSelectoptionvaluetuple in aselectnamevaluedict.items():

            try:
                # get the element
                theSelectboxfound = Select(self.driver.find_element(By.NAME, aSelectoptionvaluetuple[0]))
                # select the value store in the 2nd elem in tup
                theSelectboxfound.select_by_value(aSelectoptionvaluetuple[1])
            except NoSuchElementException:

                raise NoSuchElementException(
                    f"Either a Select box with name or a value could not be found: {aSelectoptionvaluetuple}")

        # click the submit button
        thesubbuttonelem = self.driver.find_element(By.CLASS_NAME, submmitbuttonclassname)
        thesubbuttonelem.click()

        # return the text from page source
        return self.driver.page_source


# functions

# processing a text page that is returned
def processsocpage(atext: str) -> defaultdict:
    alltextlineslist = atext.split("\n")

    # the starting char line after will be proc

    endingchar = "***"

    # runing proc is only true when a certain char is found
    runningproclines = False

    excludedwordslist = ["Search Criteria", "Quarter"]

    # in the body check
    # the field keyword to search for
    fieldkeywordsearchfor = "CCode"
    # the symbol to skip if seen
    symboltoskipinbody = "~"

    # the keys are all the courses string

    thepagedict = defaultdict(list)

    fieldlist = list()

    # store the course string
    curcoutsestr = ""

    # compile the regex
    thebodypat = re.compile(
        r"(\d+) +(\w+) +(\w+|\d) +(\S+) +([ \w\S]+, [ \w\S]+[.]|\w+) +(\w+ +\d+:\d+- *\d+:\d+\w?|[*]?TBA[*]?) +(\w+ \d*\w*|[*]?TBA[*]?|ON LINE|) +(\w+, \w+ \d+, \d+:\d+-\d+:\d+\w+|[*]?TBA[*]?)? +(\d+) +(\d+[/]?\d+|\d+) +(\d+|n/a|\S+) +(\d+) +(\d+) +(\S+)? +(\w+)")

    for i in range(len(alltextlineslist)):
        print(f"processing: '{alltextlineslist[i]}'")

        # check for ending char
        if (endingchar in alltextlineslist[i].strip()):
            break
        print(f"the line len: {len(alltextlineslist[i])}")
        if runningproclines == False:
            # check if a char is
            if ((len(alltextlineslist[i]) > 0) and alltextlineslist[i][0].isalpha()):
                print("the starting char has been found")
                runningproclines = True

                # get the course string
                thecoursrtlinelist = (' '.join(alltextlineslist[i].strip().split())).split(" ")
                print(f"thecourse str line arrray: {thecoursrtlinelist}")
                curcoutsestr = (' '.join(alltextlineslist[i].strip().split()))

                # initialie field list
                fieldlist = list()

                # check if excluded word is not in line
                for aword in excludedwordslist:
                    if aword in alltextlineslist[i]:
                        # set the runprocline to false
                        runningproclines = False
                        break

                # if(runningproclines == True):
                #     curcoutsestr = (thecoursetitlepat.search(alltextlineslist[i].strip())).group(0)
                #     curcoutsestr = ' '.join(curcoutsestr.split())

                print(f"final truth val: {runningproclines}")

        else:
            # processing the actual lines
            # print(f"processing: {aline}")
            print("in the else blk")

            # check newline
            if (len(alltextlineslist[i]) == 0):
                print("a new line has been found")
                runningproclines = False
                continue

            # check for symbol in body in line
            if (symboltoskipinbody in alltextlineslist[i]):
                # continue to nex iteration
                continue

            # process the line
            # check if it is a line with the fields
            print(f"field check: {alltextlineslist[i].lstrip()}")
            if (fieldkeywordsearchfor in alltextlineslist[i]):
                # the line is a field line with all the fields
                fieldlist = (' '.join(alltextlineslist[i].strip().split())).split(" ")
                print(f"the field list {fieldlist}")
            else:
                # the lines is a body line with info on the class
                thematchobj = thebodypat.search(alltextlineslist[i].strip())

                if thematchobj == None:
                    # there was no match so continue
                    continue
                    # raise "ERROR body match was null"

                thematchgoupslist = thematchobj.groups()

                print(f"the match obj: {thematchgoupslist}")

                # create a dict with key as the fields and value as values
                abodydict = dict()

                for cindlist in range(len(fieldlist)):
                    # insert key and value into the dict
                    abodydict[fieldlist[cindlist]] = thematchgoupslist[cindlist]

                print(f"the final dict: {abodydict}")

                # insert the created thepagedict dict into
                print(f"the course str to append in pagedict: {curcoutsestr}")
                thepagedict[curcoutsestr].append(abodydict)

    # finally print the dict
    print(thepagedict)
    print(f"the final page dict length: {len(thepagedict)}")

    count = 0

    for akey in thepagedict:
        print(f"key {akey}")
        count += len(akey)

    print(f"the count is: {count}")

    return thepagedict

    # pretty print dict
