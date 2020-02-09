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
            ac = ScrapeMultireddit(wh.log, *a)
            ac.execute(wh.reddit)
    except Exception as e:
        wh.log.error('TEST**** ScrapeMultireddit failed!', e)
        assert False
