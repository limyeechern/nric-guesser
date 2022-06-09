from flask import Flask, render_template, request
import jinja2

import numpy as np

yearDict = {2021: 38672, 2020: 38590, 2019: 39279, 2018: 39039, 2017: 39615, 2016: 41251, 2015: 42185, 2014: 42232,
            2013: 39720, 2012: 42663, 2011: 39654, 2010: 37967, 2009: 39570, 2008: 39826, 2007: 39490, 2006: 38317,
            2005: 37492, 2004: 37174, 2003: 37485, 2002: 40760, 2001: 41451, 2000: 46997, 1999: 43336, 1998: 43664,
            1997: 47333, 1996: 48577, 1995: 48635, 1994: 49554, 1993: 50225, 1992: 49402, 1991: 49114, 1990: 51142,
            1989: 47669, 1988: 52957, 1987: 43616, 1986: 38379, 1985: 42484, 1984: 41556, 1983: 40585, 1982: 42654,
            1981: 42250, 1980: 41217, 1979: 40779, 1978: 39441, 1977: 38364, 1976: 42783, 1975: 39948, 1974: 43268,
            1973: 48269, 1972: 49678, 1971: 47088, 1970: 45934, 1969: 44562, 1968: 47241, 1967: 50560, 1966: 54680,
            1965: 55725, 1964: 58217, 1963: 59530, 1962: 58977, 1961: 59930, 1960: 61775}

print("Input last 4 alphanumerics, ie 123A")


# nric = input().lower()

def getBestPrediction(answer, totalBirths, month):
    test = [int(i[3:5]) for i in answer]
    arr = []
    for y in test:
        difference = abs(y * 1150 - totalBirths * (month / 12))
        arr.append(difference)
    index = np.argmin(arr)
    pred = answer[index]
    del answer[index]
    return pred


def predictNric(nric, year, month):
    fullNric = ["", "", "", "", "", "", "", "", ""]
    temp = 5
    for char in nric:
        fullNric[temp] = char
        temp += 1
    if year <= 1967:
        fullNric[1] = "1"
        fullNric[2] = "5"
        fullNric[0] = "S"
    else:
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

    alpha = ["j", "z", "i", "h", "g", "f", "e", "d", "c", "b", "a"]
    mod = alpha.index(fullNric[-1])
    answer = []
    for possibleInt in range(mod, 262, 11):
        targetInt = possibleInt - int(fullNric[1]) * 2 - int(fullNric[2]) * 7 - int(fullNric[5]) * 4 - int(
            fullNric[6]) * 3 - int(fullNric[7]) * 2
        if fullNric[0] == "T":
            targetInt -= 4
        for pos4 in range(0, 10):
            if targetInt - (pos4 * 5) < 0:
                break
            targetInt4 = targetInt - pos4 * 5
            for pos3 in range(0, 10):
                if targetInt4 - (pos3 * 6) < 0:
                    break
                targetInt3 = targetInt4 - pos3 * 6
                if targetInt3 == 0:
                    copyNric = fullNric.copy()
                    copyNric[3], copyNric[4], = pos3, pos4
                    tempStr = ''.join(map(str, copyNric))
                    answer.append(tempStr)
                else:
                    continue
    answer = sorted(answer)

    display = []
    totalBirths = yearDict[year]
    for i in range(2):
        display.append(getBestPrediction(answer, totalBirths, month))

    return display

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        nric = request.form.get("nric")
        nric = nric.lower()
        year = int(request.form.get("year"))
        month = int(request.form.get("month"))
        result = predictNric(nric, year, month)
        print(result)
        return render_template('new.html', result=result)
    else:
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
