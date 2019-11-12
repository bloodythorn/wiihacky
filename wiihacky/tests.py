import yaml as yl

import scrape
import data
import wiihacky


def scrape_comment(wh: wiihacky.WiiHacky):
    sc = scrape.comment(wh.reddit.comment('f25ltu2'))
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_inbox(wh: wiihacky.WiiHacky):
    sc = scrape.inbox(wh.reddit.inbox)
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_message(wh: wiihacky.WiiHacky):
    sc = scrape.message(wh.reddit.inbox.message('j901cu'))
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_multireddit(wh: wiihacky.WiiHacky):
    sc = scrape.multireddit(
        wh.reddit.multireddit(redditor='bloodythorn', name='dev'))
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_redditor(wh: wiihacky.WiiHacky):
    sc = scrape.redditor(wh.reddit.redditor('bloodythorn'))
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_submission(wh: wiihacky.WiiHacky):
    sc = scrape.submission(wh.reddit.submission('dknfgw'))
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_subreddit(wh: wiihacky.WiiHacky):
    sc = scrape.subreddit(wh.reddit.subreddit('wiihacks'))
    return data.gen_filename(sc), yl.safe_dump(sc)


def scrape_user(wh: wiihacky.WiiHacky):
    sc = scrape.user(wh.reddit.user)
    return data.gen_filename(sc), yl.safe_dump(sc)


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
