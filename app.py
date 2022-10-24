from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
from flask import Flask, jsonify, make_response, send_file
from flask import request
from flask_cors import CORS, cross_origin
import numpy as np
import pandas as pd
import base64
import re
import matplotlib.pyplot as plt
import chardet

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

slangDictionary = 'resource/new_slang_dictionary.csv'
app.json_encoder = LazyJSONEncoder


# ///
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling')
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
    "enableCORS": False,
}
swagger = Swagger(app, template=swagger_template,config=swagger_config)
# ///
@cross_origin()
@swag_from("docs/formatData.yml", methods=['POST'])
@app.route('/formatData', methods=['POST'])
def formatData():
    if 'file' in request.files:   
        file = request.files['file']
        fileName = 'data.csv'
        file.save(fileName)
        dfFromFile = pd.read_csv(fileName, encoding=checkDataType(fileName), sep='~!~')
        formattedData = []
        for index, row in dfFromFile.iterrows():
            formattedRowText = formatText(row['Tweet'])
            formattedData.append(formattedRowText)
        chartImage = createChart(dfFromFile)
        return jsonify({'text': '\n'.join(formattedData), 'image': chartImage.decode('utf-8')})
    else:
        print(request.form)
        formattedText = formatText(request.form['textvalue'])
        return formattedText

def checkDataType(file):
    with open(slangDictionary, 'rb') as rawdata:
        dataType = chardet.detect(rawdata.read(100000))
        return dataType['encoding']

def formatText(text):
    text = text.lower()
    text = text.strip()
    text = re.sub('[^0-9a-zA-Z]+', ' ', text)
    text = re.sub('\n', ' ', text)
    text = re.sub('x[a-z0-9]{2}', ' ', text)
    text = re.sub('user|rt', ' ', text)
    text = re.sub(' +', ' ', text)
    
    dfSlang = pd.read_csv(slangDictionary, encoding=checkDataType(slangDictionary))
    dicSlang = dict(zip(dfSlang.slang, dfSlang.formal))
    words = []
    for word in text.split(' '):
        if word in dicSlang.keys():
            word = dicSlang[word]
        words.append(word)
    return ' '.join(words)

def createChart(df):
    hateSpeech = df["HS"].tolist()
    countHateSpeech = pd.DataFrame(hateSpeech).sum()[0]

    abusive = df["Abusive"].tolist()
    countAbusive = pd.DataFrame(abusive).sum()[0]

    hsIndividual = df["HS_Individual"].tolist()
    countHsIndividual = pd.DataFrame(hsIndividual).sum()[0]

    hsGroup = df["HS_Group"].tolist()
    countHsGroup = pd.DataFrame(hsGroup).sum()[0]

    hsReligion = df["HS_Religion"].tolist()
    countHsReligion = pd.DataFrame(hsReligion).sum()[0]

    hsRace = df["HS_Race"].tolist()
    countHsRace = pd.DataFrame(hsRace).sum()[0]

    hsPhysical = df["HS_Physical"].tolist()
    countHsPhysical = pd.DataFrame(hsPhysical).sum()[0]

    hsGender = df["HS_Gender"].tolist()
    countHsGender = pd.DataFrame(hsGender).sum()[0]

    hsOther = df["HS_Other"].tolist()
    countHsOther = pd.DataFrame(hsOther).sum()[0]

    hsWeak = df["HS_Weak"].tolist()
    countHsWeak = pd.DataFrame(hsWeak).sum()[0]

    hsModerate = df["HS_Moderate"].tolist()
    countHsModerate = pd.DataFrame(hsModerate).sum()[0]

    hsStrong = df["HS_Strong"].tolist()
    countHsStrong = pd.DataFrame(hsStrong).sum()[0]

    headers = ['hate_speech', 'abusive', 'HS_Individual','HS_Group','HS_Religion','HS_Race','HS_Physical','HS_Gender','HS_Other','HS_Weak','HS_Moderate','HS_Strong']
    values = [countHateSpeech, countAbusive, countHsIndividual, countHsGroup, countHsReligion, countHsRace, countHsPhysical, countHsGender, countHsOther, countHsWeak, countHsModerate, countHsStrong ]

    plt.bar(headers, values, color = "#8e46a6")
    plt.xticks(rotation=90)

    plt.savefig('chart.png', bbox_inches='tight')
    return encodeFile('chart.png')


def encodeFile(fileName):
    with open(fileName, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string
if __name__ == '__main__':
    app.run()
