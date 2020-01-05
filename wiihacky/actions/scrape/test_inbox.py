def test_inbox(wh):
    wh.log.info('-- Inbox Test -')
    try:
        from wiihacky.actions.scrape import ScrapeInbox
        ac = ScrapeInbox(wh.log, wh.reddit.inbox)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeInbox failed!:', e)
        assert False
