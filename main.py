

import json
import os

from selenium import webdriver
from discordwebhook import Discord
from difflib import Differ
from datetime import datetime

import corefnclass
import PageProcessHelper

#define BASE URL
BASEURL = "https://www.reg.uci.edu/perl/WebSoc"
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


CourStorFileName = 'Coursedetails.json'
#set to current term or target term
aselectboxvaluedict = {
    "YearTerm": "2024-14"
}

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
    hl = "\u001b[0;31m"
    reset = "\u001b[0;0m"
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




def main():



    aucisocdriver = corefnclass.WebDriver(BASEURL)




    StartingTime = datetime.now()

    print(f"New iteration {StartingTime}")

    check_file = os.path.isfile(CourStorFileName)

    PrevStoreDict = dict()

    if check_file is False:
        with open(CourStorFileName, "w") as outfile:
            json.dump(dict(), outfile)

    else:
        #load json
        with open(CourStorFileName) as f:
            PrevStoreDict = json.load(f)
            print(PrevStoreDict)



    StoreDict = dict()
    DiffDetectBool = False
    DiffDiscordStr = ""


    for aDeptName,acourseIdList in CourseIdSearchMap.items():
        print(aDeptName,acourseIdList)
        aselectboxvaluedict["Dept"] = aDeptName

        TargetCIds = CourseIdSearchMap[aDeptName]


        asocpagetext = aucisocdriver.getSocpage(aselectboxvaluedict)

        CoursesInfoDict = PageProcessHelper.MapCourIDData(asocpagetext)

        for aCID in TargetCIds:
            TargetCidStr = str(aCID)

            StoreDict[TargetCidStr] = CoursesInfoDict[TargetCidStr]

            print(f"Course: {CourseIDNameMap[aCID]}")


            if TargetCidStr in PrevStoreDict and PrevStoreDict[TargetCidStr][1] != CoursesInfoDict[TargetCidStr][1]:
                prevLine = PrevStoreDict[TargetCidStr][1]
                NewLine = CoursesInfoDict[TargetCidStr][1]

                print(f"{bcolors.WARNING}diff detected{bcolors.ENDC}")

                addition_idxs = get_indexes_of_additions(NewLine, prevLine)
                hl_sentence2 = highlight_string_at_idxs(prevLine, addition_idxs)
                print(hl_sentence2)
                print(CoursesInfoDict[TargetCidStr][1])


                DiffDiscordStr += f"Course: {CourseIDNameMap[aCID]} Status: {CoursesInfoDict[TargetCidStr][0]}\n"
                DiffDiscordStr += (f"Previous:\n"
                                    f"```ansi\n"
                                    f"{hl_sentence2}"
                                    f"```"
                                    )
                DiffDiscordStr += (f"Difference:\n")
                DiffDiscordStr += (f"```ansi\n"
                                    f"{NewLine}"
                                    f"```"
                                    f"\n\n")



                DiffDetectBool = True

    # send a discord notification
    if DiffDetectBool:
        # discord notificatoin
        discord.post(content=f"Difference detected Summary! {StartingTime} :\n"
                             + DiffDiscordStr)

    with open(CourStorFileName, "w") as outfile:
        json.dump(StoreDict, outfile)






# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


