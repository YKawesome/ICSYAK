# ICSYAK
## About
ICSYAK is a Discord Bot that was made for ICS 6B and 6D at UCI. 
## Problem
During the 2023 Fall Quarter in ICS 6B, the staff had to leave our class's Discord server due to various reasons. As such, all communication with them was moved to the official disussion site: Ed Discussion.
However, many of the members of the server felt that its interface was difficult to navigate and did not enjoy having to use a second platform to understand the class—this was especially needed because many critical clarifications and announcements were made on Ed Discussion. Effectively, you may miss out on a lot of points by not checking Ed Discussion.
## Solution
This bot utilizes Flask to host a web server on repl.it, and uptimerobot to make HEAD requests so that the repl doesn't go to sleep (effectively keeping the bot alive 24/7, for free). Additionally, it uses the **edapi** python package, which made communication with the Ed Stem API much more convenient. From there, I made an ed.py module to hold all utility commands I might need for the bot. I then used the asynchronous tasks.loop() method for each category in the Ed Discussion, and used one of my utility methods to pull each new thread (and sort them by date). The bot checks the most recent threads with the most recent embeds in the discord channel; if none are new, nothing new is posted (preventing repeats).

The bot now can also pull replies: Reacting to an embed from the bot will create a new Discord thread on that message, and will pull all replies and send them as embeds, linking to the reply on Ed in the author field of the embed. If there are no replies, the thread will be created but a message will clarify that there are no replies. This reply feature works with both answers and comments; however, it is only one "layer" deep, as it does not support replies to replies.

Additionally, when the bot recognizes a discord message that starts with an ed post link, it "replaces" that message with an embedded ed post (similar to the ones automatically posted in ed channels); a Discord Thread is made on that message, and all replies are attached as embeds as well.
## Implementation
<img height="400" align="center" alt="Screenshot 2023-11-15 at 1 51 53 AM" src="https://github.com/YKawesome/ICSYAK/assets/72176181/b3a86909-859d-4858-8401-8603b4f23a0c"><img height="400" align="center" alt="Screenshot 2023-11-15 at 1 53 54 AM" src="https://github.com/YKawesome/ICSYAK/assets/72176181/4f9bfe3e-3688-4d27-a43c-2d662925152c">
