from flask import Flask, render_template, request, send_from_directory, jsonify,send_file
import os
from gtts import gTTS
import wave
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import pickle
import speech_recognition as sr
import assemblyai as aai
import nltk
import bs4
import ProWritingAidSDK
from ProWritingAidSDK.rest import ApiException
from pprint import pprint

app = Flask(__name__)



UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER







# with open('gramformer_wrapper.pkl', 'rb') as file:
#     loaded_gramformer_wrapper = dill.load(file)


# with open('grammar_corrector_model.pkl', 'rb') as file:
#     loaded_data = pickle.load(file)

# loaded_tokenizer = loaded_data['tokenizer']
# loaded_model = loaded_data['model']
# loaded_torch_device = loaded_data['torch_device']

# def correct_grammar(input_text, num_return_sequences):
#     batch = loaded_tokenizer([input_text], truncation=True, padding='max_length', max_length=64, return_tensors="pt").to(
#         loaded_torch_device)
#     translated = loaded_model.generate(**batch, max_length=64, num_beams=4, num_return_sequences=num_return_sequences,
#                                        temperature=1.5)
#     tgt_text = loaded_tokenizer.batch_decode(translated, skip_special_tokens=True)
#     return tgt_text

configuration = ProWritingAidSDK.Configuration()
configuration.host = 'https://api.prowritingaid.com'
# To get an API code with 500 test credits go to https://prowritingaid.com/en/App/Api
configuration.api_key['licenseCode'] = 'B8DD0E30-EAF5-4E7D-9112-FF6D9476F22D'
api_instance = ProWritingAidSDK.TextApi(ProWritingAidSDK.ApiClient('https://api.prowritingaid.com'))




















pa=""
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/text', methods=['POST'])
def text():
    user_input = request.form['user_input']
    wrong_sent=user_input
    try:
        api_request = ProWritingAidSDK.TextAnalysisRequest(wrong_sent,
                                                       ["grammar"],
                                                       "General",
                                                       "en")
        api_response = api_instance.post(api_request)
    
    except ApiException as e:
        print("Exception when calling TextAnalysisRequest->get: %s\n" % e)
        
    tags = api_response.result.tags
    correct_sentence = wrong_sent
    for tag in reversed(tags):
        replacement = '' if tag.suggestions[0] == '(omit)' else tag.suggestions[0] 
        correct_sentence = correct_sentence[0:tag.start_pos] + replacement + correct_sentence[tag.end_pos+1:]
    print('Incorrect Sentence')
    print(wrong_sent)
    print('Correct Sentence')
    print(correct_sentence)
    print('Done')
    return correct_sentence




@app.route('/audio', methods=['POST'])
def audio():
    language = 'en'
    filename = 'output.mp3'
    if 'audio_input' not in request.files:
        return jsonify({'error': 'No audio file provided'})

    audio_file = request.files['audio_input']
    if audio_file and audio_file.filename.endswith('.txt'):
        # It's a text file
        file_content = audio_file.read().decode('utf-8')
        return render_template('text.html',text_content=file_content)






    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'})
    



    audio_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'user_audio.wav')
    audio_file.save(audio_filename)





    # aai.settings.api_key = "8de27b71fe104713ba094644d8b252a0"
    # transcriber = aai.Transcriber()
    # transcript = transcriber.transcribe(audio_filename)
    # print(transcript.text)
    # text=transcript.text
    recognizer = sr.Recognizer()
    text="Sorry cant find"
    with sr.AudioFile(audio_filename) as audio_file:
        audio_data = recognizer.record(audio_file)

        try:
            text = recognizer.recognize_google(audio_data)
            print(f"Spoken text: {text}")
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(os.path.join('uploads', filename))
    audio_file_name1 = 'output.mp3'
    audio_file_path1 = os.path.join('uploads', audio_file_name1)


    # print(audio_file)
    # print(audio_filename)
    # print(audio_basename)
    return render_template('audio.html', audio_file_path=audio_filename, audio_basename=audio_file_path1,text=text)

@app.route('/realtime', methods=['POST', 'GET'])
def realtime():
    print("alredy in realtime")
    if request.method == "POST":
        audio_data = request.files['audio_data']
        
        if audio_data:
            # Save the file to the "uploads" folder (create the folder if it doesn't exist)
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, 'file.wav')
            
            audio_data.save(file_path)
            pa=file_path
            if os.path.isfile(file_path):
                print("File saved at:", file_path)

        return render_template('chat.html', request_method="POST" )   
    else:
        return render_template("chat.html", request_method="GET")






@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_files', methods=['GET'])
def delete_files():
    try:
        # Get the list of files in the upload folder
        files = os.listdir(app.config['UPLOAD_FOLDER'])

        # Loop through the files and delete each one
        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            os.remove(file_path)

        return jsonify({'success': True, 'message': 'Files deleted successfully'})

    except Exception as e:
        return jsonify({'error': True, 'message': str(e)})

@app.route("/play", methods=['POST', 'GET'])
def play_boy():
    audio_file_name = 'file.wav'
    audio_file_path = os.path.join('uploads', audio_file_name)
    language = 'en'
    filename = 'output.mp3'
    
    # recognizer = sr.Recognizer()
    # with sr.AudioFile(audio_file_path) as audio_file:
    #     audio_data = recognizer.record(audio_file)

    #     try:
    #         text = recognizer.recognize_google(audio_data)
    #         print(f"Spoken text: {text}")
    #     except sr.UnknownValueError:
    #         print("Speech Recognition could not understand audio")
    #     except sr.RequestError as e:
    #         print(f"Could not request results from Google Speech Recognition service; {e}")

    
    aai.settings.api_key = "8de27b71fe104713ba094644d8b252a0"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file_path)
    print(transcript.text)
    text=transcript.text








    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(os.path.join('uploads', filename))

    return render_template("play.html", x=text, audio_file=filename)

@app.route("/get_audio/<filename>")
def get_audio(filename):
    file_path = os.path.join('uploads', filename)
    return send_file(file_path, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True)


