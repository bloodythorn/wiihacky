def test_user(wh):
    """
    This will scrape the user. Failure on exception.
    :param wh: WiiHacky instance.
    :return: None
    """
    wh.log.info('-- User Test -')
    try:
        from wiihacky.actions.scrape import ScrapeUser
        ac = ScrapeUser(wh.log)
        ac.execute(wh)
    except Exception as e:
        wh.log.error('TEST**** ScrapeUser failed!', e)
        assert False
