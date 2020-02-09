def test_message(wh):
    wh.log.info('-- Message Test -')
    try:
        from wiihacky.actions.scrape import ScrapeMessage
        from random import choice
        for msg in list(wh.reddit.inbox.messages()):
            wh.log.info('-- Target: {} -'.format(msg.id))
            ac = ScrapeMessage(wh.log, msg.id)
            ac.execute(wh.reddit)
    except Exception as e:
        wh.log.error('TEST**** ScrapeMessage failed!', e)
        assert False
