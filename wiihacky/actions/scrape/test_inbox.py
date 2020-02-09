def test_inbox(wh):
    wh.log.info('-- Inbox Test -')
    try:
        from wiihacky.actions.scrape import ScrapeInbox
        for a in range(5):
            ac = ScrapeInbox(wh.log)
            ac.execute(wh.reddit)
    except Exception as e:
        wh.log.error('TEST**** ScrapeInbox failed!:', e)
        assert False
