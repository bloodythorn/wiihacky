def test_multireddit(wh):
    wh.log.info('-- Multireddit Test -')
    try:
        from wiihacky.actions.scrape import ScrapeMultireddit
        multis = [
            ('bloodythorn', 'dev'),
            ('bloodythorn', 'entertainment'),
            ('bloodythorn', 'gaming'),
        ]

        for a in multis:
            multi = wh.reddit.multireddit(*a)
            ac = ScrapeMultireddit(wh.log, multi)
            ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeMultireddit failed!', e)
        assert False
