# -*- coding: utf-8 -*-
import json

import requests
from datetime import timedelta, datetime
from time import sleep
from DictObject import DictObject

from luckydonaldUtils.encoding import to_native as n
from luckydonaldUtils.encoding import text_type as unicode_type
from luckydonaldUtils.logger import logging

from .api_types import as_array
from .api_types.sendable import InputFile, Sendable
from .api_types.sendable.inline import InlineQueryResult
from .api_types.sendable.reply_markup import ForceReply
from .api_types.sendable.reply_markup import InlineKeyboardMarkup
from .api_types.sendable.reply_markup import ReplyKeyboardHide
from .api_types.sendable.reply_markup import ReplyKeyboardMarkup


__author__ = 'luckydonald'
__all__ = ["Bot"]

logger = logging.getLogger(__name__)


class Bot(object):
    _base_url = "https://api.telegram.org/bot{api_key}/{command}"  # do not chance.

    def __init__(self, api_key):
        if api_key is None:
            raise ValueError("No api_key given.")
        self.api_key = api_key
        self._last_update = datetime.now()

    def get_me(self):
        """
        A simple method for testing your bot's auth token. Requires no parameters.

        :return: Returns basic information about the bot in form of a User object.
        :rtype: User
        """
        return self.do("getMe")

    def get_updates(self, offset=None, limit=100, timeout=0, delta=timedelta(milliseconds=100), error_as_empty=True):
        """
        Use this method to receive incoming updates using long polling. An Array of Update objects is returned.

        You can choose to set `error_as_empty` to `True` or `False`.
        If `error_as_empty` is set to `True`, it will log that exception as warning, and fake an empty result,
        intended for use in for loops. In case of such error (and only in such case) it contains an "exception" field.
        Ìt will look like this: `{"result": [], "exception": e}`
        This is useful if you want to use a for loop, but ignore Network related burps.

        If `error_as_empty` is set to `False` however, all `requests.RequestException` exceptions are normally raised.

        :keyword offset: (Optional)	Identifier of the first update to be returned.
                 Must be greater by one than the highest among the identifiers of previously received updates.
                 By default, updates starting with the earliest unconfirmed update are returned.
                 An update is considered confirmed as soon as `get_updates` is called with
                 an offset higher than its `update_id`.
        :type offset: int

        :keyword limit: Limits the number of updates to be retrieved. Values between 1—100 are accepted. Defaults to 100
        :type    limit: int

        :keyword timeout: Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling
        :type    timeout: int

        :keyword delta: Wait minimal 'delta' seconds, between requests. Useful in a loop.
        :type    delta: datetime.

        :keyword error_as_empty: If errors which subclasses `requests.RequestException` will be logged but not raised.
                 Instead the returned DictObject will contain an "exception" field containing the exception occured,
                 the "result" field will be an empty list `[]`. Defaults to `False`.
        :type error_as_empty: bool


        Returns:

        :return: An Array of Update objects is returned,
                 or an empty array if there was an requests.RequestException and error_as_empty is set to True.
        :rtype: list of Update
        """
        now = datetime.now()
        if self._last_update - now < delta:
            wait = ((now - self._last_update) - delta).total_seconds()  # can be 0.2
            wait = 0 if wait < 0 else wait
            sleep(wait)
        self._last_update = datetime.now()
        try:
            return self.do("getUpdates", offset=offset, limit=limit, timeout=timeout)
        except requests.RequestException as e:
            if error_as_empty:
                logger.warn("Network related error happened in get_updates(), but will be ignored: " + str(e),
                            exc_info=True)
                self._last_update = datetime.now()
                return DictObject(result=[], exception=e)
            else:
                raise
    # end def get_updates

    def set_webhook(self, url=None, certificate=None):
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, we will send an HTTPS POST request to the specified url,
        containing a JSON-serialized Update.
        In case of an unsuccessful request, we will give up after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook request comes from Telegram,
        we recommend using a secret path in the URL, e.g. https://www.example.com/<token>.
        Since nobody else knows your bot‘s token, you can be pretty sure it’s us.

        Notes:

        1. You will not be able to receive updates using getUpdates for as long as an outgoing webhook is set up.
        2. To use a self-signed certificate, you need to upload your public key certificate using certificate parameter.
           Please upload as pytg.api_types.files.InputFile, sending a String will not work.
        3. Ports currently supported for Webhooks: 443, 80, 88, 8443.

        All types used in the Bot API responses are represented as JSON-objects.
        It is safe to use 32-bit signed integers for storing all Integer fields unless otherwise noted.

        Optional fields may be not returned when irrelevant.

        https://core.telegram.org/bots/api#setwebhook


        Optional keyword parameters:

        :keyword url: HTTPS url to send updates to. Use an empty string to remove webhook integration
        :type    url: str

        :keyword certificate: Upload your public key certificate so that the root certificate in use can be checked.
                              See our self-signed guide for details.
        :type    certificate: pytg.api_types.files.InputFile


        Returns:

        :return: True if did work.
        :rtype:  bool
        """
        assert(url is None or isinstance(url, unicode_type))  # unicode on python 2, str on python 3
        assert(certificate is None or isinstance(certificate, InputFile))
        return self.do("setWebhook", url=url, certificate=certificate)
    # end def set_webhook

    def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=False, disable_notification=False,
                     reply_to_message_id=None, reply_markup=None):
        """
        Use this method to send text messages. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#sendmessage


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel
                        (in the format @channelusername)
        :type  chat_id: int | str

        :param text: Text of the message to be sent
        :type  text: str


        Optional keyword parameters:

        :keyword parse_mode: Send "Markdown" or "HTML", if you want Telegram apps to show bold, italic,
                             fixed-width text or inline URLs in your bot's message.
        :type    parse_mode: str

        :keyword disable_web_page_preview: Disables link previews for links in this message
        :type    disable_web_page_preview: bool

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(text is not None)
        assert(isinstance(text, unicode_type))  # unicode on python 2, str on python 3
        assert(parse_mode is None or isinstance(parse_mode, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_web_page_preview is None or isinstance(disable_web_page_preview, bool))
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
            InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
        )))
        return self.do("sendMessage", chat_id=chat_id, text=text, parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)
    # end def send_message
    send_msg = send_message  # alias to send_message(...)

    def forward_message(self, chat_id, from_chat_id, message_id, disable_notification=False):
        """
        Use this method to forward messages of any kind. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#forwardmessage

        Parameters:

        :param chat_id: Unique identifier for the target chat (chat id of user chat or group chat) or username of the
                        target channel (in the format @channelusername)
        :type  chat_id: int | str

        :param from_chat_id: Unique identifier for the chat where the original message was sent
                             (id for chats or the channel's username in the format @channelusername)
        :type  from_chat_id: int | str

        :param message_id: Unique message identifier to forward
        :type  message_id: int


        Optional keyword parameters:

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(from_chat_id is not None)
        assert(isinstance(from_chat_id, (int, str)))
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(message_id is not None)
        assert(isinstance(message_id, int))
        return self.do(
            "forwardMessage", chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id,
            disable_notification=disable_notification
        )
    # end def forward_message

    def _do_fileupload(self, file_param_name, value, **kwargs):
        if isinstance(value, str):
            kwargs[file_param_name] = str(value)
        elif isinstance(value, unicode_type):
            kwargs[file_param_name] = n(value)
        elif isinstance(value, InputFile):
            kwargs["files"] = value.get_request_files(file_param_name)
        else:
            raise TypeError("Parameter {key} is not type (str, {text_type}, {input_file_type}), but type {type}".format(
                key=file_param_name, type=type(value), input_file_type=InputFile, text_type=unicode_type))
        return self.do("send{cmd}".format(cmd=file_param_name.capitalize()), **kwargs)

    def send_photo(self, chat_id, photo, caption=None, disable_notification=False, reply_to_message_id=None,
                   reply_markup=None):
        """
        Use this method to send photos. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#sendphoto


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                        @channelusername)
        :type  chat_id: `int` or `str`

        :param photo: Photo to send. You can either pass a file_id as String to resend a photo
                      file that is already on the Telegram servers, or upload a new photo,
                      specifying the file path as :class:`InputFile <pytgbot/pytgbot.api_types.files.InputFile>`.
        :type  photo: :class:`InputFile` | str


        Optional keyword parameters:

        :keyword caption: Photo caption (may also be used when resending photos by file_id), 0-200 characters
        :type    caption: str

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(photo is not None)
        assert(isinstance(photo, (InputFile, str)))
        assert(caption is None or isinstance(caption, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
            InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
        )))
        return self._do_fileupload(
            "photo", photo, chat_id=chat_id, caption=caption, disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, reply_markup=reply_markup
        )
    # end def send_photo

    def send_audio(self, chat_id, audio, duration=None, performer=None, title=None, disable_notification=False,
                   reply_to_message_id=None, reply_markup=None):
        """
        Use this method to send audio files, if you want Telegram clients to display them in the music player.
        Your audio must be in the .mp3 format. Bots can currently send audio files of up to 50 MB in size,
        this limit may be changed in the future.

        For sending voice messages, use the sendVoice method instead.

        https://core.telegram.org/bots/api#sendaudio


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                        @channelusername)
        :type  chat_id: int | str

        :param audio: Audio file to send. You can either pass a file_id as String to resend a audio
                      file that is alreadyon the Telegram servers, or upload the new audio,
                      specifying the file path as pytg.api_types.files.InputFile.
        :type  audio: pytg.api_types.files.InputFile | str


        Optional keyword parameters:

        :keyword duration: Duration of the audio in seconds
        :type    duration: int

        :keyword performer: Performer
        :type    performer: str

        :keyword title: Track name
        :type    title: str

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(audio is not None)
        assert(isinstance(audio, (InputFile, str)))
        assert(duration is None or isinstance(duration, int))
        assert(performer is None or isinstance(performer, unicode_type))  # unicode on python 2, str on python 3
        assert(title is None or isinstance(title, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
            InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
        )))
        return self._do_fileupload(
            "audio", audio, chat_id=chat_id, reply_to_message_id=reply_to_message_id, duration=duration,
            performer=performer, title=title, disable_notification=disable_notification, reply_markup=reply_markup
        )
    # end def send_audio

    def send_document(self, chat_id, document, caption=None, disable_notification=False, reply_to_message_id=None,
                      reply_markup=None):
        """
        Use this method to send general files. On success, the sent Message is returned.
        Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.

        https://core.telegram.org/bots/api#senddocument


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                        @channelusername)
        :type  chat_id: int | str

        :param document: Document to send. You can either pass a file_id as String to resend a
                         file that is already on the Telegram servers, or upload the new document,
                         specifying the file path as pytg.api_types.files.InputFile.
        :type  document: pytg.api_types.files.InputFile | str


        Optional keyword parameters:

        :keyword caption: Document caption (may also be used when resending documents by file_id), 0-200 characters
        :type    caption: str

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(document is not None)
        assert(isinstance(document, (InputFile, str)))
        assert(caption is None or isinstance(caption, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
            InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
        )))
        return self._do_fileupload(
            "document", document, chat_id=chat_id, document=document, caption=caption,
            disable_notification=disable_notification, reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup
        )

    # end def send_document

    def send_sticker(self, chat_id, sticker, disable_notification=False, reply_to_message_id=None, reply_markup=None):
        """
        Use this method to send .webp stickers. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#sendsticker


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                        @channelusername)
        :type  chat_id: int | str

        :param sticker: Sticker to send. You can either pass a file_id as String to resend a
                        sticker file that is already on the Telegram servers, or upload the new sticker,
                        specifying the file path as pytg.api_types.files.InputFile.
        :type  sticker: pytg.api_types.files.InputFile | str


        Optional keyword parameters:

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(sticker is not None)
        assert(isinstance(sticker, (InputFile, str)))
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
            InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
        )))
        return self._do_fileupload(
            "sticker", sticker, chat_id=chat_id, sticker=sticker, disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, reply_markup=reply_markup
        )
    # end def send_sticker

    def send_video(self, chat_id, video, duration=None, width=None, height=None, caption=None,
                   disable_notification=False, reply_to_message_id=None, reply_markup=None):
        """
        Use this method to send video files. On success, the sent Message is returned.
        Telegram clients support mp4 videos (other formats may be sent as Document).
        Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.

        https://core.telegram.org/bots/api#sendvideo


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                        @channelusername)
        :type  chat_id: int | str

        :param video: Video to send. You can either pass a file_id as String to resend a
                      video file that is already on the Telegram servers, or upload the new video,
                      specifying the file path as pytg.api_types.files.InputFile.
        :type  video: pytg.api_types.files.InputFile | str


        Optional keyword parameters:

        :keyword duration: Duration of sent video in seconds
        :type    duration: int

        :keyword width: Video width
        :type    width: int

        :keyword height: Video height
        :type    height: int

        :keyword caption: Video caption (may also be used when resending videos by file_id), 0-200 characters
        :type    caption: str

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                        Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(video is not None)
        assert(isinstance(video, (InputFile, str)))
        assert(duration is None or isinstance(duration, int))
        assert(width is None or isinstance(width, int))
        assert(height is None or isinstance(height, int))
        assert(caption is None or isinstance(caption, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
             InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
         )))
        return self._do_fileupload(
            "video", video, chat_id=chat_id, video=video, duration=duration, width=width, height=height,
            caption=caption, disable_notification=disable_notification, reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup
        )
    # end def send_video

    def send_voice(self, chat_id, voice, duration=None, disable_notification=False, reply_to_message_id=None,
                   reply_markup=None):
        """
        Use this method to send audio files,
        if you want Telegram clients to display the file as a playable voice message.
        For this to work, your audio must be in an .ogg file encoded with OPUS (other formats may be sent as Audio or
        Document).

        On success, the sent Message is returned.
        Bots can currently send voice messages of up to 50 MB in size, this limit may be changed in the future.

        https://core.telegram.org/bots/api#sendvoice


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                         @channelusername)
        :type  chat_id: int | str

        :param voice: Audio file to send.
                      You can either pass a file_id as str to resend an audio that is already on the Telegram servers,
                      or upload a new audio file using a pytg.api_types.files.InputFile.
        :type  voice: pytg.api_types.files.InputFile | str


        Optional keyword parameters:

        :keyword duration: Duration of sent audio in seconds
        :type    duration: int

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                     Android users will receive a notification with no sound.
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(voice is not None)
        assert(isinstance(voice, (InputFile, str)))
        assert(duration is None or isinstance(duration, int))
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
             InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
         )))
        return self._do_fileupload(
            "voice", voice, chat_id=chat_id, voice=voice, duration=duration,
            disable_notification=disable_notification, reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup
        )
    # end def send_voice

    def send_location(self, chat_id, latitude, longitude, disable_notification=False, reply_to_message_id=None,
                      reply_markup=None):
        """
        Use this method to send point on the map. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#sendlocation


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                         @channelusername)
        :type  chat_id: int | str

        :param latitude: Latitude of location
        :type  latitude: float

        :param longitude: Longitude of location
        :type  longitude: float


        Optional keyword parameters:

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                       Android users will receive a notification with no sound
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(latitude is not None)
        assert(isinstance(latitude, float))
        assert(longitude is not None)
        assert(isinstance(longitude, float))
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
             InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
         )))
        return self.do("sendLocation", chat_id=chat_id, latitude=latitude, longitude=longitude,
                       disable_notification=disable_notification, reply_to_message_id=reply_to_message_id,
                       reply_markup=reply_markup)
    # end def send_location

    def send_venue(self, chat_id, latitude, longitude, title, address, foursquare_id=None, disable_notification=False,
                   reply_to_message_id=None, reply_markup=None):
        """
        Use this method to send information about a venue. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#sendvenue


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                         @channelusername)
        :type  chat_id: int | str

        :param latitude: Latitude of the venue
        :type  latitude: float

        :param longitude: Longitude of the venue
        :type  longitude: float

        :param title: Name of the venue
        :type  title: str

        :param address: Address of the venue
        :type  address: str


        Optional keyword parameters:

        :keyword foursquare_id: Foursquare identifier of the venue
        :type    foursquare_id: str

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                       Android users will receive a notification with no sound
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                                A JSON-serialized object for an inline keyboard, custom reply keyboard,
                                instructions to hide reply keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(latitude is not None)
        assert(isinstance(latitude, float))
        assert(longitude is not None)
        assert(isinstance(longitude, float))
        assert(title is not None)
        assert(isinstance(title, unicode_type))  # unicode on python 2, str on python 3
        assert(address is not None)
        assert(isinstance(address, unicode_type))  # unicode on python 2, str on python 3
        assert(foursquare_id is None or isinstance(foursquare_id, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
             InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
         )))
        return self.do("sendVenue", chat_id=chat_id, latitude=latitude, longitude=longitude, title=title,
                       address=address, foursquare_id=foursquare_id, disable_notification=disable_notification,
                       reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)

    # end def send_venue

    def send_contact(self, chat_id, phone_number, first_name, last_name=None, disable_notification=None,
                     reply_to_message_id=None, reply_markup=None):
        """
        Use this method to send phone contacts. On success, the sent Message is returned.

        https://core.telegram.org/bots/api#sendcontact


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                         @channelusername)
        :type  chat_id: int | str

        :param phone_number: Contact's phone number
        :type  phone_number: str

        :param first_name: Contact's first name
        :type  first_name: str


        Optional keyword parameters:

        :keyword last_name: Contact's last name
        :type    last_name: str

        :keyword disable_notification: Sends the message silently. iOS users will not receive a notification,
                                       Android users will receive a notification with no sound
        :type    disable_notification: bool

        :keyword reply_to_message_id: If the message is a reply, ID of the original message
        :type    reply_to_message_id: int

        :keyword reply_markup: Additional interface options.
                               A JSON-serialized object for an inline keyboard, custom reply keyboard,
                               instructions to hide keyboard or to force a reply from the user.
        :type    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardHide | ForceReply


        Returns:

        :return: On success, the sent Message is returned
        :rtype:  Message
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(phone_number is not None)
        assert(isinstance(phone_number, unicode_type))  # unicode on python 2, str on python 3
        assert(first_name is not None)
        assert(isinstance(first_name, unicode_type))  # unicode on python 2, str on python 3
        assert(last_name is None or isinstance(last_name, unicode_type))  # unicode on python 2, str on python 3
        assert(disable_notification is None or isinstance(disable_notification, bool))
        assert(reply_to_message_id is None or isinstance(reply_to_message_id, int))
        assert(reply_markup is None or isinstance(reply_markup, (
             InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply
         )))
        return self.do("sendContact", chat_id=chat_id, phone_number=phone_number,
                       first_name=first_name, last_name=last_name, disable_notification=disable_notification,
                       reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)
    # end def send_contact

    def send_chat_action(self, chat_id, action):
        """
        Use this method when you need to tell the user that something is happening on the bot's side.
        The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status).

        Example: The ImageBot needs some time to process a request and upload the image.
                 Instead of sending a text message along the lines of "Retrieving image, please wait...",
                 the bot may use sendChatAction with action = "upload_photo".
                 The user will see a "sending photo" status for the bot.

        We only recommend using this method when a response from the bot will take a noticeable amount of time to arrive

        https://core.telegram.org/bots/api#sendchataction


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target channel (in the format
                         @channelusername)
        :type  chat_id: int | str

        :param action: Type of action to broadcast. Choose one, depending on what the user is about to receive:
                        "typing" for text messages, "upload_photo" for photos,
                        "record_video" or "upload_video" for videos, "record_audio" or "upload_audio" for audio files,
                        "upload_document" for general files, "find_location" for location data.
        :type  action: str


        Returns:

        :return:
        :rtype:
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(action is not None)
        assert(isinstance(action, unicode_type))  # unicode on python 2, str on python 3
        return self.do("sendChatAction", chat_id=chat_id, action=action)
    # end def send_chat_action

    def get_file(self, file_id):
        """
        Use this method to get basic info about a file and prepare it for downloading.
        For the moment, bots can download files of up to 20MB in size.

        On success, a File object is returned.
        The file can then be downloaded via the link https://api.telegram.org/file/bot<token>/<file_path>,
        where <file_path> is taken from the response.
        It is guaranteed that the link will be valid for at least 1 hour.
        When the link expires, a new one can be requested by calling get_file again.

        https://core.telegram.org/bots/api#getfile


        Parameters:

        :param file_id: File identifier to get info about
        :type  file_id: str


        Returns:

        :return: On success, a File object is returned
        :rtype:  File
        """
        assert(file_id is not None)
        assert(isinstance(file_id, str))
        return self.do("getFile", file_id=file_id)
    # end def get_file

    def edit_message_text(self, text, chat_id=None, message_id=None, inline_message_id=None, parse_mode=None,
                          disable_web_page_preview=None, reply_markup=None):
        """
        Use this method to edit text messages sent by the bot or via the bot (for inline bots).
         On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

        https://core.telegram.org/bots/api#editmessagetext


        Parameters:

        :param text: New text of the message
        :type  text:  str


        Optional keyword parameters:

        :keyword chat_id: Required if inline_message_id is not specified. Unique identifier for the target chat or
                          username of the target channel (in the format @channelusername)
        :type    chat_id:  int | str

        :keyword message_id: Required if inline_message_id is not specified. Unique identifier of the sent message
        :type    message_id:  int

        :keyword inline_message_id: Required if chat_id and message_id are not specified.
                                    Identifier of the inline message
        :type    inline_message_id:  str

        :keyword parse_mode: Send "Markdown" or "HTML", if you want Telegram apps to show bold, italic, fixed-width text
                             or inline URLs in your bot's message.
        :type    parse_mode:  str

        :keyword disable_web_page_preview: Disables link previews for links in this message
        :type    disable_web_page_preview:  bool

        :keyword reply_markup: A JSON-serialized object for an inline keyboard.
        :type    reply_markup:  InlineKeyboardMarkup


        Returns:

        :return: On success, if edited message is sent by the bot, the edited Message is returned,
                 otherwise True is returned.
        :rtype:  Message or bool
        """
        assert (message_id is None or isinstance(message_id, int))
        assert (inline_message_id is None or isinstance(inline_message_id, str))
        assert (text is not None)
        assert (isinstance(text, str))
        assert (parse_mode is None or isinstance(parse_mode, str))
        assert (disable_web_page_preview is None or isinstance(disable_web_page_preview, bool))
        return self.do("editMessageText", text=text, chat_id=chat_id, message_id=message_id,
                       inline_message_id=inline_message_id, parse_mode=parse_mode,
                       disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup)
    # end def edit_message_text

    def edit_message_caption(self, chat_id=None, message_id=None, inline_message_id=None, caption=None,
                             reply_markup=None):
        """
        Use this method to edit captions of messages sent by the bot or via the bot (for inline bots).

        On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

        https://core.telegram.org/bots/api#editmessagecaption


        Optional keyword parameters:

        :keyword chat_id: Required if inline_message_id is not specified. Unique identifier for the target chat or
                          username of the target channel (in the format @channelusername)
        :type    chat_id:  int | str

        :keyword message_id: Required if inline_message_id is not specified. Unique identifier of the sent message
        :type    message_id:  int

        :keyword inline_message_id: Required if chat_id and message_id are not specified.
                                    Identifier of the inline message
        :type    inline_message_id:  str

        :keyword caption: New caption of the message
        :type    caption:  str

        :keyword reply_markup: A JSON-serialized object for an inline keyboard.
        :type    reply_markup:  InlineKeyboardMarkup


        Returns:

        :return: On success, if edited message is sent by the bot, the edited Message is returned,
                 otherwise True is returned.
        :rtype:  Message or bool
        """
        assert (message_id is None or isinstance(message_id, int))
        assert (inline_message_id is None or isinstance(inline_message_id, str))
        assert (caption is None or isinstance(caption, str))
        return self.do("editMessageCaption", chat_id=chat_id, message_id=message_id,
                       inline_message_id=inline_message_id, caption=caption, reply_markup=reply_markup)
    # end def edit_message_caption

    def edit_message_reply_markup(self, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        """
        Use this method to edit only the reply markup of messages sent by the bot or via the bot (for inline bots).
        On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

        https://core.telegram.org/bots/api#editmessagereplymarkup


        Optional keyword parameters:

        :keyword chat_id: Required if inline_message_id is not specified. Unique identifier for the target chat or
                          username of the target channel (in the format @channelusername)
        :type    chat_id:  int | str

        :keyword message_id: Required if inline_message_id is not specified. Unique identifier of the sent message
        :type    message_id:  int

        :keyword inline_message_id: Required if chat_id and message_id are not specified.
                                    Identifier of the inline message
        :type    inline_message_id:  str

        :keyword reply_markup: A JSON-serialized object for an inline keyboard.
        :type    reply_markup:  InlineKeyboardMarkup


        Returns:

        :return: On success, if edited message is sent by the bot, the edited Message is returned,
                 otherwise True is returned.
        :rtype:  Message or bool
        """
        assert (message_id is None or isinstance(message_id, int))
        assert (inline_message_id is None or isinstance(inline_message_id, str))
        return self.do(
            "editMessageReplyMarkup", chat_id=chat_id, message_id=message_id, inline_message_id=inline_message_id,
            reply_markup=reply_markup
        )
    # end def edit_message_reply_markup

    def kick_chat_member(self, chat_id, user_id):
        """
        Use this method to kick a user from a group or a supergroup. In the case of supergroups,
        the user will not be able to return to the group on their own using invite links, etc., unless unbanned first.

        The bot must be an administrator in the group for this to work. Returns True on success.

        Note: This will method only work if the ‘All Members Are Admins’ setting is off in the target group.
              Otherwise members may only be removed by the group's creator or by the member that added them.

        https://core.telegram.org/bots/api#kickchatmember


        Parameters:

        :param chat_id: Unique identifier for the target group or username of the target supergroup (in the format
                        @supergroupusername)
        :type  chat_id: int | str

        :param user_id: Unique identifier of the target user
        :type  user_id: int


        Returns:

        :return: Returns True on success
        :rtype:  bool
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(user_id is not None)
        assert(isinstance(user_id, int))
        return self.do("kickChatMember", chat_id=chat_id, user_id=user_id)
    # end def kick_chat_member

    def leave_chat(self, chat_id):
        """
        Use this method for your bot to leave a group, supergroup or channel. Returns True on success.

        https://core.telegram.org/bots/api#leavechat


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target supergroup or channel (in the
                        format @channelusername)
        :type  chat_id: int | str


        Returns:

        :return: Returns True on success
        :rtype:  True
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        return self.do("leaveChat", chat_id=chat_id)

    # end def leave_chat

    def unban_chat_member(self, chat_id, user_id):
        """
        Use this method to unban a previously kicked user in a supergroup.
        The user will not return to the group automatically, but will be able to join via link, etc.

        The bot must be an administrator in the group for this to work. Returns True on success.

        https://core.telegram.org/bots/api#unbanchatmember


        Parameters:

        :param chat_id: Unique identifier for the target group or username of the target supergroup (in the format
                         @supergroupusername)
        :type  chat_id: int | str

        :param user_id: Unique identifier of the target user
        :type  user_id: int


        Returns:

        :return: Returns True on success
        :rtype: bool
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(user_id is not None)
        assert(isinstance(user_id, int))
        return self.do("unbanChatMember", chat_id=chat_id, user_id=user_id)
    # end def unban_chat_member

    def get_chat(self, chat_id):
        """
        Use this method to get up to date information about the chat (current name of the user for one-on-one
        conversations, current username of a user, group or channel, etc.)

        Returns a Chat object on success.

        https://core.telegram.org/bots/api#getchat


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target supergroup or channel (in the
                        format @channelusername)
        :type  chat_id: int | str


        Returns:

        :return: Returns a Chat object on success
        :rtype:  Chat
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        return self.do("getChat", chat_id=chat_id)
    # end def get_chat

    def get_chat_administrators(self, chat_id):
        """
        Use this method to get a list of administrators in a chat.

        On success, returns an Array of ChatMember objects that contains information about all chat administrators
        except other bots. If the chat is a group or a supergroup and no administrators were appointed,
        only the creator will be returned.

        https://core.telegram.org/bots/api#getchatadministrators


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target supergroup or channel (in the\n
                        format @channelusername)
        :type  chat_id: int | str


        Returns:

        :return: On success, returns an Array of ChatMember objects that contains information about all
                 chat administrators except other bots. If the chat is a group or a supergroup and no administrators
                 were appointed, only the creator will be returned
        :rtype:  Array of ChatMember
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        return self.do("getChatAdministrators", chat_id=chat_id)
    # end def get_chat_administrators

    def get_chat_members_count(self, chat_id):
        """
        Use this method to get the number of members in a chat. Returns Int on success.

        https://core.telegram.org/bots/api#getchatmemberscount


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target supergroup or channel (in the
                         format @channelusername)
        :type  chat_id: int | str


        Returns:

        :return: Returns Int on success
        :rtype:  Int
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        return self.do("getChatMembersCount", chat_id=chat_id)
    # end def get_chat_members_count

    def get_chat_member(self, chat_id, user_id):
        """
        Use this method to get information about a member of a chat. Returns a ChatMember object on success.

        https://core.telegram.org/bots/api#getchatmember


        Parameters:

        :param chat_id: Unique identifier for the target chat or username of the target supergroup or channel (in the
                         format @channelusername)
        :type  chat_id: int | str

        :param user_id: Unique identifier of the target user
        :type  user_id: int


        Returns:

        :return: Returns a ChatMember object on success
        :rtype:  ChatMember
        """
        assert(chat_id is not None)
        assert(isinstance(chat_id, (int, str)))
        assert(user_id is not None)
        assert(isinstance(user_id, int))
        return self.do("getChatMember", chat_id=chat_id, user_id=user_id)
    # end def get_chat_member

    def answer_inline_query(self, inline_query_id, results, cache_time=None, is_personal=None, next_offset=None,
                            switch_pm_text=None, switch_pm_parameter=None):
        """
        Use this method to send answers to an inline query. On success, True is returned.
        No more than 50 results per query are allowed.

        https://core.telegram.org/bots/api#answerinlinequery


        Parameters:

        :param inline_query_id: Unique identifier for the answered query
        :type  inline_query_id: str

        :param results: A JSON-serialized array of results for the inline query
        :type  results: list of InlineQueryResult


        Optional keyword parameters:

        :keyword cache_time: The maximum amount of time in seconds that the result of the inline query may be cached on
                             the server. Defaults to 300.
        :type    cache_time: int

        :keyword is_personal: Pass True, if results may be cached on the server side only for the user that sent the
                              query. By default, results may be returned to any user who sends the same query
        :type    is_personal: bool

        :keyword next_offset: Pass the offset that a client should send in the next query with the same text to receive
                              more results. Pass an empty string if there are no more results or if you don‘t support
                              pagination. Offset length can’t exceed 64 bytes.
        :type    next_offset: str

        :keyword switch_pm_text: If passed, clients will display a button with specified text that switches
                                 the user to a private chat with the bot and sends the bot a start message with the
                                 parameter switch_pm_parameter
        :type    switch_pm_text: str

        :keyword switch_pm_parameter: Parameter for the start message sent to the bot when user presses
                                      the switch button
                                         Example:
                                            An inline bot that sends YouTube videos can ask the user to connect the
                                            bot to their YouTube account to adapt search results accordingly.
                                            To do this, it displays a "Connect your YouTube account" button above the
                                            results, or even before showing any.
                                            The user presses the button, switches to a private chat with the bot and,
                                            in doing so, passes a start parameter that instructs the bot to return an
                                            oauth link.
                                            Once done, the bot can offer a switch_inline button so that
                                            the user can easily return to the chat where they wanted to use the bot's
                                            inline capabilities.
        :type    switch_pm_parameter: str


        Returns:

        :return: On success, True is returned
        :rtype: bool
        """
        assert(inline_query_id is not None)
        if isinstance(inline_query_id, int):
            inline_query_id = str(inline_query_id)
        assert(isinstance(inline_query_id, (str, unicode_type)))
        inline_query_id = n(inline_query_id)
        assert(results is not None)
        if isinstance(results, InlineQueryResult):
            results = [results]
        assert(isinstance(results, (list, tuple)))  # list of InlineQueryResult
        result_objects = []
        for result in results:
            assert isinstance(result, InlineQueryResult)  # checks all elements of results
            result_objects.append(result.to_array())
        assert(cache_time is None or isinstance(cache_time, int))
        assert(is_personal is None or isinstance(is_personal, bool))
        if next_offset is not None:
            assert(isinstance(next_offset, (str, unicode_type, int)))
            next_offset = n(str(next_offset))
        assert(switch_pm_text is None or isinstance(switch_pm_text, unicode_type))  # py2: unicode, py3: str
        assert(switch_pm_parameter is None or isinstance(switch_pm_parameter, unicode_type))  # py2: unicode, py3: str
        return self.do(
            "answerInlineQuery", inline_query_id=inline_query_id, results=json.dumps(result_objects),
            cache_time=cache_time, is_personal=is_personal, next_offset=next_offset, switch_pm_text=switch_pm_text,
            switch_pm_parameter=switch_pm_parameter
        )
    # end def answer_inline_query

    def answer_callback_query(self, callback_query_id, text=None, show_alert=None):
        """
        Use this method to send answers to callback queries sent from inline keyboards.
        The answer will be displayed to the user as a notification at the top of the chat screen or as an alert.
        On success, True is returned.

        https://core.telegram.org/bots/api#answercallbackquery


        Parameters:

        :param callback_query_id: Unique identifier for the query to be answered
        :type  callback_query_id: str


        Optional keyword parameters:

        :keyword text: Text of the notification. If not specified, nothing will be shown to the user
        :type    text: str

        :keyword show_alert: If true, an alert will be shown by the client instead of a notification at the top of the
                             chat screen. Defaults to false.
        :type    show_alert: bool


        Returns:

        :return: On success, True is returned
        :rtype: bool
        """
        assert(callback_query_id is not None)
        assert(isinstance(callback_query_id, unicode_type))  # unicode on python 2, str on python 3
        assert(text is None or isinstance(text, unicode_type))  # unicode on python 2, str on python 3
        assert(show_alert is None or isinstance(show_alert, bool))
        return self.do("answerCallbackQuery", callback_query_id=callback_query_id, text=text, show_alert=show_alert)
    # end def answer_callback_query

    def get_user_profile_photos(self, user_id, offset=None, limit=None):
        """
        Use this method to get a list of profile pictures for a user. Returns a UserProfilePhotos object.

        https://core.telegram.org/bots/api#getuserprofilephotos


        Parameters:

        :param user_id: Unique identifier of the target user
        :type  user_id: int


        Optional keyword parameters:

        :keyword offset: Sequential number of the first photo to be returned. By default, all photos are returned.
        :type    offset: int

        :keyword limit: Limits the number of photos to be retrieved. Values between 1—100 are accepted. Defaults to 100.
        :type    limit: int


        Returns:

        :return: Returns a UserProfilePhotos object.
        :rtype:  UserProfilePhotos

        """
        assert(user_id is not None)
        assert(isinstance(user_id, int))
        assert(offset is None or isinstance(offset, int))
        assert(limit is None or isinstance(limit, int))
        return self.do("getUserProfilePhotos", user_id=user_id, offset=offset, limit=limit)
    # end def get_user_profile_photos

    def do(self, command, files=None, use_long_polling=False, **query):
        """
        Send a request to the api.

        :param command: The Url command parameter
        :param files: if it needs to send files.
        :param use_long_polling: if it should use long polling.
                                (see http://docs.python-requests.org/en/latest/api/#requests.Response.iter_content)
        :param query: will get json encoded.
        :return:
        """
        params = {}
        for key in query.keys():
            element = query[key]
            if element is not None:
                if isinstance(element, Sendable):
                    params[key] = json.dumps(as_array(element))
                else:
                    params[key] = element
        url = self._base_url.format(api_key=n(self.api_key), command=n(command))
        r = requests.post(url, params=params, files=files, stream=use_long_polling,
                          verify=True)  # No self signed certificates. Telegram should be trustworthy anyway...
        res = DictObject.objectify(r.json())
        res["response"] = r  # TODO: does this failes on json lists? Does TG does that?
        # TG should always return an dict, with at least a status or something.
        return res
    # end def do
# end class