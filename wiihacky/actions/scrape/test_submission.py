def test_submission(wh):
    wh.log.info('-- Submission Test -')
    try:
        from wiihacky.actions.scrape import ScrapeSubmission
        submission = wh.reddit.random_subreddit().random()
        wh.log.info('-- Target: {} -'.format(submission.id))
        ac = ScrapeSubmission(wh.log, submission)
        ac.execute()
    except Exception as e:
        wh.log.error('TEST**** ScrapeSubmission failed!', e)
        assert False
