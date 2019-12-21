import logging as lg

from praw.models import Multireddit

from wiihacky.actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeMultireddit(Action):
    """This action when given a subreddit will scrape and save the data."""

    def __init__(self, log: lg.Logger, multi: Multireddit):
        """Initialize the action."""
        Action.__init__(self, log)
        self.multi = multi
        self.TXT_MULTIREDDIT = self.multi.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_MULTIREDDIT
        complete = False
        data = {}
        # Scrape
        try:
            self.log.info(ac + '.')
            data = self.scrape()
        except Exception as e:
            scrape.ex_occurred(self.log, ac + ':', e)
        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(self.TXT_MULTIREDDIT.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                data[const.TXT_DISPLAY_NAME].lower() + '-' + \
                str(data[const.TXT_UTC_STAMP])
            from pathlib import Path
            pth = Path(const.DATA_DIR) / data[const.TXT_TYPE].lower() / fn
            # Confirm directories
            from os import makedirs
            makedirs(pth.parent, exist_ok=True)
            # Save File
            with open(pth.with_suffix(const.FILE_SUFFIX), 'w') as f:
                from yaml import safe_dump
                f.write(safe_dump(data))
            complete = True
        except Exception as e:
            scrape.ex_occurred(
                self.log, const.TXT_SAVING.format(self.TXT_MULTIREDDIT), e)
        # End of Action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape a multi reddit.

        This function will scrape the multiredit return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        scrape.fetch(self.multi)
        output = dict(vars(self.multi))
        scrape.prep_dict(output, self.multi.__class__.__name__)
        output[const.TXT_SUBREDDIT + 's'] = \
            [a.display_name for a in output[const.TXT_SUBREDDIT + 's']]
        output[const.TXT_PATH] = output[const.TXT_PATH]
        output[const.TXT_AUTHOR] = output['_' + const.TXT_AUTHOR].name
        output.update([
            (const.TXT_COMMENTS, [a.id for a in self.multi.comments()]),
            (self.multi.controversial.__name__,
             [a.id for a in self.multi.controversial()]),
            (self.multi.hot.__name__, [a.id for a in self.multi.hot()]),
            (self.multi.new.__name__, [a.id for a in self.multi.new()]),
            (self.multi.rising.__name__, [a.id for a in self.multi.rising()]),
            (self.multi.top.__name__, [a.id for a in self.multi.top()]),
        ])
        return scrape.strip_all(output)
