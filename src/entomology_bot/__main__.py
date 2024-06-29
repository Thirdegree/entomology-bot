import praw
import yaml
import logging

ACTIVE_SUBREDDIT = "thirdegree"

logging.basicConfig(level=logging.INFO)

class EntomologyBot:
    def __init__(self, reddit: praw.Reddit) -> None:
        self.reddit = reddit
        self.responses: dict[str, str] = {}

    def load_responses(self) -> None:
        wiki_page = self.reddit.subreddit(ACTIVE_SUBREDDIT).wiki["entomology-bot"].content_md
        self.responses = yaml.safe_load(wiki_page)
        logging.info("Loaded responses")

    def run(self) -> None:
        for comment in self.reddit.subreddit(ACTIVE_SUBREDDIT).stream.comments(skip_existing=True):
            try:
                self.load_responses()
            except yaml.scanner.ScannerError:
                logging.error("Failed to load yaml configuration", exc_info=True)
            for command in self.responses:
                if comment.body == command:
                    try:
                        self.handle_command(comment, command)
                    except praw.exceptions.RedditAPIException:
                        logging.error("Failed to handle comment %s", comment, exc_info=True)

    def handle_command(self, comment: praw.models.Comment, command: str) -> None:
        response = f"""{self.responses[command]}

*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/{ACTIVE_SUBREDDIT}) if you have any questions or concerns.*"""

        reply = comment.submission.reply(response)
        logging.info("Replied to submission %s in response to command in comment %s", comment.submission, comment)
        if not any(top_level.stickied for top_level in comment.submission.comments):
            reply.mod.distinguish(sticky=True)
            logging.info("Distinguished rely")


def main() -> None:
    reddit = praw.Reddit("entomology-bot")
    bot = EntomologyBot(reddit)
    try:
        bot.load_responses()
        bot.run()
    except yaml.scanner.ScannerError:
        logging.error("Failed to load config on startup -- exiting")


if __name__ == "__main__":
    main()
