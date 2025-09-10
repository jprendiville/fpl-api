""" Send a tweet with predictions """
import os
import sys
import logging
from django.utils import timezone
from io import BytesIO
import django
import tweepy

from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

from common.utils import get_last_gameweek, get_next_gameweek

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fpl.settings")
django.setup()

from players.models import PlayerPrediction
from fpl.properties.properties import get_properties
from tweets.models import Tweet

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def draw_headers(draw, event, header_font):
    """ Draw the header """

    title_text = f"Gameweek {event.id}"
    title_position = (30, 20)  # Left-aligned title
    draw.text(title_position, title_text, font=header_font, fill='black')

    # Add column headers (left-aligned)
    column_headers = ["Name", "Opponent", "Prediction"]
    column_widths = [170, 100, 100]
    if event.is_current:
        column_headers.append("Actual")
        column_widths.append(100)
    row_position = (30, 60)  # Adjust as needed
    for i, header in enumerate(column_headers):
        draw.text((row_position[0] + sum(column_widths[:i]), row_position[1]),
                  header, font=header_font, fill='black')


def draw_predictions(draw, event, predictions, text_font):
    """ Draw the predictions """

    row_position = (30, 90)  # Adjust as needed
    for result in predictions:
        name = result.player.shortened_name()
        team = result.player.player_team.short_name
        opponent = result.get_opponent_short()
        prediction = result.prediction
        actual = result.total_points

        # Draw status icon
        if event.is_next:
            draw_status_icon(draw, result.player.chance_of_playing_next_round,
                             (row_position[0] - 25, row_position[1]),
                             text_font)

        draw.text((row_position[0], row_position[1]), name + " (" + team + ")",
                  font=text_font, fill='black')
        draw.text((row_position[0] + 170, row_position[1]), opponent,
                  font=text_font, fill='black')
        draw.text((row_position[0] + 270, row_position[1]), str(prediction),
                  font=text_font, fill='black')
        if event.is_current:
            draw.text((row_position[0] + 370, row_position[1]), str(actual),
                      font=text_font, fill='black')

        # Move down to the next row
        row_position = (row_position[0], row_position[1] + 30)


def add_watermark(project_root, properties, image):
    """ Add watermark to the image """
    watermark_path = os.path.join(project_root, 'fpl',
                                  properties.watermark)
    watermark = Image.open(watermark_path)

    # Ensure that the watermark has an alpha channel for transparency
    watermark = watermark.convert("RGBA")

    # Calculate the position to center the watermark
    watermark_position = (
        (image.width - watermark.width) // 2,
        (image.height - watermark.height) // 2
    )

    # Create a transparent mask based on the watermark's alpha channel
    transparency=64
    mask = watermark.split()[3].point(lambda i: i * transparency / 255.)

    # Paste the watermark onto the image using the mask
    image.paste(watermark, watermark_position, mask)

    return image


def draw_status_icon(draw, chance_of_playing, position, text_font):
    """ Draw status icon based on player's chance of playing """
    icon_size = (20, 20)  # Adjust as needed

    if chance_of_playing == 100:
        color = 'green'
    elif chance_of_playing >= 25:
        color = 'orange'
    else:
        color = 'red'

    # Create an image for the status icon
    draw.ellipse([position, (position[0] + icon_size[0], position[1] +
                             icon_size[1])], fill=color)

    # Draw text inside the ellipse with the specified text size
    bold_text_font = ImageFont.truetype(text_font.path, size=10,
                                        encoding="unic")
    text_position = (position[0] + 11, position[1] + 11)  # Adjust as needed
    draw.text(text_position, str(chance_of_playing), anchor='mm',
              fill="black", font=bold_text_font)


def get_header_font(project_root, properties):
    """ Get and set the header text size and font """

    header_font_size = 18
    header_font_path = os.path.join(project_root, 'fpl',
                                    properties.header_font)
    return ImageFont.truetype(header_font_path, header_font_size)


def get_text_font(project_root, properties):
    """ Get and set the text size and font """

    text_font_size = 16
    text_font_path = os.path.join(project_root, 'fpl', properties.text_font)
    return ImageFont.truetype(text_font_path, text_font_size)


