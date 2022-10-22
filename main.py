import os
import yaml
import json
import gooey
import requests
import datetime
import  twitchAPI

"""
Main application with Gooey
to switch from CLI use --ignore-gooey
"""
@gooey.Gooey(
    # GUI setup
    program_name=f"Twitter Auto Like",
    required_cols=1,
    default_size=(400, 400),
)
def main():
    # Gooey parser
    parser = gooey.GooeyParser()

    # Required argument yaml file
    # contains twitter account keys
    # and usernames to scrape tweets from
    parser.add_argument(
        "yaml_file",
        widget="FileChooser",
        help="select file to load"
    )

    # Parse arguments
    args = parser.parse_args()

    # Load yaml and parse data
    data = yaml.load(
        open(args.yaml_file, "r"), 
        yaml.loader.SafeLoader)

    # Pretty print data
    print(json.dumps(data, indent=2), flush=True)

    # Twitch client
    twitch_client = twitchAPI.twitch.Twitch(
        data["twitch_client_id"],
        data["twitch_client_secret"]
    )

    # We only want to pull clips from today
    # starting at 12:00 AM
    started_at = datetime.datetime.combine(
        datetime.date.today(),
        datetime.datetime.min.time())

    # Create folder named "clips"
    # if it does not exist
    if not os.path.exists("clips"):
        os.mkdir("clips")
    
    # Get channel metadata such as ID, username, etc.
    twitch_channels = twitch_client.get_users(
        logins=data["channels"])["data"]
    
    # Loop through each channel
    for channel in twitch_channels:
        # Folder where clips will be
        # after downloading
        print(channel, flush=True)
        channel_folder = os.path.join(
            "clips",
            channel["login"]
        )

        # Create channel folder 
        # if not exist    
        if not os.path.exists(channel_folder):
            os.mkdir(channel_folder)
    
        # Get all channel's clips from today
        channel_clips = twitch_client.get_clips(
            started_at=started_at,
            broadcaster_id=channel["id"], 
        )["data"]

        # Loop through each clip
        for clip in channel_clips:

            # Open file for writing download
            clip_file = open(
                os.path.join(
                    channel_folder,
                    f"{clip['title']}.mp4"),
                "wb"
            )
            print(json.dumps(clip, indent=2), flush=True)

            
            # Download URL of twitch clip
            download_url = clip["thumbnail_url"] \
                .split("-preview", 1)[0] + \
                ".mp4"
            print(f"downloading ~ {download_url}", flush=True)


            # Start download
            response = requests.get(download_url)
            
            # Write response in chunks 
            for chunk in response.iter_content(chunk_size=255):
                clip_file.write(chunk)
            
            # Finally close file and move on to next clip
            clip_file.close()







if __name__ == "__main__":
    main()