# Poster-vk-bot

## What's this???

Bot connects with a group token.

Images DMed to the bot will be saved to a local folder on the server.

When posting is initiated, saved images will be posted on the group's wall and then removed from the local folder.

## Available commands

`test` - tests if the bot is running

`ls` - get current files count in the local folder

`post` - posts a random image from the local folder

`timer N[s|m|h]` (e.g. `timer 10s`) - queues up **all** available images for posting with an N seconds (s), minutes (m), or hours (h) interval

`timer N[s|m|h] L` (e.g. `timer 5m 10`) - same as the previous command but limits (L) the total number of queued images

`end` - kills the bot
