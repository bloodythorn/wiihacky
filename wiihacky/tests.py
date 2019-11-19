import wiihacky
import random

if __name__ == "__main__":
    wh = wiihacky.WiiHacky()
    # subreddit = wh.reddit.subreddit('wiihacks')
    # comment = random.choice(list(subreddit.comments()))
    # message = random.choice(list(wh.reddit.inbox.messages()))
    redditor = wh.reddit.redditor('bloodythorn')
    ac = wiihacky.actions.ScrapeRedditor(wh.log, redditor)
