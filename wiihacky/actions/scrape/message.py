import logging as lg

from praw.models import Message

from actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeMessage(Action):
    """This action when given a comment will scrape and save the data."""

    def __init__(self, log: lg.Logger, msg: Message):
        """Initialize the action."""
        Action.__init__(self, log)
        self.msg = msg
        self.TXT_MESSAGE = self.msg.__class__.__name__

    def execute(self):
        """Execute action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_MESSAGE
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
                const.TXT_SAVING.format(self.TXT_MESSAGE.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                data[const.TXT_ID] + '-' + \
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
                self.log, const.TXT_SAVING.format(self.TXT_MESSAGE), e)
        # End of Action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape a message.

        This function will scrape a message and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.
        """
        scrape.fetch(self.msg)
        output = dict(vars(self.msg))
        scrape.prep_dict(output, self.msg.__class__.__name__)
        output[const.TXT_REPLIES] = [a.id for a in output[const.TXT_REPLIES]]
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        output[const.TXT_DEST] = output[const.TXT_DEST].name
        return scrape.strip_all(output)
