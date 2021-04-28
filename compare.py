# Thesis Annotation Comparison Tool
# version 1.0
# by Robin van der Noord, s3745686
# Python 3.8 or better
import datetime
import sys
import csv
from collections import defaultdict, Counter
from pprint import pprint


class CompareTool:
    EXPLICITNESS = {
        'e': 'EXPLICIT',
        'i': 'IMPLICIT',
        'n': 'NOT',
    }
    TARGET = {
        'i': 'INDIVIDUAL',
        'g': 'GROUP',
        'o': 'OTHER',
        'n': 'NOT',
    }

    def __init__(self, *files):
        self.files = files
        self.tweets, self.annotations = self.load_annotations()

        self.stats_basic = defaultdict(int)
        self.stats_detail = defaultdict(int)

        # change these numbers (and todo: change logic) when using less or more files
        self.full_agree = 4
        self.majority_agree = 3

    def load_annotations(self):
        print("### Reading Files ###")
        tweets = {}
        annotations = defaultdict(list)

        for file in self.files:
            with open(file, encoding='UTF-8') as f:
                for row in csv.DictReader(f, delimiter='\t'):

                    annotations[row['id']].append({
                        'explicitness': row['explicitness'] or '',
                        'target': row['target'] or '',
                        'id': row['id'],
                        'who': file,
                    })
                    if not row['id'] in tweets:
                        del row['explicitness']
                        del row['target']
                        # store all fields except annotations
                        tweets[row['id']] = row

        print('loaded', len(tweets), len(annotations))
        return tweets, annotations

    def choose(self, annotation, goal):
        if len(annotation) < self.majority_agree:
            # not enough annotated this one -> skip
            self.stats_basic['skipped'] += 1
            return ""

        c = Counter([a[goal] for a in annotation]).most_common(2)
        label, cnt = c[0]

        self.stats_basic[f'total-{goal}'] += 1

        if cnt == self.full_agree:
            # fully agree!
            self.stats_basic[f'{goal}-agree'] += 1
            self.stats_detail[f'{goal}-agree-{label or "None"}'] += 1
        elif cnt >= self.majority_agree:
            # majority agree (3 vs 1)
            self.stats_basic[f'{goal}-3majority'] += 1
            self.stats_detail[f'{goal}-3majority-{label or "None"}'] += 1
        else:
            no2_label, no2_cnt = c[-1]

            label, no2_label = sorted([label or 'None', no2_label or 'None'])

            # perfect split (2 vs 2) or majority split ( 2 vs 1 vs 1)
            self.stats_basic[f'{goal}-split'] += 1
            self.stats_detail[f'{goal}-split-{label}+{no2_label}'] += 1
            return "?"

        return label

    def start(self):
        print("### Comparing Annotations ###")
        for _id, annotation in self.annotations.items():
            if any([a.get('explicitness') for a in annotation]):
                self.tweets[_id]['explicitness'] = self.choose(annotation, 'explicitness')
                self.tweets[_id]['target'] = self.choose(annotation, 'target')

    def analyze(self):
        print("### Data Statistics ###")
        pprint(self.stats_basic)
        pprint(self.stats_detail)

    def count_todo(self):
        return sum([1 for t in self.tweets.values() if t.get('target') == "?" or t.get('explicitness') == '?'])

    def annotate(self):
        print('### Started Manual Annotating ### ')
        todo = self.count_todo()

        index = 1
        for _id, tweet in self.tweets.items():
            explicitness = tweet.get('explicitness', '')
            target = tweet.get('target', '')

            if explicitness == "?" or target == "?":
                print(f"{index}/{todo}")
                print(tweet['text'])
                if explicitness == "NOT":
                    target = ""
                    print("! Target skipped because explicitness was NOT")
                else:
                    print('explicitness:', explicitness)
                    print('target:', target)
                    pprint(self.annotations[_id])

                    while True:
                        explicitness = (
                                input('EXPLICITNESS: [E]XPLICIT | [I]MPLICIT | [N]OT ? ') + ' '
                        )[0].lower()  # grab first letter

                        if explicitness in self.EXPLICITNESS.keys():
                            explicitness = self.EXPLICITNESS[explicitness]
                            break
                    if explicitness == 'NOT':
                        target = ''
                    else:
                        while True:
                            target = (
                                    input('TARGET: [I]NDIVIDUAL | [G]ROUP | [O]THER | [N]ONE ? ') + ' '
                            )[0].lower()
                            if target in self.TARGET.keys():
                                target = self.TARGET[target]
                                break

                tweet['target'] = target
                tweet['explicitness'] = explicitness
                index += 1

    def export(self):
        print("### Saving File ###")
        now = str(datetime.datetime.now()).replace(":", "").replace(".", "").replace(" ", "-")
        output_file = f"gold-{now}.csv"

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'text', 'user', 'source', 'user.description', 'split', 'explicitness', 'target']
            writer = csv.DictWriter(csvfile,
                                    fieldnames=fieldnames,
                                    delimiter='\t',
                                    extrasaction='ignore'  # <- ignore 'stripped'
                                    )
            writer.writeheader()
            writer.writerows(self.tweets.values())


if __name__ == '__main__':
    t = CompareTool(*sys.argv[1:])
    t.start()
    t.analyze()
    t.annotate()
    t.export()
    # usage: python3 compare.py file1.csv file2.csv [file3.csv] [file4.csv] [...]
