import wiihacky
import random

if __name__ == "__main__":
    wh = wiihacky.WiiHacky()
    subreddit = wh.reddit.subreddit('wiihacks')
    comment = random.choice(list(subreddit.comments()))
    ac = wiihacky.actions.ScrapeComment(wh.log, comment)
