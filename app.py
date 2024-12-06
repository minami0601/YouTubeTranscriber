import os
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import NoTranscriptAvailable, TranscriptsDisabled
from utils import extract_video_id

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "youtube-transcriber-secret"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        url = request.form.get('url', '')
        video_id = extract_video_id(url)
        
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all transcript parts into one text
        full_transcript = ' '.join([entry['text'] for entry in transcript_list])
        
        return jsonify({
            'success': True,
            'transcript': full_transcript,
            'video_id': video_id
        })

    except (TranscriptsDisabled, NoTranscriptAvailable):
        return jsonify({
            'error': 'この動画の文字起こしは利用できません'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500
