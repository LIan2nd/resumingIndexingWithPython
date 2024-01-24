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

# Extract pdf to Text
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save('uploads/' + file.filename)

    pdf_path = 'uploads/' + file.filename
    try:
        text = extract_text_from_pdf(pdf_path)
        # Tokenisasi kata
        tokens = word_tokenize(text)

        # Mengonversi teks menjadi lowercase
        words = [word.lower() for word in tokens if word.isalpha()]

        # Menghapus kata-kata stop words (kata-kata umum yang tidak memberi makna)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word not in stop_words]

        # Hitung frekuensi kemunculan kata
        word_freq = FreqDist(filtered_words)

        # Ambil 5 kata paling umum sebagai ringkasan
        summary_words = word_freq.most_common()

        # Membuat list berisi pasangan kata dan frekuensinya
        summary_list = [{'word': word, 'freq': freq} for word, freq in summary_words]

        # Mengirimkan data ke template HTML
        # return render_template('result.html', summary_list=summary_list)
        return render_template('index.html', summary_list=summary_list)
        # return summary_list

    except Exception as e:
        return render_template('result.html', error_message=f"Error: {e}")
        # print(f"Error: {e}")

    return jsonify({'message': 'File uploaded successfully'})

if __name__ == '__main__':
    app.run(debug=True)
