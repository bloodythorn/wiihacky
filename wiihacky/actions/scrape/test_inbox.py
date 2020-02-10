def test_inbox(wh):
    """
    Scrapes inbox 5 times, failure on exception.

    :param wh: WiiHacky instance.
    :return: None
    """
    wh.log.info('-- Inbox Test -')
    try:
        from wiihacky.actions.scrape import ScrapeInbox
        for a in range(5):
            ac = ScrapeInbox(wh.log)
            ac.execute(wh)
    except Exception as e:
        wh.log.error('TEST**** ScrapeInbox failed!:', e)
        assert False
