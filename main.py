

import json
import time
import os

from selenium import webdriver
from discordwebhook import Discord
from difflib import Differ
from datetime import datetime

import corefnclass

#define discord webhook
discord = Discord(url="https://discord.com/api/webhooks/1212292461611847690/L9WHALL5g8ArkD2L0uJ3vWz912Kk1WsbXDO0Cq25jeNgaQNfJOqc3BNIc-mhnh1i-x7I")
#Sleep between setting
SLEEPSECONDS = 10800 #3hrs

#define course settings to watch
#define course ids to keep track of in format of "Department Name":[courseids,...]
CourseIdSearchMap = {"COMPSCI":[34330,34080,34350,34220],
                     "IN4MATX":[36100]
                     }
#define the course id to name mapping for printing
CourseIDNameMap = {34330 : "cs175",
                   34080: "cs122D",
                   36100:"informatics 131",
                   34350:"cs179",
                   34220 : "CS147"}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Return string with the escape sequences at specific indexes to highlight
def highlight_string_at_idxs(string, indexes):
    # hl = "\x1b[38;5;160m"  # 8-bit
    hl = "\x1b[91m"
    reset = "\x1b[0m"
    words_with_hl = []
    for string_idx, word in enumerate(string.split(" ")):
        if string_idx in indexes:
            words_with_hl.append(hl + word + reset)
        else:
            words_with_hl.append(word)
    return " ".join(words_with_hl)

# Return indexes of the additions to s2 compared to s1
def get_indexes_of_additions(s1, s2):
    diffs = list(Differ().compare(s1.split(" "), s2.split(" ")))
    indexes = []
    adj_idx = 0  # Adjust index to compensate for removed words
    for diff_idx, diff in enumerate(diffs):
        if diff[:1] == "+":
            indexes.append(diff_idx - adj_idx)
        elif diff[:1] == "-":
            adj_idx += 1
    return indexes




