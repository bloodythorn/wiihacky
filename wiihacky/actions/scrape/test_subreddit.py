def test_subreddit(wh):
    # Subreddit
    wh.log.info('-- Subreddit Test -')
    try:
        from wiihacky.actions.scrape import ScrapeSubreddit
        subreddit = wh.reddit.random_subreddit()
        wh.log.info('-- Target: {} -'.format(subreddit.display_name))
        ac = ScrapeSubreddit(wh.log, subreddit)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeSubreddit failed!', e)
        assert False
