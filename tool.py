# Thesis Annotation Tool
# version 0.1
# by Robin van der Noord, s3745686
# Python 3.8 or better

import sys
import csv
import re

ENCODING = 'UTF-8'


class Tool:
    def __init__(self, args):
        if not args:
            print('Please specify a file', file=sys.stderr)
            exit(1)
        self.file = args[0]
        self.sep = args[1] if len(args) > 1 else '\t'
        self.out = args[2] if len(args) > 2 else self.file

        self.history = {}  # <- to fill in duplicates
        self.todo = []  # <- no level yet

        username_re = re.compile(r'@(\w){1,15}')
        url_re = re.compile(r'https?://t.co/\w+')

        with open(self.file, encoding=ENCODING) as f:
            reader = csv.DictReader(f, delimiter=self.sep)

            # build history of scores:
            for line in reader:
                line['stripped'] = re.sub(url_re, 'http://_', re.sub(username_re, '@_', line['text']))
                if line.get('level') and not self.history.get(line['stripped']):
                    self.history[line['stripped']] = line['level']
                self.todo.append(line)

    def save(self):
        print('saving')

        with open(self.out, 'w', newline='', encoding=ENCODING) as csvfile:
            fieldnames = ['id', 'text', 'level']
            writer = csv.DictWriter(csvfile,
                                    fieldnames=fieldnames,
                                    delimiter=self.sep,
                                    extrasaction='ignore'  # <- ignore 'stripped'
                                    )
            writer.writeheader()
            writer.writerows(self.todo)
        print('done!')
        exit()

    def main(self):
        for (index, tweet) in enumerate(self.todo):
            try:
                self.annotate_tweet(index, tweet)
            except Exception as e:
                print('### Err:')
                print(e)
                print(index, tweet)
                self.save()

        # all done!
        self.save()

    def annotate_tweet(self, index, tweet):
        print(f"{index}/{len(self.todo)}")
        print(tweet['text'])
        if tweet.get('level'):
            # already done!
            print(f"!! Already filled in with {tweet['level']}")
            pass  # continue
        elif hist := self.history.get(tweet['stripped']):
            tweet['level'] = hist  # hist stored the level
            print(f"!! Seen before with {hist}")
        else:

            while True:  # no worries, it has an exit condition (2 even)
                inp = input('1-7? 0 to save; ')
                if not inp.isdigit() or int(inp) > 7:
                    continue
                choice = int(inp)
                if not choice:
                    # save and exit
                    self.save()
                tweet['level'] = choice
                break
            self.history[tweet['stripped']] = tweet


if __name__ == '__main__':
    t = Tool(sys.argv[1:])
    t.main()
    # usage: python tool.py <input file> [delimiter] [output file]
