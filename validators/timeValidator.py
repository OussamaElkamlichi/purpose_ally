import re
def is_valid_24_hour_time(timeIp):
    time_text = timeIp.strip()
    # Regular expression to match 24-hour time format (HH:MM)
    pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    if re.match(pattern, time_text):
        return True
    return False

# def get_user_timezone(update, context):
#     if update.message.location:
#         latitude = update.message.location.latitude
#         longitude = update.message.location.longitude

#         # Determine timezone
#         tf = TimezoneFinder()
#         timezone = tf.timezone_at(lat=latitude, lng=longitude)
#         update.message.reply_text(f"Your timezone appears to be: {timezone}")
#     else:
#         update.message.reply_text("Please share your location to determine your timezone.")