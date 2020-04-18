def test_redditor(wh):
    """
    Scrapes 10 random redditors. Failure on exception.

    :param wh: WiiHacky instance.
    :return: None
    """
    wh.log.info('-- Redditor Test -')
    try:
        from wiihacky.actions.scrape import ScrapeRedditor
        pops = list(wh.reddit.redditors.popular())
        from random import choice
        for a in range(10):
            redditor = wh.reddit.redditor(choice(pops).display_name[2:])
            wh.log.info('-- Target: {} -'.format(redditor.name))
            ac = ScrapeRedditor(wh.log, redditor.name)
            ac.execute(wh)
    except Exception as e:
        wh.log.error('TEST**** ScrapeRedditor failed!', e)
        assert False
