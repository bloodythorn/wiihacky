def test_comment(wh):
   wh.log.info('-- Comment Test -')
   try:
      from wiihacky.actions.scrape import ScrapeComment
      from random import choice
      comment = choice(list(wh.reddit.random_subreddit().comments()))
      wh.log.info('-- Target: {} -'.format(comment.id))
      ac = ScrapeComment(wh.log, comment)
      ac.execute()
   except Exception as e:
      wh.log.error('TEST**** ScrapeComment failed!', e)
      assert False
