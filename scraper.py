import requests
import googleapiclient.discovery
import csv

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = ""

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)

# searching function for channel id with given name
def get_channel_id(channel_name, DEVELOPER_KEY):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key" \
          f"={DEVELOPER_KEY}"
    response = requests.get(url)
    channel_id = response.json()['items'][0]['id']['channelId']
    return channel_id


def start_search(channel_name):
    channel_id = get_channel_id(channel_name, DEVELOPER_KEY)
    if not channel_id:
        print("Channel could not be found")
    else:
        all_results = []
        next_page_token = None
        comment_count = 0

        while True:
            # only 100 comments can be obtained with a single request
            # pageToken will be changed at every 100 comment and will be point next comments
            request = youtube.commentThreads().list(
                part="snippet",
                allThreadsRelatedToChannelId=channel_id,
                maxResults=100,
                pageToken=next_page_token
            )

            response = request.execute()

            # every item has a comment in it
            for item in response['items']:

                # formatting the result
                comment = item['snippet']['topLevelComment']['snippet']
                all_results.append([comment['authorDisplayName'],
                                    comment['textOriginal'],
                                    comment['publishedAt'][:10],
                                    comment['likeCount']])
                comment_count += 1
                print(f'comment count:{comment_count}')

            # if there are more comments, the loop will be continue with new token
            if "nextPageToken" in response.keys():
                next_page_token = response["nextPageToken"]

            # end of the comments, time to save results if comments are found
            else:
                if all_results:
                    fields = ['Author Name', 'Text', 'Published At', 'Like Count']
                    with open('results.csv', 'w', encoding="utf-8") as f:
                        write = csv.writer(f, lineterminator='\n')
                        write.writerow(fields)
                        write.writerows(all_results)
                break
