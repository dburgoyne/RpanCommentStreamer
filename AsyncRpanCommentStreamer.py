#!/usr/bin/python

# This file is part of RpanCommentStreamer (https://github.com/dburgoyne/RpanCommentStreamer).
# Copyright (c) 2021 Danny Burgoyne.
# 
# RpanCommentStreamer is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, version 3.
#
# RpanCommentStreamer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with RpanCommentStreamer. If not, see
# <http://www.gnu.org/licenses/>.

import asyncio
import json
import requests
import websockets

# Struct to encapsulate an RPAN comment. Could just use a namedtuple too.
class RpanComment:
    def __init__(self, author, timestamp, body):
        self.author = author
        self.timestamp = timestamp
        self.body = body

class AsyncRpanCommentStreamer:
    # Initially configures the streamer to listen to a certain stream.
    def __init__(self, stream_id):     
        # Get the web socket URL from the HTTP API.
        strapi_request = requests.get(f'https://strapi.reddit.com/videos/t3_{stream_id}')
        if strapi_request.status_code != 200:
            raise ConnectionError
        self.stream_uri = strapi_request.json()['data']['post']['liveCommentsWebsocket']

    # Reads from the web socket indefinitely, and invokes message_handler on every new comment.
    async def consume(self, message_handler, log_method=print):
        async with websockets.connect(self.stream_uri) as websocket:
            await log_method(f'Connected to {self.stream_uri}')
            await log_method('--------------------------------')
            async for message in websocket:
                # Parse out the message and hand off to message_handler.
                comment_json = json.loads(message)
                if comment_json['type'] == 'new_comment':
                    payload = comment_json['payload']
                    await message_handler(RpanComment(author=payload['author'],
                                                      timestamp=payload['created_utc'],
                                                      body=payload['body']))
