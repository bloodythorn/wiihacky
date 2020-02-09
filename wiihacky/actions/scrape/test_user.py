def test_user(wh):
    wh.log.info('-- User Test -')
    try:
        from wiihacky.actions.scrape import ScrapeUser
        ac = ScrapeUser(wh.log)
        ac.execute(wh.reddit)
    except Exception as e:
        wh.log.error('TEST**** ScrapeUser failed!', e)
        assert False
