from ring_doorbell import Ring
import urllib.request
import random
import string
import datetime
from os import listdir
from os.path import isfile, join
import requests
import json
import os


class RingBell:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def fetch_video_urls(self, username, password):
        ring_obj = Ring(username, password)
        number_of_cam = len(ring_obj.devices['stickup_cams'])
        video_urls = []
        for counter in range(0, number_of_cam):
            stickup_cam = ring_obj.stickup_cams[counter]
            counter = counter + 1
            video_urls.append(stickup_cam.recording_url(stickup_cam.last_recording_id))

        return video_urls

    def download_cam_videos(self, video_urls):

        for video in video_urls:
            filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)]) + str(datetime.datetime.now()) + ".mp4"
            urllib.request.urlretrieve(video, "videos/"+filename)

    def upload_to_gdrive(self, access_token, parent_id, upload_api_url):
        onlyfiles = [f for f in listdir("videos") if isfile(join("videos", f))]
        for video_files in onlyfiles:
            headers = {
                "Authorization": access_token}
            para = {
                "name": video_files,
                "parents": [parent_id]
            }
            files = {
                'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
                'file': open("videos/"+video_files, "rb")
            }
            r = requests.post(
                upload_api_url,
                headers=headers,
                files=files
            )
            print(r.text)

    def clean_videos_folder(self, folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)



with open('config.json') as config_file:
    config = json.load(config_file)

username = config['ring_doorbell']['username']
password = config['ring_doorbell']['password']
access_token = "Bearer " + config['gdrive']['access_token']
upload_api_url = config['gdrive']['upload_api_url']
folder_parentid = config['gdrive']['folder_parentId']

ringObj = RingBell(username, password)
print('Fetching videos from the RingBell Server...')
video_urls = ringObj.fetch_video_urls(username, password)
print("Fetched URLS: ", video_urls)
print('Downloading videos to local drive...')
ringObj.download_cam_videos(video_urls)
print('Download Finished, you may look files in the Videos folder.')
print('Uploading file started...')
ringObj.upload_to_gdrive(access_token, folder_parentid, upload_api_url)
print('Clearing videos folders...')
folder = "videos"
ringObj.clean_videos_folder(folder)
print('Videos folder cleaned.')







