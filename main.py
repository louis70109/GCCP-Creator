import tempfile
from google.cloud import speech, storage
import os
import uvicorn

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()

from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()

google_temp = tempfile.NamedTemporaryFile(suffix='.json')
fire_temp = tempfile.NamedTemporaryFile(suffix='.json')
try:
    GOOGLE_KEY = os.environ.get('GOOGLE_KEY', '{}')
    google_temp.write(GOOGLE_KEY.encode())
    google_temp.seek(0)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_temp.name
except:
    google_temp.close()


def transcribe_gcs(bucket, audio):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    print('-------------Start to recognize')
    client = speech.SpeechClient()
    gcs_uri = f"gs://{bucket}/{audio}"
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=48000,
        language_code="zh-TW",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result()
    return response


def upload_data_to_gcs(bucket_name, data, target_key, meta=None):
    # if type(data) == str:
    #     data = data.encode('big5')

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(target_key)
        blob.upload_from_string(data, content_type=meta)
        return blob.public_url

    except Exception as e:
        print(e)

    return None


def contents_dict_to_subtitle(contents, vtt=False):
    # [{
    #         "description": "我覺不得了。",
    #         "id": 0,
    #         "end_time": "0:00:59.200",
    #         "start_time": "0:00.00"},
    #         {"id": 1,
    #          "end_time": "0:01:59.600",
    #          "start_time": "0:00:59.900",
    #          "description": "Ok有經驗？"}]

    result = 'WEBVTT\n\n' if vtt else ''
    content_len, idx, count = len(contents), 0, 0

    # Arrange firebase data list sequence
    while True:
        try:
            content = contents[idx]
            if content.get("id") == count:
                result += f'{content.get("id")}\n{content.get("start_time")} --> {content.get("end_time")}\n{content.get("description")}\n\n'
                contents.pop(idx)
                count += 1
                idx = 0
            else:
                idx += 1
            if len(contents) == 0:
                break
        except IndexError:
            break

    return result


def time_transfer(time_serial) -> str:
    # example: 2:46:40.10000000
    time = str(time_serial)[:11]
    import re
    if re.search("[0-9]*:[0-9]+:[0-9]+", time) and len(time) == 7:
        time_obj = time.split(":")
        time = time_obj[0] + ":" + time_obj[1] + ":" + time_obj[2] + ".000"
    return time


@app.route('/', methods=['POST'])
async def index(request: Request):
    data = await request.json()

    if data['contentType'] == 'audio/mpeg':
        scripts = transcribe_gcs(data['bucket'], data['name'])
        results = scripts.results

        subtitle = []
        count = 0
        for word in list(results[0].alternatives[0].words):
            subtitle.append({
                'id': count,
                'description': word.word,
                'start_time': time_transfer(word.start_time),
                'end_time': time_transfer(word.end_time)
            })
            count += 1
        vtt_sub = subtitle.copy()
        print('SRT dict done')
        print('Generate to SRT format')
        srt_string_result = contents_dict_to_subtitle(subtitle)
        print('wait to upload to gcs')
        upload_data_to_gcs(data['bucket'], srt_string_result, f'{data["name"]}.srt',
                           meta='text/srt')
        print('Generate to VTT format')
        vtt_string_result = contents_dict_to_subtitle(vtt_sub, vtt=True)
        print('wait to upload to gcs')
        upload_data_to_gcs(data['bucket'], vtt_string_result, f'{data["name"]}.vtt',
                           meta='text/vtt')
        print('upload success')
        return "HI", 200


if __name__ == "__main__":
    reload = True if os.getenv('API_ENV') != 'production' else False
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=reload)
