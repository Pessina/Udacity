# Enron dataset analysis
## 1. Introduction
This machine learning project, is based on a public dataset from Enron, that was one of the greatest american company, but it was involved on a fraud. And the Government investigated it, and some of the company executives was arrested (during the project we will call them poi - person of interest). After the investigation some data from the company came to public, like emails trade between employees, salary, bonus, stock options, etc. And we can use it to train a machine learning model and find patterns on data to predict who else is involved on fraud, but didn't get arrested.
The dataset have 146 data points, 19 features and the poi labels. For the project I used a supervised machine learning with the 5 best features selected using SelectKBest. For the first part of analysis, I inspect the dataset searching for features with too much null values and outlier. Two columns have too much null values loan_advances and director_fees for the outliers I found one, but its not a person its the total, and of course I removed it

## 2. Feature Selection and Scaling
One of my first steps on my analysis is explore the dataset and see if is useful create new features to better visualize the data or increase the performance for my algorithm. Then I created two new features: percentage_to_poi, percentage_from_poi that represents the percentage of messages traded with poi person for each person. My main motivation to create those features, was that I thought that one of the most important features to determine if a person is poi or not is the number of emails traded with poi. Using just the total number, i can’t see a clearly relationship between these features and poi label, then I created new features to help me
In this project I used SelectKBest combined with GridSearchCV to choose what are the best features for my model. The GridSearch return to me that the best k parameter for SelectKBest combined with my GaussianNB classifier is 5, than I use 5 features on my final model, that are salary,  exercised_stock_options, bonus, total_stock_value, percentage_to_poi. As we can see one of the features created, was selected by SelectKBest to be on my final model.
I didn't scale any feature, as my classifier (GaussianNB) don't require it.
Bellow you can check the features importance gave by SelectKBest:
1. exercised_stock_options - 25.3801052997602
1. total_stock_value - 24.752523020258508
1. bonus - 21.3278904139791
1. salary - 18.861795316466416
1. percentage_to_poi - 16.873870264572993
1. deferred_income - 11.732698076065354
1. long_term_incentive - 10.222904205832778
1. restricted_stock - 9.480743203478934
1. total_payments - 8.96781934767762
1. shared_receipt_with_poi - 8.903821557165571
1. loan_advances - 7.301406651536036
1. expenses - 6.3746144901977475
1. from_poi_to_this_person - 5.446687483325353
1. other - 4.263576638144469
1. percentage_from_poi - 3.293828632029562
1. from_this_person_to_poi - 2.470521222656084
1. director_fees - 2.0893098994318806
1. to_messages - 1.7516942790340737
1. deferral_payments - 0.20970584227026345
1. from_messages - 0.1587702392129193
1. restricted_stock_deferred - 0.0644770280387286

## Classifiers used
For my final model I choose to use the GaussianNB that had the best performance. But I also tried AdaBoostClassifier and DecisionTreeClassifier. Here you can check their performance:
1. GaussianNB:
    1. Accuracy - 0.85
    1. Precision - 0.49
    1. Recall - 0.32
1. Decision tree:
    1. Accuracy - 0.79
    1. Precision - 0.28
    1. Recall- 026
1. AdaBoostClassifier:
    1. Accuracy - 0.83
    1. Precision - 0.37
    1. Recall - 0.27

## Classifier Tuning
Tune a machine learning algorithm means that you will try different parameters for the model and select the best set, that gives you the best performance for your dataset. In other words, you have to make the best fit between your model and the data to achieve the best performance, and you do this adjusting your algorithm parameters, tuning it. If I don't do this well, my model will not achieve the best performance that it can.
The importance of tune the algorithm is try to achieve the best performance for it, the best fit between your model and the data. And one way to do it is trying different values for classifier parameters.
To tune my model I chose GridSearchCV, that try different combinations of parameters for my feature selection and classifier, and return to me the best one, that I used on my final model.
The GaussianNB algorithm don't have parameters to tune, but the others classifiers that I used, DecisionTreeClassifier and AdaBoostClassifier have. Let's take as example the Decision Tree to explain how I did its running, first I searched on sklearn documentation what are the available parameters that I can tune. Then a I selected some of then, and give a set of values, that I think is good, to GridSearchCV, and this algorithm tried all of them and retrieve to me the best set of parameters.

## Validation
Validation is a process to check if the algorithm generalize well, and have good performance metrics like accuracy, precision, recall, etc. One common mistake on validation is overfitting, that occurs when you train and test your model on same data, and it doesn't mean that the algorithm "learn" and generalized the data, but it can mean it memorized the results and repeated it on validation phase. To avoid it, a good practice is split our dataset on training and test data. In my case i splitted the data in 70% for training and 30% to test
I also used the tester.py script to validate my model, that uses Stratified Shuffle Split cross validation. This algorithm create multiple train and test sets, and uses it to evaluate my algorithm metrics, this is a good approach for this case due the small number of data entries.

## Performance
As we saw on Classifier Tuning section, my final model get this scores:
1. GaussianNB:
    1. Accuracy - 0.85
    1. Precision - 0.49
    1. Recall - 0.32

I get theses scores on tester.py, file provided from udacity on final_project folder. Here we will not explore the accuracy metric, due my explanation on the last section why this metric is not useful here. But in general words accuracy is the simple division of correct prediction by total prediction.
Here the precision and recall is more important, let's make a little explanation what they mean.
* Precision: it's a metric that measure the fraction of true positives predictions by all positive predictions. In other words how many of our positive predictions really are positive
* Recall: its a metric that measure the fraction of true positive predictions by total positive values on dataset. In other words how many of our positive values was correct predicted.

For our model, these metrics are important because we have a little set of pois person, what makes accuracy useless. And with these metrics we can look directly to what fraction of pois we predicted correct, and what fraction of our pois prediction was correct. What are greater metrics to evaluate our model performance.

