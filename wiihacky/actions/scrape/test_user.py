def test_user(wh):
    wh.log.info('-- User Test -')
    try:
        from wiihacky.actions.scrape import ScrapeUser
        ac = ScrapeUser(wh.log, wh.reddit.user)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeUser failed!', e)
        assert False
