How to configure the plugin
===========================

Get the API key from [here](https://trello.com/1/appKey/generate)
Note: The secret is *not* the token.

Get the token from
https://trello.com/1/authorize?response_type=token&scope=read,write&expiration=never&key=API_KEY_HERE

Get your board ids from
https://trello.com/1/members/me/boards?fields=name&key=API_KEY_HERE&token=TOKEN_HERE

Using the id from above grab the list id from
https://trello.com/1/boards/BOARD_ID_HERE/lists?fields=name&key=API_KEY_HERE&token=TOKEN_HERE

Notes
-----

Yes, this is horrible. The plugin interface could do with some work to make it
support oauth cleanly as well as provide board selection in a human friendly
way.

For now, IT WORKS.
