def test_message(wh):
    """
    Scrapes all messages in inbox, failure on exception.

    :param wh: WiiHacky instance.
    :return: None
    """
    wh.log.info('-- Message Test -')
    try:
        from wiihacky.actions.scrape import ScrapeMessage
        for msg in list(wh.reddit.inbox.messages()):
            wh.log.info('-- Target: {} -'.format(msg.id))
            ac = ScrapeMessage(wh.log, msg.id)
            ac.execute(wh)
    except Exception as e:
        wh.log.error('TEST**** ScrapeMessage failed!', e)
        assert False
