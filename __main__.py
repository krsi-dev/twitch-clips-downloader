import os
import eel
from twitch import Twitch

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

eel.init("web")

@eel.expose
def submit(config):
    clip_output_folder = os.path.join(ROOT_DIR, config["twitch_channel"])

    if not os.path.exists(clip_output_folder):
        os.mkdir(clip_output_folder)

    Twitch(
            twitch_channel=config["twitch_channel"],
            twitch_client_id=config["twitch_client_id"],
            twitch_client_secret=config["twitch_client_secret"],
            clip_started_at=config["clip_started_at"],
            clip_output_folder=clip_output_folder
    ).get_clips()

eel.start('index.html', size=(275, 400))
