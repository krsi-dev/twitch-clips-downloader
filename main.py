import os
import gooey
import dotenv
import slugify
import requests
import datetime
import  twitchAPI


PROGRAM_NAME = "Twitch Clips Downloader"

"""
Main application with Gooey
to switch from CLI use --ignore-gooey
"""
@gooey.Gooey(
    # GUI setup
    program_name=f"Twitch Clips Downloader",
    required_cols=1,
    default_size=(400, 550),
)
def main():
    # ENV
    config = dotenv.dotenv_values(".env")
    
    # Gooey parser
    parser = gooey.GooeyParser()

    parser.add_argument(
        "twitch_client_id",
        type=str,
        widget="PasswordField",
        help="your twitch client ID",
        default=config.get("TWITCH_CLIENT_ID")
    )

    parser.add_argument(
        "twitch_client_secret",
        type=str,
        widget="PasswordField",
        help="your twitch client secret",
        default=config.get("TWITCH_CLIENT_SECRET")
    )

    # Required argument yaml file
    # contains twitter account keys
    # and usernames to scrape tweets from
    parser.add_argument(
        "twitch_channels",
        type=str,
        help="twitch channels separated by spaces",
        default=config.get("TWITCH_CHANNELS")
    )

    parser.add_argument(
        "select_date",
        type=str,
        help="choose a date to pull clips from",
        widget="DateChooser"
    )

    # Parse arguments
    args = parser.parse_args()

    # Load yaml and parse data
    twitch_date = args.select_date
    twitch_client_id = args.twitch_client_id
    twitch_client_secret = args.twitch_client_secret
    twitch_channels = args.twitch_channels.split()

    # Pretty print data
    print(f"{len(twitch_channels)} channels found.")

    # Twitch client
    twitch_client = twitchAPI.twitch.Twitch(
        twitch_client_id,
        twitch_client_secret
    )

    # We only want to pull clips from today
    # starting at 12:00 AM
    date_selected = datetime.datetime.strptime(twitch_date, "%Y-%m-%d")
    started_at = datetime.datetime.combine(
        date_selected,
        datetime.datetime.min.time())

    # Create folder named "clips"
    # if it does not exist
    if not os.path.exists("clips"):
        os.mkdir("clips")
    
    # Get channel metadata such as ID, username, etc.
    twitch_channels = twitch_client.get_users(logins=twitch_channels)
    
    # Loop through each channel
    for channel in twitch_channels["data"]:
        channel_name = channel["login"]

        # create clips folder
        if not os.path.exists("clips"):
            os.mkdir("clips")

        # start pagination
        next_token = 1

        # video counter to not skip same clip titles
        counter = 1

        while next_token:
            channel_clips = False

            # if next_token is 1 it means 
            # this is the first request
            if next_token == 1:
                # Get all channel's clips
                channel_clips = twitch_client.get_clips(
                    first=100,
                    started_at=started_at,
                    broadcaster_id=channel["id"], 
                )

                # set next pagination
                page = channel_clips.get("pagination")
                if page:
                    next_token = page["cursor"]
                else:
                    next_token = None

            # Page token exist
            # request for next page
            elif next_token and next_token != 1:
                channel_clips = twitch_client.get_clips(
                    first=100,
                    broadcaster_id=channel["id"], 
                    started_at=started_at,
                    after=next_token
                )

                # set next pagination
                page = channel_clips.get("pagination")
                if page:
                    next_token = page["cursor"]
                else:
                    next_token = None
            else:
                # exit out of while loop
                break
            
            clips = channel_clips["data"]
            
            # exit out of while loop
            # if there's no clips
            if not len(clips):
                break

            # Loop through each clip
            for clip in clips:
                clip_title = channel_name + f" {counter} " + slugify.slugify(clip["title"], separator=" ")
                clip_thumbnail  = clip["thumbnail_url"]
                # Open file for writing download
                clip_path = os.path.join("clips", f"{clip_title}.mp4")
                clip_file = open(clip_path, "wb")

                # Download URL of twitch clip
                download_url = clip_thumbnail.split("-preview", 1)[0] + ".mp4"
                print(f"{clip_title}.mp4", flush=True)
                counter += 1

                # Start download
                response = requests.get(download_url)
                
                # Write response in chunks 
                for chunk in response.iter_content(chunk_size=255):
                    clip_file.write(chunk)
                
                # Finally close file and move on to next clip
                clip_file.close()







if __name__ == "__main__":
    main()