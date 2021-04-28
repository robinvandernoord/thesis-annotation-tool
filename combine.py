# Thesis Annotation Comparison Tool
# version 1.0
# by Robin van der Noord, s3745686
# Python 3.8 or better
import csv
import sys
import csv


def main(files):
    lines = []
    fieldnames = ['id', 'text', 'user', 'source', 'user.description', 'split']
    for annotator_no, file in enumerate(files):
        print('loading', file, annotator_no)
        fieldnames.extend([f'explicitness-annotator-{annotator_no + 1}', f'target-annotator-{annotator_no + 1}'])
        with open(file, encoding='UTF-8') as f:
            for tweet_no, row in enumerate(csv.DictReader(f, delimiter='\t')):
                expl = row['explicitness']
                targ = row['target']
                if not annotator_no:
                    del row['explicitness']
                    del row['target']
                    row['explicitness-annotator-1'] = expl
                    row['target-annotator-1'] = targ

                    # annotator 1
                    lines.append(row)
                else:
                    line = lines[tweet_no]
                    line[f'explicitness-annotator-{annotator_no + 1}'] = expl
                    line[f'target-annotator-{annotator_no + 1}'] = targ

    print('writing')
    with open('combined.csv', 'w', newline='', encoding='UTF-8') as c:
        writer = csv.DictWriter(c,
                                fieldnames=fieldnames,
                                delimiter='\t',
                                extrasaction='ignore'
                                )
        writer.writeheader()
        writer.writerows(lines)


if __name__ == '__main__':
    main(sys.argv[1:])