def main(name):


    # discord.post(content="Hello, world.") #for sending a discord message

    #options test
    chrome_options = webdriver.ChromeOptions()

    # chrome_options.add_argument("headless") #to make this headless
    chrome_options.add_argument("disable-extensions")
    chrome_options.add_argument("disable-popup-blocking")
    chrome_options.page_load_strategy = 'eager'

    ### This blocks images and javascript requests
    chrome_prefs = {
        "profile.default_content_setting_values": {
            "images": 2,
            "javascript": 2,
        }
    }
    chrome_options.experimental_options["prefs"] = chrome_prefs

    aucisocdriver = corefnclass.WebDriver("https://www.reg.uci.edu/perl/WebSoc",chrome_options)



    # for agivendept in theallalldeptlist:

    CourStorFileName = 'Coursedetails.json'


    while(True):

        StartingTime = datetime.now()

        print(f"New iteration {StartingTime}")

        check_file = os.path.isfile(CourStorFileName)

        if check_file is False:
            with open(CourStorFileName, "w") as outfile:
                json.dump(dict(), outfile)





        #load json
        with open(CourStorFileName) as f:
            PrevStoreDict = json.load(f)
            print(PrevStoreDict)



        # test the function
        aselectboxvaluedict = {"YearTerm": "2024-14"}

        StoreDict = dict()
        DiffDetectBool = False
        DiffDiscordStr = ""

        for aDeptName,acourseIdList in CourseIdSearchMap.items():
            print(aDeptName,acourseIdList)
            aselectboxvaluedict["Dept"] = aDeptName


            asocpagetext = aucisocdriver.getSocpage(aselectboxvaluedict)

            PageTableList = asocpagetext.split('\n')
            # print(PageTableList)


            for anumind,aline in enumerate(PageTableList):


                    coursidinLineList = aline.split()

                    if len(coursidinLineList) > 0:
                        try:
                            CleanedLine = aline.strip()
                            aPotCourseNum = int(coursidinLineList[0])


                            if aPotCourseNum in acourseIdList:
                                StoreDict[aPotCourseNum] = CleanedLine
                                print(CourseIDNameMap[aPotCourseNum])
                                print(CleanedLine)

                                #check for differences
                                if str(aPotCourseNum) in PrevStoreDict and CleanedLine != PrevStoreDict[str(aPotCourseNum)]:
                                    DiffDetectBool = True

                                    print(f"{bcolors.WARNING}diff detected{bcolors.ENDC}")
                                    addition_idxs = get_indexes_of_additions(CleanedLine, PrevStoreDict[str(aPotCourseNum)])
                                    hl_sentence2 = highlight_string_at_idxs(PrevStoreDict[str(aPotCourseNum)], addition_idxs)
                                    print(hl_sentence2)

                                    DiffDiscordStr += f"Course: {CourseIDNameMap[aPotCourseNum]}\n"
                                    DiffDiscordStr += f"{CleanedLine}\n\n"




                                print()

                        except ValueError:
                            pass

        #send a discord notification
        if DiffDetectBool:
            # discord notificatoin
            discord.post(content=f"Difference detected Summary! {StartingTime} :\n"
                                 + DiffDiscordStr)

        with open(CourStorFileName, "w") as outfile:
            json.dump(StoreDict, outfile)

        time.sleep(SLEEPSECONDS)





        # print(asocpagetext.split('\n'))

        # theretdict = corefnclass.processsocpage(asocpagetext)
        #
        #
        # print("the return dict")
        # print(theretdict)


        #write to file

        # print(asocpagetext)


        # for akey in theretdict:
        #     thewritetotaldictfile.write(f"!!the course!!: {akey}\n")
        #
        #     for alist in theretdict[akey]:
        #         thewritetotaldictfile.write(f"the list:\n{alist}\n")
        #
        #     #write a space to seperate it
        #     thewritetotaldictfile.write("\n")

    #close the file at the end
    # thewritetotaldictfile.close()




    # for adept in theallalldeptlist:
    #
    #     aselectboxvaluedict = {"YearTerm":"2023-14"}
    #     aselectboxvaluedict["Dept"] = adept
    #
    #     asocpagetext = aucisocdriver.getSocpage(aselectboxvaluedict).split("\n")
    #
    #     print(asocpagetext)
    #
    #     # time.sleep(10)
    #
    #     #csv process test
    #
    #     processtext = str()
    #
    #     with open("test.txt",'r') as thetext:
    #         # print(alltextlines.readlines())
    #
    #         alltextlineslist = thetext.readlines()
    #
    #         alltextlineslist = asocpagetext
    #
    #         # print(alltextlineslist.)
    #
    #
    #
    #
    #
    #         #the starting char line after will be proc
    #
    #         endingchar = "***"
    #
    #
    #
    #         # for index in range(len(alltextlineslist)):
    #         #     print(f"processing: {alltextlineslist[index]}")
    #         #
    #         #     if(startingchar in alltextlineslist[index]):
    #         #         #store the index of the line
    #         #         print("set the starting index")
    #         #         startingprocindex = index
    #         #
    #         #     if(endingchar in alltextlineslist[index]):
    #         #         #store the index of the line
    #         #         endingprocindex = index
    #         #
    #         # print(f"the final indexs: startingindx={startingprocindex} endingindx={endingprocindex}")
    #
    #         # runing proc is only true when a certain char is found
    #         runningproclines = False
    #
    #         excludedwordslist = ["Search Criteria","Quarter"]
    #
    #
    #
    #
    #
    #         # print(f" in thest {'Hello' in 'thei is hello a test'}")
    #
    #         #the keys are all the courses string
    #
    #         thepagedict = defaultdict(list)
    #
    #         fieldlist = list()
    #
    #         #store the course string
    #         curcoutsestr = ""
    #
    #         #compile the regex
    #         thebodypat = re.compile(r"(\d+) +(\w+) +(\w+|\d) +(\S+) +([ \w\S]+, [ \w\S]+[.]|\w+) +(\w+ +\d+:\d+- *\d+:\d+\w?|[*]?TBA[*]?) +(\w+ \d*\w*|[*]?TBA[*]?|ON LINE|) +(\w+, \w+ \d+, \d+:\d+-\d+:\d+\w+|[*]?TBA[*]?)? +(\d+) +(\d+[/]?\d+|\d+) +(\d+|n/a|\S+) +(\d+) +(\d+) +(\S+)? +(\w+)")
    #
    #
    #         for i in range(len(alltextlineslist)):
    #             print(f"processing: '{alltextlineslist[i]}'")
    #
    #             #check for ending char
    #             if(endingchar in alltextlineslist[i].strip()):
    #                 break
    #             print(f"the line len: {len(alltextlineslist[i])}")
    #             if runningproclines ==  False:
    #                 #check if a char is
    #                 if((len(alltextlineslist[i]) > 0) and alltextlineslist[i][0].isalpha()):
    #                     print("the starting char has been found")
    #                     runningproclines = True
    #
    #                     #get the course string
    #                     thecoursrtlinelist = (' '.join(alltextlineslist[i].strip().split())).split(" ")
    #                     print(f"thecourse str line arrray: {thecoursrtlinelist}")
    #                     curcoutsestr = (' '.join(alltextlineslist[i].strip().split()))
    #
    #
    #
    #                     #initialie field list
    #                     fieldlist = list()
    #
    #                     #check if excluded word is not in line
    #                     for aword in excludedwordslist:
    #                         if aword in alltextlineslist[i]:
    #                             #set the runprocline to false
    #                             runningproclines = False
    #                             break
    #
    #                     # if(runningproclines == True):
    #                     #     curcoutsestr = (thecoursetitlepat.search(alltextlineslist[i].strip())).group(0)
    #                     #     curcoutsestr = ' '.join(curcoutsestr.split())
    #
    #                     print(f"final truth val: {runningproclines}")
    #
    #             else:
    #                 #processing the actual lines
    #                 # print(f"processing: {aline}")
    #                 print("in the else blk")
    #
    #                 # check newline
    #                 if (len(alltextlineslist[i]) == 0):
    #                     print("a new line has been found")
    #                     runningproclines = False
    #                     continue
    #
    #                 #check for ~ in line
    #                 if("~" in alltextlineslist[i]):
    #                     #continue to nex iteration
    #                     continue
    #
    #
    #
    #                 #process the line
    #                 #check if it is a line with the fields
    #                 print(f"field check: {alltextlineslist[i].lstrip()}")
    #                 if("CCode" in alltextlineslist[i]):
    #                     #the line is a field line with all the fields
    #                     fieldlist = (' '.join(alltextlineslist[i].strip().split())).split(" ")
    #                     print(f"the field list {fieldlist}")
    #                 else:
    #                     #the lines is a body line with info on the class
    #                     thematchobj = thebodypat.search(alltextlineslist[i].strip())
    #
    #                     if thematchobj == None:
    #                         #there was no match so continue
    #                         continue
    #                         # raise "ERROR body match was null"
    #
    #                     thematchgoupslist = thematchobj.groups()
    #
    #                     print(f"the match obj: {thematchgoupslist}")
    #
    #                     #create a dict with key as the fields and value as values
    #                     abodydict = dict()
    #
    #                     for cindlist in range(len(fieldlist)):
    #                         #insert key and value into the dict
    #                         abodydict[fieldlist[cindlist]] = thematchgoupslist[cindlist]
    #
    #                     print(f"the final dict: {abodydict}")
    #
    #
    #                     #insert the created thepagedict dict into
    #                     print(f"the course str to append in pagedict: {curcoutsestr}")
    #                     thepagedict[curcoutsestr].append(abodydict)
    #
    #
    #
    #
    #
    #
    #
    #
    #         #finally print the dict
    #         print(thepagedict)
    #         print(f"the final page dict length: {len(thepagedict)}")
    #
    #         count = 0
    #
    #         for akey in thepagedict:
    #             print(f"key {akey}")
    #             count += len(akey)
    #
    #         print(f"the count is: {count}")
    #
    #         fouttotaldict = open("out.txt", "a")
    #
    #         fouttotaldict.write(str(thepagedict))
    #
    #         fouttotaldict.close()
    #
    #         #pretty print dict



    # #get list of possible departments
    # driverdpt = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    # driverdpt.get('https://www.reg.uci.edu/perl/WebSoc')
    # thedeptfield = driverdpt.find_element(By.NAME, "Dept")
    #
    # #thedeptfiels is a select list
    # selectdeptfield = Select(thedeptfield)
    # deptoptionlist = (selectdeptfield.options)[1:]
    #
    # print(f"the attribute test: {deptoptionlist[0].get_attribute('value')}")
    #
    # thedeptnamelist = list()
    # thedeptnamelist.append('COMPSCI')
    #
    #
    # # for aselectable in deptoptionlist:
    # #     print(f"the selectable options {aselectable.text}")
    # #     thedeptnamelist.append(aselectable.text)
    #
    # #close dept driver afterwards
    # driverdpt.close()
    #
    # # selectdeptfield.select_by_visible_text(deptoptionlist[1].text)
    #
    # # time.sleep(10)
    # # thedeptlist = thedeptfield.text.strip().split(sep='\n')
    #
    # # print(f"the dept {thedeptlist[1:]}")
    #
    # # thedeptlist = list()
    # #
    # # for aline in thedeptfield.text.split('\n'):
    # #     cleanline = aline.strip()
    # #     print(f"the line: {cleanline}")
    # #     if('.' in cleanline):
    # #         print(f"there is a dot in line")
    # #         print(f"{cleanline.split(' .', 1)[0]}")
    # #
    # #         #append to deptlist
    # #         thedeptlist.append(cleanline.split(' .', 1)[0])
    # #
    # # print("the final dept list")
    # # print(thedeptlist)
    #
    # driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)
    #
    # for agivendept in thedeptnamelist:
    #     print(f"getting dept: {agivendept}")
    #
    #
    #     driver.get('https://www.reg.uci.edu/perl/WebSoc')
    #
    #     #fill in for department name
    #     deptbox = driver.find_element(By.NAME,"Dept")
    #     #get it as a select object
    #     dptselectobj = Select(deptbox)
    #     dptselectobj.select_by_value(agivendept)
    #
    #     # time.sleep(10)
    #     #
    #     submittextbut = driver.find_element(By.CLASS_NAME,"banner-width")
    #     submittextbut.click()
    #
    #
    #
    #
    #     print("-------------------")
    #     print(driver.page_source)
    #
    #     print("=-----------------")
    #
    #     # print(submittextbut)
    #
    #     fulltext = driver.page_source
    #
    #     print(f"the fulltext {fulltext}")
    #
    #     #wait for debug
    #     time.sleep(5)
    #
    #
    #
    #     #write to a file
    #     fwrite = open("acompsci-courses.txt",'a')
    #
    #     fwrite.write(fulltext)
    #     fwrite.close()

    # # close driver afterwards
    # driver.close()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('PyCharm')


