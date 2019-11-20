import wiihacky
# import random

if __name__ == "__main__":
    wh = wiihacky.WiiHacky()
    # subreddit = wh.reddit.subreddit('wiihacks')
    # comment = random.choice(list(subreddit.comments()))
    # message = random.choice(list(wh.reddit.inbox.messages()))
    # redditor = wh.reddit.redditor('bloodythorn')
    # submission = random.choice(list(redditor.submissions.new()))
    # subreddit = wh.reddit.subreddit('wiihacks')
    multi = wh.reddit.multireddit(redditor='bloodythorn', name='dev')
    ac = wiihacky.actions.ScrapeMultireddit(wh.log, multi)
