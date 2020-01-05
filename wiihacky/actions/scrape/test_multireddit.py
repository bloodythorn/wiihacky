def test_multireddit(wh):
    wh.log.info('-- Multireddit Test -')
    try:
        from wiihacky.actions.scrape import ScrapeMultireddit
        multi = wh.reddit.multireddit(redditor='bloodythorn', name='dev')
        ac = ScrapeMultireddit(wh.log, multi)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeMultireddit failed!', e)
        assert False
