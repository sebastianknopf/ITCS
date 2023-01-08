import json
import ast
import locale

import numpy as np
import pandas as pd

from argparse import ArgumentParser


def generate_result_table(filename, inputs):

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    for name, file in inputs.items():

        # read JSON data
        with open(file, 'r') as f:
            q_data = json.load(f)

            f.close()

            # remap q data to q-table
            q_table = {ast.literal_eval(k): np.array(v) for k, v in q_data.items()}

            # fill results in schema: route, scenario => action to choose
            df = pd.DataFrame({
                'route': [k[0] for k, v in q_table.items() if k[1] == 0],
                'scenario': [k[2] for k, v in q_table.items() if k[1] == 0],
                'action': [np.argmax(v) for k, v in q_table.items() if k[1] == 0],
            })

            df.to_excel(writer, sheet_name=name, index=False)

    writer.close()


def print_result_table(filename):

    # locale settings
    locale.setlocale(locale.LC_ALL, 'de')

    # read JSON data
    with open(filename, 'r') as f:
        q_data = json.load(f)

        f.close()

        # remap q data to q-table
        q_table = {ast.literal_eval(k): np.array(v) for k, v in q_data.items()}

        for k, v in q_table.items():
            if k[1] == 0:

                print('route: {0}, scenario: {1}'.format(k[0], k[2]))
                for action in v:
                    print(locale.format('%.4f', action, 1))

                print()


if __name__ == '__main__':

    # add options parser
    parser = ArgumentParser()
    parser.add_argument('-f', '--full', dest='env_full', action='store_true')
    parser.add_argument('-p', '--print', dest='print', action='store_true')

    args = parser.parse_args()

    # generate output file
    if args.env_full:
        filename = 'output/results-village.xlsx'
    else:
        filename = 'output/results.xlsx'

    generate_result_table(filename, {
        'Q-Learning': 'output/q-learning.json',
        'SARSA': 'output/ne-sarsa.json',
        'Expected SARSA': 'output/ne-expected-sarsa.json',
    })

    # print results for each file
    if args.print:

        np.set_printoptions(edgeitems=0)
        np.core.arrayprint._line_width = 250

        print('Q-Learning')
        print_result_table('output/q-learning.json')
        print()

        print('SARSA')
        print_result_table('output/ne-sarsa.json')
        print()

        print('Expected SARSA')
        print_result_table('output/ne-expected-sarsa.json')
        print()
