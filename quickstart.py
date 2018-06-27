# Sample Python code for user authorization

import os
import json
import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

#get information of this channel based on username
def channels_list_by_username(service, **kwargs):
    results = service.channels().list(
        **kwargs
    ).execute()

    return results

#get all the video data from based on channel's playlist ID
def fetch_all_videos_from_playlistId(service, playlistId):
    results = service.playlistItems().list(
        part='contentDetails',
        playlistId=playlistId,
        maxResults=50
    ).execute()

    nextPageToken = results.get('nextPageToken')

    #repeat until there isn't another page of items
    while ('nextPageToken' in results):
        nextPage = service.playlistItems().list(
            part='contentDetails',
            playlistId=playlistId,
            maxResults=50,
            pageToken=nextPageToken
        ).execute()
        results['items'] = results['items'] + nextPage['items'] #concatenate page results together


        if 'nextPageToken' not in nextPage:
            results.pop('nextPageToken',None)
        else:
            nextPageToken = nextPage['nextPageToken']
    return results
#   print('This channel\'s ID is %s. Its title is %s, and it has %s views.' %
#        (results['items'][0]['id'],
#         results['items'][0]['snippet']['title'],
#         results['items'][0]['statistics']['viewCount']))


def get_all_videos_from_videoList(videoList):
    
    #get first item
    firstVideoId = videoList['items'][0]['contentDetails']['videoId']
    results = service.videos().list(
            part='snippet,contentDetails,statistics',
            id = firstVideoId
            ).execute()

    #get the rest
    
    for playlistItemIndex in range(1,videoList['pageInfo']['totalResults']):
        videoId =  videoList['items'][playlistItemIndex]['contentDetails']['videoId']
        nextResult = service.videos().list(
            part='snippet,contentDetails,statistics',
            id = videoId
        ).execute()

        results['items'] = results['items'] + nextResult['items']

    return results
        

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()  # get authentication

    # use API
    channels = channels_list_by_username(service,
                                         part='contentDetails,statistics',
                                         forUsername='tokopedia')  # grab playlist ID and channel statistics

    #get ID of this channel's playlist which contains all of the channel's uploaded videos
    playlistId = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    #get list of video data
    videoList = fetch_all_videos_from_playlistId(service, playlistId)

    #get ID of a video 
    videoData = get_all_videos_from_videoList(videoList)


    with open('data.json','w') as outfile:
        json.dump(videoData,outfile)
