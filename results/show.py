import pandas as pd
import matplotlib.pyplot as plt


def gen_analysis(files, filter_by="category"):
    """
    return DataFrame including accuracy data filtered by options
    parameters
    ----------
        filter_by:
            category
            sentence_position
    """
    submissions = {}
    for ii in submission_files:
        submission_date = ii.split('_')[1]
        print ">>> ", submission_date, filter_by
        submission = pd.read_csv(ii, names=['Question ID', 'Estimation'],
                                 index_col='Question ID',  header=0)
        submission.sort_index(inplace=True)

        # accuracy of each category per submission
        num_items_cat = master_set.groupby(filter_by).size()
        is_correct = master_set['Answer'] == submission['Estimation']
        num_correct_items_cat = master_set[is_correct].groupby(filter_by).size()
        category_accuracy = num_correct_items_cat / num_items_cat

        # accuracy of submission
        num_questions = len(master_set)
        num_correct = len(master_set[is_correct])
        submission_accuracy = float(num_correct) / float(num_questions)

        # accuracy of submission with accuracy of each category
        accu = category_accuracy.append(pd.Series(submission_accuracy,
                                                  index=['accuracy']))
        print accu, "\n"

        # collect accuracy information
        submissions.update({pd.to_datetime(submission_date): accu})

    # making dataframe
    df = pd.DataFrame(submissions).T
    return df


if __name__ == "__main__":
    # test_set and answer_key path
    test_set_path = 'test.csv'
    answer_key_path = 'key.csv'

    # 4 submission files from 30 submissions
    submission_files = ['submit_20141118_a9c3331.csv',
                        'submit_20141203_702eb0a.csv',
                        'submit_20141211_ec6ccf6.csv',
                        'submit_20141220_06c89ea.csv']

    # read base date
    test_set = pd.read_csv(test_set_path, index_col='Question ID',
                           usecols=[0, 3, 5], header=0)
    answer_key = pd.read_csv(answer_key_path, index_col='Question ID', header=0)
    master_set = answer_key.join(test_set)
    master_set.sort_index(inplace=True)

    df_by_category = gen_analysis(submission_files, filter_by='category')
    df_by_position = gen_analysis(submission_files,
                                  filter_by="Sentence Position")

    # with from 0.0 to 1.0
    # ax = df.plot(ylim=(0,1), marker='x')
    df_by_category.plot(figsize=(12, 10), marker='o')
    df_by_position.plot(figsize=(12, 10), marker='o')
    # plt.show()
