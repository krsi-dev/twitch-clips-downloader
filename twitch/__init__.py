import os
import slugify
import requests
import datetime
import twitchAPI

class Twitch:
    def __init__(
        self,
        twitch_channel,
        twitch_client_id,
        twitch_client_secret,
        clip_started_at,
        clip_output_folder
    ) -> None:
        
        self.twitch_channel = twitch_channel

        self.twitch_client = twitchAPI.Twitch(
            twitch_client_id,
            twitch_client_secret
        )
        
        self.clip_started_at = datetime.datetime.combine(
            datetime.datetime.strptime(clip_started_at, "%Y-%m-%d"),
            datetime.datetime.min.time()
        )

        self.clip_output_folder = clip_output_folder

        self.clip_token = 1
        self.clip_count = 1


    def get_clips(self):
        channel = self.twitch_client.get_users(logins=[self.twitch_channel])["data"][0]
        
        while self.clip_token:

            if self.clip_token == 1:
                clips = self.twitch_client.get_clips(
                    first=100,
                    started_at=self.clip_started_at,
                    broadcaster_id=channel.get("id"), 
                )

                self.clip_token = clips.get("pagination")
            
            elif self.clip_token:
                clips = self.twitch_client.get_clips(
                    first=100,
                    broadcaster_id=channel.get("id"), 
                    started_at=self.clip_started_at,
                    after=self.clip_token
                )

                self.clip_token = clips.get("pagination")
            else:
                break

            for clip in clips["data"]:
                clip_filename = f"{self.twitch_channel} {self.clip_count} " + \
                    slugify.slugify(clip.get("title"), separator=" ")
                
                clip_filepath = os.path.join(
                    self.clip_output_folder,
                    f"{clip_filename}.mp4"
                )


                clip_download_url = clip.get("thumbnail_url") \
                    .split("-preview", 1)[0] + \
                    ".mp4"

                download_file = open(clip_filepath, "wb")
                download_response = requests.get(clip_download_url)

                for download_chunk in download_response.iter_content(chunk_size=255):
                    download_file.write(download_chunk)
                    
                self.clip_count += 1
                download_file.close()