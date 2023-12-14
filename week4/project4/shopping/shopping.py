import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    with open(filename) as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append(list(map(convertor, row.keys(), row.values())))
    evidence = [row[:-1] for row in data]
    labels = [row[-1] for row in data]
    return (evidence, labels)



def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    return KNeighborsClassifier(n_neighbors=1).fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    accurate_labels = []
    for actual, predicted in zip(labels, predictions):
        if actual == predicted:
            accurate_labels.append(actual)

    accurate_positives = accurate_labels.count(1)
    accurate_negatives = accurate_labels.count(0)

    actual_positives = labels.count(1)
    actual_negatives = labels.count(0)

    sensitivity = accurate_positives / actual_positives
    specificity = accurate_negatives / actual_negatives
    return (sensitivity, specificity)
    


def convertor(key, value):
    if key in [
        'Administrative', 'Informational', 'ProductRelated',
        'OperatingSystems', 'Browser', 'Region', 'TrafficType'
    ]:
        return int(value)
    elif key in [
        'Administrative_Duration', 'Informational_Duration',
        'ProductRelated_Duration', 'BounceRates', 'ExitRates',
        'PageValues', 'SpecialDay']:
        return float(value)
    elif key == 'Month':
        months =  ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        months_dict = dict(zip(months, range(0,12)))
        return months_dict[value]
    elif key == 'VisitorType':
        if value == 'Returning_Visitor':
            return 1
        return 0
    elif key == 'Weekend':
        return 1 if value == 'TRUE' else 0
    else:
        return 1 if value == 'TRUE' else 0

    
if __name__ == "__main__":
    main()
