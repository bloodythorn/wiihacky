import random


if __name__ == "__main__":
    from wiihacky import WiiHacky
    wh = WiiHacky()

    wh.log.info('Starting Tests')

    wh.log.info('- Scrape Actions Test -')
    # User
    wh.log.info('-- User Test -')
    try:
        from wiihacky.actions.scrape import ScrapeUser
        ac = ScrapeUser(wh.log, wh.reddit.user)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeUser failed!', e)

    # Inbox
    wh.log.info('-- Inbox Test -')
    try:
        from wiihacky.actions.scrape import ScrapeInbox
        ac = ScrapeInbox(wh.log, wh.reddit.inbox)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeInbox failed!:', e)

    # Message
    wh.log.info('-- Message Test -')
    try:
        from wiihacky.actions.scrape import ScrapeMessage
        msg = random.choice(list(wh.reddit.inbox.messages()))
        wh.log.info('-- Target: {} -'.format(msg.id))
        ac = ScrapeMessage(wh.log, msg)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeMessage failed!', e)

    # Redditor
    wh.log.info('-- Redditor Test -')
    try:
        from wiihacky.actions.scrape import ScrapeRedditor
        pops = list(wh.reddit.redditors.popular())
        redditor = wh.reddit.redditor(random.choice(pops).display_name[2:])
        wh.log.info('-- Target: {} -'.format(redditor.name))
        ac = ScrapeRedditor(wh.log, redditor)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeRedditor failed!', e)

    # Multireddit
    wh.log.info('-- Multireddit Test -')
    try:
        from wiihacky.actions.scrape import ScrapeMultireddit
        multi = wh.reddit.multireddit(redditor='bloodythorn', name='dev')
        ac = ScrapeMultireddit(wh.log, multi)
    except Exception as e:
        wh.log.error('TEST**** ScrapeMultireddit failed!', e)

    # Subreddit
    wh.log.info('-- Subreddit Test -')
    try:
        from wiihacky.actions.scrape import ScrapeSubreddit
        subreddit = wh.reddit.random_subreddit()
        wh.log.info('-- Target: {} -'.format(subreddit.display_name))
        ac = ScrapeSubreddit(wh.log, subreddit)
    except Exception as e:
        wh.log.error('TEST**** ScrapeSubreddit failed!', e)

    # Submission
    wh.log.info('-- Submission Test -')
    try:
        from wiihacky.actions.scrape import ScrapeSubmission
        submission = wh.reddit.random_subreddit().random()
        wh.log.info('-- Target: {} -'.format(submission.id))
        ac = ScrapeSubmission(wh.log, submission)
    except Exception as e:
        wh.log.error('TEST**** ScrapeSubmission failed!', e)

    # Comment
    wh.log.info('-- Comment Test -')
    try:
        from wiihacky.actions.scrape import ScrapeComment
        comment = \
            random.choice(list(wh.reddit.random_subreddit().comments()))
        wh.log.info('-- Target: {} -'.format(comment.id))
        ac = ScrapeComment(wh.log, comment)
    except Exception as e:
        wh.log.error('TEST**** ScrapeComment failed!', e)
