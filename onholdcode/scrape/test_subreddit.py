def test_subreddit(wh):
    """
    Scrape 10 random subreddits. Failure on exception.
    :param wh:
    :return:
    """
    wh.log.info('-- Subreddit Test -')
    try:
        from wiihacky.actions.scrape import ScrapeSubreddit
        for a in range(10):
            subreddit = wh.reddit.random_subreddit()
            wh.log.info('-- Target: {} -'.format(subreddit.display_name))
            ac = ScrapeSubreddit(wh.log, subreddit.display_name)
            ac.execute(wh)
    except Exception as e:
        wh.log.error('TEST**** ScrapeSubreddit failed!', e)
        assert False
