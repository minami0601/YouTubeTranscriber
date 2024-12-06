import os
from flask import Flask, render_template, request, jsonify, make_response
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import NoTranscriptAvailable, TranscriptsDisabled
from utils import extract_video_id

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "youtube-transcriber-secret"

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        url = request.form.get('url', '')
        video_id = extract_video_id(url)
        
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # まず日本語の文字起こしを試みる
        try:
            transcript = transcript_list.find_transcript(['ja'])
        except NoTranscriptAvailable:
            # 日本語が無い場合は英語を試みる
            try:
                transcript = transcript_list.find_transcript(['en'])
            except NoTranscriptAvailable:
                # 利用可能な言語のリストを取得
                available_transcripts = transcript_list.manual_transcripts
                if not available_transcripts:
                    available_transcripts = transcript_list.generated_transcripts
                
                if not available_transcripts:
                    raise NoTranscriptAvailable("No transcripts available")
                
                # 最初に見つかった文字起こしを使用
                transcript = list(available_transcripts.values())[0]
        
        transcript_data = transcript.fetch()
        full_transcript = ' '.join([entry['text'] for entry in transcript_data])
        
        return jsonify({
            'success': True,
            'transcript': full_transcript,
            'video_id': video_id,
            'language': transcript.language_code
        })

    except (TranscriptsDisabled, NoTranscriptAvailable) as e:
        return jsonify({
            'error': 'この動画の文字起こしは利用できません'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'エラーが発生しました: {str(e)}'
        }), 500

@app.route('/download-transcript', methods=['POST'])
def download_transcript():
    try:
        transcript = request.json.get('transcript', '')
        if not transcript:
            return jsonify({'error': 'テキストが見つかりません'}), 400
            
        response = make_response(transcript)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=transcript.txt'
        return response
        
    except Exception as e:
        return jsonify({
            'error': f'ダウンロード中にエラーが発生しました: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
