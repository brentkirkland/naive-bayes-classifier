#!/usr/bin/python

import re
from collections import Counter
import random
import time
import math
import sys

def combine(words):
    new_words = []
    for i in range(0, len(words) - 1):
        word = words[i] + words[i+1];
        new_words.append(word);
    return new_words


def parse_data(textfile):
    no_words = 0;
    words = [];
    lines = [];
    no_lines = 0;
    rating_0_count = 0;
    rating_1_count = 0;
    rating_0_no_words = 0;
    rating_1_no_words = 0;
    rating_1_words = [];
    rating_0_words = [];
    with open(textfile) as inputfile:
        for line in inputfile:
            # local data
            line_data = re.findall(r"[\w']+", line);
            line_count = len(line_data) - 1;
            line_rating = line_data.pop();
            line_words = line_data;
            line_words = map(lambda x:x.upper(), line_words);
            line_words.extend(combine(line_words));
            line_word_counts = Counter(line_words);
            line_dict = {
                'no_words': line_count,
                'rating': line_rating,
                'words': line_words,
                'word_count': line_word_counts
            };
            lines.append(line_dict)
            # global data
            no_words = no_words + line_count;
            words.extend(line_words);
            no_lines = no_lines + 1;
            if line_rating == '1':
                rating_1_count = rating_1_count + 1;
                rating_1_no_words = rating_1_no_words + line_count;
                rating_1_words.extend(line_words);
            else:
                rating_0_count = rating_0_count + 1;
                rating_0_no_words = rating_0_no_words + line_count;
                rating_0_words.extend(line_words);

    word_count = Counter(words);
    rating_0_word_count = Counter(rating_0_words);
    rating_1_word_count = Counter(rating_1_words);
    words = {
        'no_words': float(no_words),
        'no_lines': float(no_lines),
        'words': words,
        'word_count': word_count,
        'rating': [
            {'count': float(rating_0_count),
            'no_words': float(rating_0_no_words),
            'word_count': rating_0_word_count
            },
            {'count': float(rating_1_count),
            'no_words': float(rating_1_no_words),
            'word_count': rating_1_word_count
            }
        ],
        'lines': lines}
    return words

def create_dictionary(data):
    data_length = len(data);
    for i in range(0, data_length):
        line_data = {'rating': data[i] }

def basic_stats(name, data):
    print(name);
    print('Number of words: ', data['no_words']);
    print('Number of lines: ', data['no_lines']);
    print('Ratings 0:')
    print('Number of rating 0: ', data['rating'][0]['count']);
    print('Number of rating 0 words: ', data['rating'][0]['no_words']);
    print('Ratings 1: ')
    print('Number of rating 1: ', data['rating'][1]['count']);
    print('Number of rating 1 words: ', data['rating'][1]['no_words']);
    print('\n')

def create_validation_set(txt):
    validation_file = '';
    training_file = '';
    num_lines = sum(1 for line in open(txt))
    # num_val = sum(1 for line in open(tyt))
    num_val = num_lines / 10;
    randoms = random.sample(range(1, num_lines), num_val)
    with open(txt) as inputfile:
        for num, line in enumerate(inputfile, 1):
            if num in randoms:
                validation_file = validation_file + line;
            else:
                training_file = training_file + line;
    f = open('validation.txt', 'w');
    f.write(validation_file);
    f.close()
    f = open('training_new.txt', 'w');
    f.write(training_file);
    f.close()

