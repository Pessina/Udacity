# coding: utf-8
#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
# Import all features, to posterior selection
features_list = ['poi', 'salary', 'deferral_payments', 'total_payments', 'loan_advances', 'bonus', 'restricted_stock_deferred', 'deferred_income',\
 'total_stock_value', 'expenses', 'exercised_stock_options', 'other', 'long_term_incentive', 'restricted_stock', 'director_fees', 'to_messages',
 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

# Load data on data frame to easir manipulation
df = pd.DataFrame.from_dict(data_dict, orient='index')
df = df.drop(['email_address'], axis=1)
df.replace('NaN', np.nan, inplace = True)

# Uncomment to see dataframe info
# df.info()

### Task 2: Remove outliers
# To better explore the outliers lets plot the data

# Uncomment to see the total outlier
# df.plot.scatter(x = 'salary', y = 'bonus')
# df['salary'].idxmax()

df.drop('TOTAL', inplace = True)

# df.plot.scatter(x = 'salary', y = 'bonus')

### Task 3: Create new feature(s)

# Plor before new features
# ax = df[df['poi'] == False].plot.scatter(x='from_this_person_to_poi', y='from_poi_to_this_person', color='blue', label='non-poi')
# df[df['poi'] == True].plot.scatter(x='from_this_person_to_poi', y='from_poi_to_this_person', color='red', label='poi', ax=ax)

df['percentage_from_poi'] = df['from_poi_to_this_person'] / df['to_messages']
df['percentage_to_poi'] = df['from_this_person_to_poi'] / df['from_messages']

# Plor after new features
# ax = df[df['poi'] == False].plot.scatter(x='percentage_from_poi', y='percentage_to_poi', color='blue', label='non-poi')
# df[df['poi'] == True].plot.scatter(x='percentage_from_poi', y='percentage_to_poi', color='red', label='poi', ax=ax)

# Testing the classifier performance with new features
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cross_validation import train_test_split

df = df.fillna(value=0.0)

# Uncomment to cheack performance of classifieras before and after new features
# def evaluate_metrics (clf, features_test, labels_test):
#     accuracy = clf.score(features_test, labels_test)
#     predict = clf.predict(features_test)
#     precision = precision_score(labels_test, predict)
#     recall = recall_score(labels_test, predict)
#     return accuracy, precision, recall
#
# # Creating classifiers
# clf_gaussianNB = GaussianNB()
# clf_decision_tree = DecisionTreeClassifier(random_state=0)
# clf_ad_boost = AdaBoostClassifier()
#
# classifiers = [
#     {
        # 'name': 'Gaussian NB',
#         'clf': clf_gaussianNB
#     },
#     {
#         'name': 'Decision Tree',
#         'clf': clf_decision_tree
#     },
#     {
#         'name': 'AdaBoost',
#         'clf': clf_ad_boost
#     }
# ]
#
# ### Getting features and labels from dataframe
# labels = df['poi'].values
# features = df.drop(['percentage_from_poi', 'percentage_to_poi', 'poi'], axis=1).values
#
# features_train, features_test, labels_train, labels_test =     train_test_split(features, labels, test_size=0.3, random_state=42)
#
# print ('Values before new features:')
# for classifier in classifiers:
#     classifier['clf'].fit(features_train, labels_train)
#     accuracy, precision, recall = evaluate_metrics(classifier['clf'], features_test, labels_test)
#     print (classifier['name'] +           ' accuracy=' + str(accuracy) +           ' precision=' + str(precision) +           ' recall=' + str(recall))
#
# ### Getting features and labels from dataframe
# labels = df['poi'].values
# features = df.drop(['poi'], axis=1).values
#
# features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.3, random_state=42)
#
# print ('\nValues after new features:')
# for classifier in classifiers:
#     classifier['clf'].fit(features_train, labels_train)
#     accuracy, precision, recall = evaluate_metrics(classifier['clf'], features_test, labels_test)
#     print (classifier['name'] +           ' accuracy=' + str(accuracy) +           ' precision=' + str(precision) +           ' recall=' + str(recall))


from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import RFECV
from sklearn.pipeline import Pipeline

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Use GridSearchCV to tune and find the best parameters to my algorithm
# Uncomment to check what paremeters GridSearchCV choose as the best for each classifier
# def tunning_clf(clf, features, labels):
#
#     selector = SelectKBest(f_classif)
#
#     pipeline = Pipeline([('selector', selector), ('clf', clf['clf'])])
#     if clf['name'] == 'Gaussian NB':
#         parameters = [
#             {
#                 'selector__k': range(1, 10),
#             }
#         ]
#     if clf['name'] == 'Decision Tree':
#         parameters = [
#             {
#                 'selector__k': range(1, 10),
#                 'clf__min_samples_split': range(2, 10),
#             }
#         ]
#     if clf['name'] == 'AdaBoost':
#         parameters = [
#             {
#                 'selector__k': range(1, 10),
#                 'clf__n_estimators': range(10, 100, 10),
#             }
#         ]
#
#
#     grid_search = GridSearchCV(pipeline, parameters)
#     grid_search.fit(features, labels)
#
#     return grid_search.best_estimator_
#
# # Creating classifiers
# clf_gaussianNB = GaussianNB()
# clf_decision_tree = DecisionTreeClassifier(random_state=0)
# clf_ad_boost = AdaBoostClassifier()
#
# classifiers = [
#     {
#         'name': 'Gaussian NB',
#         'clf': clf_gaussianNB
#     },
#     {
#         'name': 'Decision Tree',
#         'clf': clf_decision_tree
#     },
#     {
#         'name': 'AdaBoost',
#         'clf': clf_ad_boost
#     }
# ]
#
# #Now lets select what features we will use
# labels = df['poi']
# features = df.drop(['poi'], axis=1)
#
# clf = tunning_clf(classifiers[0], features, labels)
# print(clf.get_params)
#
# clf = GaussianNB()
#
# # Selecting features with kbest
# selector = SelectKBest(f_classif, k=5)
# selector.fit_transform(features, labels)
#
# # # Filtering features from dataframe
# mask = selector.get_support()
# new_features = list(features.columns[mask])
# features_list = features_list + new_features
# features = features.loc[:, new_features]


### Task 5: Tune your classifier to achieve better than .3 precision and recall
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info:
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
labels = df['poi']
features = df.drop(['poi'], axis=1)
features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.3, random_state=42)

clf = GaussianNB()
features_list=['poi']

# Selecting features with kbest
selector = SelectKBest(f_classif, k=5)
selector.fit_transform(features, labels)

# # Filtering features from dataframe
mask = selector.get_support()
new_features = list(features.columns[mask])
features_list = features_list + new_features
features = features.loc[:, new_features]
features.columns

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.
my_dataset = df.to_dict(orient='index')
dump_classifier_and_data(clf, my_dataset, features_list)
