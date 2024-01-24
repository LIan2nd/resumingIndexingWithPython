from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify  
import pdfplumber
import nltk

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('tagsets')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.probability import FreqDist
from collections import defaultdict

app = Flask(__name__)

@app.route('/')
def landing_page():
    summary_list = []
    return render_template('index.html', summary_list=summary_list)

# Text to Summary
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Extract pdf to Text
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text
# End Extract pdf to Text

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save('uploads/' + file.filename)
    pdf_path = 'uploads/' + file.filename

    try:
        text = extract_text_from_pdf(pdf_path)

        def _create_frequency_table(text_string) -> dict:
          stopWords = set(stopwords.words("english"))
          words = word_tokenize(text_string)
          ps = PorterStemmer()

          freqTable = dict()
          for word in words:
            word = ps.stem(word)
            if word in stopWords:
              continue
            if word in freqTable:
              freqTable[word] +=1
            else:
              freqTable[word] = 1

          return freqTable
        # Run Create Frequency
        p = _create_frequency_table(text)

        # Sent Token
        q = sent_tokenize(text)

        # Function Score Sentences
        def _score_sentences(sentences, freqTable) -> dict:
          sentenceValue = dict()
          for sentence in sentences:
            word_count_in_sentence = (len(word_tokenize(sentence)))
            for wordValue in freqTable:
              if wordValue in sentence.lower():
                if sentence[:10] in sentenceValue:
                  sentenceValue[sentence[:10]] += freqTable[wordValue]
                else:
                  sentenceValue[sentence[:10]] = freqTable[wordValue]
            sentenceValue[sentence[:10]] = sentenceValue[sentence[:10]] // word_count_in_sentence
          return sentenceValue

        r = _score_sentences(q, p)

        def _find_average_score(sentenceValue) -> int:
            sumValues = 0
            for entry in sentenceValue:
                sumValues += sentenceValue[entry]

            # Average value of a sentence from original text
            average = int(sumValues / len(sentenceValue))
            return average

        s = _find_average_score(r)

        def _generate_summary(sentences, sentenceValue, thershold):
            sentence_count = 0
            summary = ''

            for sentence in sentences:
                if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] > (thershold):
                    summary += "" + sentence
                    sentence_count += 1
            return  summary
        # End Text to Summary

        # Create Resume
        resume = _generate_summary(q, r, s)

        # Mengirimkan data ke template HTML
        # return Resume
        return render_template('index.html', resume=resume)

    except Exception as e:
        return render_template('index.html', error_message=f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