def upload_media(api, file_path):
    """ Send the image to Twitter """

    try:
        # Upload media (image) and get the media_id
        media = api.media_upload(file_path)
        return media.media_id
    except tweepy.errors.TweepyException as exc:
        raise ValueError(f"Error uploading media: {exc}")


def create_tweet(client, text, media_ids, in_reply_to_media_id):
    """ Update the tweet with hashtags """

    try:
        # Create tweet with optional media
        tweet = client.create_tweet(text=text, media_ids=media_ids,
                                    in_reply_to_tweet_id=in_reply_to_media_id)
        return tweet
    except tweepy.errors.TweepyException as exc:
        raise ValueError(f"Error creating tweet: {exc}")


def previous_prediction(project_root, properties, api, client):
    event = get_last_gameweek()
    predictions = (PlayerPrediction.objects.filter
                   (gameweek_id=event.id, player__chance_of_playing_next_round__gt=0).
                   order_by('-prediction'))[:10]
    in_reply_to_media_id = (Tweet.objects.filter(gameweek=event.id).
                            values_list('predictions_media_id', flat=True).first())

    # Create a new image with a white background
    width, height = 470, 400  # Set your desired image dimensions
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    header_font = get_header_font(project_root, properties)
    text_font = get_text_font(project_root, properties)

    draw_headers(draw, event, header_font)
    draw_predictions(draw, event, predictions, text_font)
    add_watermark(project_root, properties, image)

    save_and_tweet(api, client, image, project_root, properties, event,
                   in_reply_to_media_id)


def new_prediction(project_root, properties, api, client):
    event = get_next_gameweek()
    predictions = (PlayerPrediction.objects.filter
                   (gameweek_id=event.id, player__chance_of_playing_next_round__gt=0).
                   order_by('-prediction'))[:10]

    # Create a new image with a white background
    width, height = 395, 400  # Set your desired image dimensions
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    header_font = get_header_font(project_root, properties)
    text_font = get_text_font(project_root, properties)

    draw_headers(draw, event, header_font)
    draw_predictions(draw, event, predictions, text_font)
    add_watermark(project_root, properties, image)

    save_and_tweet(api, client, image, project_root, properties, event,
                   in_reply_to_media_id=None)


def main():
    """ Main function. Authenticate to Twitter, get predictions, generate
    an image and send the tweet
    """

    # Get the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    properties = get_properties()

    load_dotenv(os.path.join(project_root, 'fpl', 'twitter_config.env'))
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

    if None in (API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
        logger.info("Error: One or more Twitter API keys are missing.")
        sys.exit(1)

    client = tweepy.Client(consumer_key=API_KEY,
                           consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN,
                           access_token_secret=ACCESS_TOKEN_SECRET)
    auth = tweepy.OAuth1UserHandler(
        API_KEY,
        API_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET
    )

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Update the previous gameweek tweet with the actuals
    previous_prediction(project_root, properties, api, client)
    new_prediction(project_root, properties, api, client)


def save_and_tweet(api, client, image, project_root, properties, event,
                   in_reply_to_media_id):
    """ Save the image and send the tweet """

    # Get the predictions images directory path from the config
    predictions_images_path = os.path.join(project_root,
                                           properties.predictions_images)

    # Create the full path including the project root
    image_path = os.path.join(predictions_images_path,
                              f"gameweek_{event.id}.png")

    # Ensure the directory structure exists
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image.save(image_path)

    # If you want to get the image bytes (useful for Tweepy)
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    try:
        # Upload media (image) and get the media_id
        media_id = upload_media(api, image_path)
        tweet = create_tweet(client, properties.hashtags + f" #GW{event.id}",
                     [media_id], in_reply_to_media_id)
        Tweet.objects.update_or_create(gameweek=event.id,
                                       defaults={
                                        'predictions_media_id': in_reply_to_media_id if in_reply_to_media_id is not None else tweet.data['id'],
                                        'actuals_media_id': tweet.data['id'] if in_reply_to_media_id is not None else None,
                                        'updated': timezone.now()})
        logger.info(f"Tweeted for Gameweek {event.id}")

    except ValueError as ve:
        logger.info(f"Error: {ve}")


if __name__ == "__main__":
    main()
