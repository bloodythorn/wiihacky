def test_redditor(wh):
    # Redditor
    wh.log.info('-- Redditor Test -')
    try:
        from wiihacky.actions.scrape import ScrapeRedditor
        pops = list(wh.reddit.redditors.popular())
        from random import choice
        redditor = wh.reddit.redditor(choice(pops).display_name[2:])
        wh.log.info('-- Target: {} -'.format(redditor.name))
        ac = ScrapeRedditor(wh.log, redditor)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeRedditor failed!', e)
        assert False