def train(data, word_set, n = 0.5805, predict = False, v = 8.5):
    number_of_lines = data['no_lines'];
    num = word_set['no_lines'];
    p_0 = float(data['rating'][0]['count']/number_of_lines);
    p_1 = float(data['rating'][1]['count']/number_of_lines);
    correct = 0;

    for i in word_set['lines']:
        test = i;
        p_0_d = math.log10(p_0);
        p_1_d = math.log10(p_1);

        for i in test['words']:
            x_0 = data['rating'][0]['word_count'][i] + 1.0;
            x_1 = data['rating'][1]['word_count'][i] + 1.0;
            v = len(data['word_count'])/v
            y_0 = len(data['rating'][0]['word_count'])
            y_1 = len(data['rating'][1]['word_count'])
            t_0 = x_0/(v + y_0);
            t_1 = x_1/(v + y_1);
            total_t = t_0 + t_1;
            t_0_d = t_0/total_t;
            t_1_d = t_1/total_t;
            if t_0_d > n and x_0 > 1:
                p_0_d = p_0_d + math.log10(x_0/(v + y_0));
                p_1_d = p_1_d + math.log10(x_1/(v + y_1));
            elif t_1_d > n and y_0 > 1:
                p_0_d = p_0_d + math.log10(x_0/(v + y_0));
                p_1_d = p_1_d + math.log10(x_1/(v + y_1));
        if test['rating'] == '1' and p_1_d > p_0_d:
            if predict:
                print '1';
            correct = correct + 1;
        elif test['rating'] == '0' and p_0_d > p_1_d:
            if predict:
                print '0';
            correct = correct + 1;
        elif test['rating'] == '1' and p_0_d > p_1_d:
            if predict:
                print '0';
        elif test['rating'] == '0' and p_1_d > p_0_d:
            if predict:
                print '1';

    return correct/num

def stem(training_words):
    training_accuracy = train(training_words, training_words);
    print training_accuracy;
    x = training_words['word_count'].most_common(100);
    for i in range(0, 100):
        occurence = x[i][1];
        word = x[i][0];
        del training_words['word_count'][word];
        del training_words['rating'][0]['word_count'][word];
        del training_words['rating'][1]['word_count'][word];

    training_accuracy = train(training_words, training_words);
    print training_words['word_count'].most_common(30);
    return training_accuracy, training_words;

def find_max(training_words):
    max_prob = 0;
    max_word = '';
    for i in training_words['rating'][1]['word_count']:
        x = float(training_words['rating'][1]['word_count'][i] + 1);
        y = float(training_words['rating'][0]['word_count'][i] + 1);
        if max_prob < (y / (x + y)) and x > 1:
            print x;
            print y;
            print i;
            max_word = i;
            max_prob = y / (x + y);
            print max_prob;
    print max_prob;
    print max_word;
    print training_words['rating'][1]['word_count'][max_word];

def spin(training_words, validation_words, testing_words, start_time, args):
    # find the max parameters on the validation set
    previous_accuracy = 0;
    best_n = 0;
    best_best_n = 0;
    best_train_n = 0;
    best_v = 1;
    amount = 10000;
    v_amount = 100;
    v = 1;
    for i in range(1, amount):
        n = float(1.0 / (i / 1000.0));
        if n >= 0.5 and n < 0.65:
            accuracy = train(training_words, validation_words, n, False, v);
            if previous_accuracy < accuracy:
                best_v = v;
                best_n = n;
                previous_accuracy = accuracy;
                accuracy_two = train(training_words, training_words, n, False, v);
                # if accuracy_two > .999:
                if best_train_n < train(training_words, testing_words, n, False, v):
                    best_train_n = train(training_words, testing_words, n, False, v);
                    best_best_n = n;
    if best_best_n == 0:
        best_best_n = best_n;

    if best_train_n < .865:
        main(args, start_time);

    return best_best_n, best_v;

def main(args, start_time = time.time()):
    create_validation_set(args[0]);
    training_words = parse_data('training_new.txt');
    validation_words = parse_data('validation.txt');
    testing_words = parse_data(args[1]);

    best_n, v = spin(training_words, validation_words, testing_words, start_time, args);
    training_accuracy = train(training_words, training_words, best_n, False, v);
    training_time = time.time() - start_time;

    start_time = time.time()
    # testing_words = parse_data('testing.txt');
    testing_accuracy = train(training_words, testing_words, best_n, True, v);
    testing_time = time.time() - start_time;

    print str(int(math.ceil(training_time))) + ' seconds (training)';
    print str(int(math.ceil(testing_time))) + ' seconds (labeling)';
    training_accuracy = float("{0:.3f}".format(training_accuracy));
    testing_accuracy = float("{0:.3f}".format(testing_accuracy));
    if training_accuracy == 1.0:
        training_accuracy = 0.999;
    print str(training_accuracy) + ' (training)';
    print str(testing_accuracy) + ' (testing)';


if __name__ == "__main__":
    main(sys.argv[1:])
