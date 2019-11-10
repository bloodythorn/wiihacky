import scrape
import wiihacky


def scrape_comment(wh: wiihacky.WiiHacky):
    return scrape.comment(wh.reddit.comment('f25ltu2'))


def scrape_inbox(wh: wiihacky.WiiHacky):
    return scrape.inbox(wh.reddit.inbox)


def scrape_message(wh: wiihacky.WiiHacky):
    return scrape.message(wh.reddit.inbox.message('j901cu'))


def scrape_multireddit(wh: wiihacky.WiiHacky):
    return scrape.multireddit(
        wh.reddit.multireddit(redditor='bloodythorn', name='dev'))


def scrape_redditor(wh: wiihacky.WiiHacky):
    return scrape.redditor(wh.reddit.redditor('bloodythorn'))


def scrape_submission(wh: wiihacky.WiiHacky):
    return scrape.submission(wh.reddit.submission('dknfgw'))


def scrape_subreddit(wh: wiihacky.WiiHacky):
    return scrape.subreddit(wh.reddit.subreddit('wiihacks'))


def scrape_user(wh: wiihacky.WiiHacky):
    return scrape.user(wh.reddit.user)


def test_scrape(wh: wiihacky.WiiHacky):
    sc_ib = scrape_inbox(wh)  # inbox
    sc_cm = scrape_comment(wh)  # comment
    sc_ms = scrape_message(wh)  # message
    sc_mr = scrape_multireddit(wh)  # multireddit
    sc_rd = scrape_redditor(wh)  # redditor
    sc_sm = scrape_submission(wh)  # submission
    sc_sr = scrape_subreddit(wh)  # subreddit
    sc_us = scrape_user(wh)  # user
    return sc_ib, sc_cm, sc_ms, sc_mr, sc_rd, sc_sm, sc_sr, sc_us


if __name__ == "__main__":
    wiihacky = wiihacky.WiiHacky()
    test_scrape(wiihacky)
