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

# Enable nested async loops. This must happen before importing asyncio.
import nest_asyncio
nest_asyncio.apply()

import asyncio
import os
import random

from AsyncRpanCommentStreamer import RpanComment, AsyncRpanCommentStreamer
from discord.ext import commands
from dotenv import load_dotenv

# Load Discord token from the .env file.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# TODO The next three variables are SHARED by a single instance of the bot!
# TODO That means each instance of the bot should run in only one server at a time!
# TODO Replace these with threadsafe dictionaries keyed on server/channel to make it scalable.

# Username filter toggle. Turning off means ALL comments on the RPAN stream will be echoed.
username_filter_active = True
# List of usernames whose comments should be echoed when the filter is on.
username_monitoring_list = [ ]
# Reference to the async task that reads RPAN comments, so that it can be stopped.
task_handle = None

bot = commands.Bot(command_prefix='!rcs ')

@bot.command(name='add_username', help='Adds a username to the monitoring list.')
async def add_username(ctx, username):
    # Strip leading u/ if provided.
    if username.startswith('u/'):
        username = username[2:]
    if username in username_monitoring_list:
        response = f'u/{username} was already in the monitoring list.'
    else:
        username_monitoring_list.append(username)
        response = f'Added u/{username} to the monitoring list.'
    await ctx.send(response)

@bot.command(name='remove_username', help='Removes a username from the monitoring list.')
async def remove_username(ctx, username):
    # Strip leading u/ if provided.
    if username.startswith('u/'):
        username = username[2:]
    if username in username_monitoring_list:
        username_monitoring_list.remove(username)
        response = f'Removed u/{username} from the monitoring list.'
    else:
        response = f'u/{username} was not found in the monitoring list.'
    await ctx.send(response)

@bot.command(name='list_usernames', help='Prints all usernames in the monitoring list.')
async def list_usernames(ctx):
    response = 'Corrently monitoring comments by these users:'
    for username in username_monitoring_list:
        response += f'\n • u/{username}'
    await ctx.send(response)

@bot.command(name='toggle_username_filter', help='Switches username filtering on/off.')
async def toggle_username_filter(ctx):
    global username_filter_active
    username_filter_active = not username_filter_active
    if username_filter_active:
        response = 'Enabled username filter (was disabled).'   
    else:
        response = 'Disabled username filter (was enabled).' 
    await ctx.send(response)

@bot.command(name='start', help='Starts monitoring the indicated stream.')
async def start(ctx, stream_id):
    global task_handle
    if len(stream_id) != 6:
        await ctx.send('Invalid stream ID (must be exactly six characters).')
    elif task_handle is not None:
        await ctx.send('Bot is already started - please stop it first :)')
    else:
        stream = AsyncRpanCommentStreamer(stream_id)

        # This is the method that is called on each new comment to echo it in your channel.
        # You can change this method to do whatever you like.
        async def message_handler(comment: RpanComment):
            if not username_filter_active or comment.author in username_monitoring_list:
                await ctx.send(comment.author + ': ' + comment.body)

        # This is the method called by AsyncRpanCommentStreamer to print log messages.
        # As written, they are also echoed in the channel. You can have it print somewhere else if you like.
        async def log_method(log_message):
            await ctx.send(log_message)

        # Start a new task to continuously stream comments from the RPAN feed.
        task_handle = asyncio.ensure_future(stream.consume(message_handler=message_handler, log_method=log_method))
        asyncio.get_event_loop().run_until_complete(task_handle)

@bot.command(name='stop', help='Stops any monitoring.')
async def stop(ctx):
    global task_handle
    await ctx.send('Stopping...')
    if task_handle is None:
        await ctx.send('Bot is already stopped - try starting it first :)')
    else:
        task_handle.cancel()
        task_handle = None
        await ctx.send('RPAN monitoring stopped.')

bot.run(TOKEN)
