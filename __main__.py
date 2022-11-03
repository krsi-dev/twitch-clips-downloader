import argparse
from twitch import Twitch

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python ./src"
    )

    parser.add_argument(
        "twitch_channel",
        type=str,
        help="Name of the channel"
    )

    parser.add_argument(
        "twitch_client_id",
        type=str,
        help="Twitch API Client ID",
    ),

    parser.add_argument(
        "twitch_client_secret",
        type=str,
        help="Twitch API Client Secret"
    )

    parser.add_argument(
        "clip_started_at",
        type=str,
        help="Pull clips from a certain starting date"
    )

    kwargs = parser.parse_args()

    Twitch(**kwargs).get_clips()