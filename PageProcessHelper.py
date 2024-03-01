#the page processing helper functions

import re
from collections import namedtuple

def MapCourIDData(aWebSocPage):
    CourseNumTextPat = re.compile(r"^(\d{5})(?:.*) +(\w+)$")


    RetDictionary = dict()

    ThePageLineList = list(filter(bool,[str.strip() for str in aWebSocPage.splitlines()]))

    for aLineNum,aLine in enumerate(ThePageLineList):

        TheMatchedObj = CourseNumTextPat.match(aLine)
        if TheMatchedObj is not None:
            MatchObjGroups = TheMatchedObj.groups()

            courseList = list()
            courseList.append(MatchObjGroups[1])
            courseList.append(aLine)


            RetDictionary[MatchObjGroups[0]] = courseList

    return RetDictionary

        # print(CourseNumTextPat.match(aLine))

