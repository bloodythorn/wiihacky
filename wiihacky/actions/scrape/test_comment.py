def test_comment(wh):
    wh.log.info('-- Comment Test -')
    try:
        from wiihacky.actions.scrape import ScrapeComment
        from random import choice
        for a in range(10):
            comment = choice(list(wh.reddit.random_subreddit().comments()))
            wh.log.info('-- Target: {} -'.format(comment.id))
            ac = ScrapeComment(wh.log, comment.id)
            ac.execute(wh.reddit)
    except Exception as e:
        wh.log.error('TEST**** ScrapeComment failed!', e)
        assert False
