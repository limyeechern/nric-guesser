
from flask import Flask, render_template, request

import numpy as np

"""
yearDict represents a hash map of the total number of births for the particular year. 
Data obtained from https://tablebuilder.singstat.gov.sg/table/TS/M810091
"""

yearDict = {2021: 38672, 2020: 38590, 2019: 39279, 2018: 39039, 2017: 39615, 2016: 41251, 2015: 42185, 2014: 42232,
            2013: 39720, 2012: 42663, 2011: 39654, 2010: 37967, 2009: 39570, 2008: 39826, 2007: 39490, 2006: 38317,
            2005: 37492, 2004: 37174, 2003: 37485, 2002: 40760, 2001: 41451, 2000: 46997, 1999: 43336, 1998: 43664,
            1997: 47333, 1996: 48577, 1995: 48635, 1994: 49554, 1993: 50225, 1992: 49402, 1991: 49114, 1990: 51142,
            1989: 47669, 1988: 52957, 1987: 43616, 1986: 38379, 1985: 42484, 1984: 41556, 1983: 40585, 1982: 42654,
            1981: 42250, 1980: 41217, 1979: 40779, 1978: 39441, 1977: 38364, 1976: 42783, 1975: 39948, 1974: 43268,
            1973: 48269, 1972: 49678, 1971: 47088, 1970: 45934, 1969: 44562, 1968: 47241, 1967: 50560, 1966: 54680,
            1965: 55725, 1964: 58217, 1963: 59530, 1962: 58977, 1961: 59930, 1960: 61775}

"""
Explanation of the algorithm in comments
"""
def predictNric(nric, year, month):
    fullNric = ["", "", "", "", "", "", "", "", ""]
    position = 5
    # We first fill up our NRIC with all the data we have, the last 4 alphanumeric characters
    # and the year that was given
    for char in nric:
        fullNric[position] = char
        position += 1
    # People born before 1967 do not have the birth year as the first two characters
    # https://sg.theasianparent.com/singapore-nric-number point 3
    if year <= 1967:
        fullNric[1] = "1"
        fullNric[2] = "5"
        fullNric[0] = "S"
    else:
        # Handling case of people born from 2000 to 2009
        if len(str(year % 100)) == 1:
            fullNric[1] = "0"
            fullNric[2] = str(year % 100)[0]
            fullNric[0] = "T"
        else:
            fullNric[1] = str(year % 100)[0]
            fullNric[2] = str(year % 100)[1]
            if year <= 2000:
                fullNric[0] = "S"
            else:
                fullNric[0] = "T"
    # NRIC algorithm: https://ivantay2003.medium.com/creation-of-singapore-identity-number-nric-24fc3b446145
    # The index of the character maps to the alphabet. Refer to algorithm.
    alpha = ["j", "z", "i", "h", "g", "f", "e", "d", "c", "b", "a"]
    # Obtain the last character of your NRIC and identify the value of it from the list alpha.
    mod = alpha.index(fullNric[-1])
    answer = []
    flag = False
    # We have to reverse engineer by following the algorithm. For example, S1234567A
    # Given the birth year, we have the first two digits, given the last 4 alphanumerics, we have the last 3 numbers
    # According to the algorithm, the sum of all the values modulo 11 should be the value of variable mod.
    # We iterate from the value of mod, with jumps of 11
    for possibleInt in range(mod, 262, 11):
        # We get the sum of position1 * 2, position2 * 7, position5 * 4, position6 * 3 and position7*2.
        targetInt = possibleInt - int(fullNric[1]) * 2 - int(fullNric[2]) * 7 - int(fullNric[5]) * 4 - int(
            fullNric[6]) * 3 - int(fullNric[7]) * 2
        # According to algorithm, people born after 2000 have an additional +4 to the total sum
        # So we minus 4 in our target
        if fullNric[0] == "T":
            targetInt -= 4
        # Negative values are not wanted
        if targetInt < 0:
            continue
        # We try to find the first possible value of position4 given position3 == 0. And break out of the loop.
        # This greatly enhances the efficiency of the algorithm to reduce search space.
        for pos4 in range(0, 10):
            if targetInt - (pos4 * 5) == 0:
                answer.append(f"0{pos4}")
                flag = True
                break
        if flag:
            break
    # We know that the differences of all possible NRIC differ by only 11 in position3,4.
    # Therefore, we just iterate by summing 11 to get a list of possible position3,4s
    while True:
        prev = int(answer[-1])
        if (prev + 11) > 100:
            break
        answer.append(str(prev + 11))
    # I only have 2 chances to guess your NRIC so I only created a list of 2 possible answers.
    display = [[], []]
    totalBirths = yearDict[year]
    for i in range(2):
        # Refer to comments below to understand the function getBestPrediction
        bestPred = getBestPrediction(answer, totalBirths, month, nric[:3])
        copyNric = fullNric.copy()
        copyNric[3] = bestPred[0]
        copyNric[4] = bestPred[1]
        tempStr = ''.join(map(str, copyNric)).upper()
        display[i] = tempStr
    return display


def getBestPrediction(answer, totalBirths, month, lastThree):
    test = [int(i+lastThree) for i in answer]
    arr = []
    for y in test:
        # So apparently (correct me if I am wrong but this gets me the answer) the positions 3 onwards
        # provides information of your birth as the ith baby of the year.
        # Given the number of births of the year, we divide it by the month corrected to the middle of the month,
        # to obtain your expected i position of birth, we then calculate the differences.
        # for example, individual SXX01234A is approximately the 1234th child born in that year.
        difference = abs(y - totalBirths * ((month-0.5)/ 12))
        arr.append(difference)
    # We obtain the argmin which is the smallest difference between y and the expected number of babies till the
    # month of the year
    index = np.argmin(arr)
    pred = answer[index]
    # Remove this from the list to get the second prediction
    del answer[index]
    return pred


app = Flask(__name__)

# Flask
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        try:
            nric = request.form.get("nric")
            nric = nric.lower()
            year = int(request.form.get("year"))
            month = int(request.form.get("month"))
            result = predictNric(nric, year, month)
            result[0] = result[0].upper()
            result[1] = result[1].upper()
            return render_template('new.html', result=result)
        except Exception:
            return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
