# Recursive Feature Elimination
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn_pandas import DataFrameMapper
from dataprocessor import ProcessData, Filter

result_file = open("testresult.txt", "a")
for num_features in range(10, 24):
    training_frame = ProcessData.trainData()
    testing_frame = ProcessData.testData()

    # Remove anomalies in training frame based on percentile
    all_columns = list(training_frame.columns)
    rm_columns = ['UnitNumber', 'Time', 'Setting1', 'Setting2', 'Setting3', 'RUL']
    filter_columns = [x for x in all_columns if x not in rm_columns]
    training_frame = Filter.filterDataPercentile(panda_frame=training_frame, columns=filter_columns, lower_percentile=0.01, upper_percentile=0.99, column_err_threshold=3, order='above')

    # Training data columns
    del training_frame['UnitNumber']
    del training_frame['Time']

    # Testing columns
    del testing_frame['UnitNumber']
    del testing_frame['Time']

    training_columns = list(training_frame.columns)
    training_columns.remove('RUL')
    response_column = 'RUL'

    # Set mapper
    df_mapper = DataFrameMapper([(training_columns, None), (response_column, None)])

    # Train data - pandas to sklearn
    data = df_mapper.fit_transform(training_frame)

    # Test data - pandas to sklearn
    test = df_mapper.fit_transform(testing_frame)

    features = df_mapper.features[0][0]
    response = df_mapper.features[1][0]


    # [row : column]
    column_count = len(data[0, :])

    # Sklearn data
    x_train = data[:, 0:column_count-1]
    y_train = data[:, column_count-1]
    x_test = test[:, 0:column_count-1]
    y_test = test[:, column_count-1]

    # Setting up algorithm
    rf = RandomForestRegressor(max_depth=20, n_estimators=50)


    rfe = RFE(rf, num_features)
    rfe = rfe.fit(x_train, y_train)

    # summarize the selection of the attributes
    support = rfe.ranking_
    ranking = rfe.ranking_

    selected_features = [features[i] for i in range(len(support)) if support[i] == True]

    training_frame = pd.read_csv('datasets/train.csv')
    testing_frame = pd.read_csv('datasets/test.csv')

    for feature in training_columns:
        if feature not in selected_features:
            print "Removed :",feature
            del training_frame[feature]
            del testing_frame[feature]

    selected_features = list(training_frame.columns)
    selected_features.remove('UnitNumber')
    selected_features.remove('Time')
    selected_features.remove('RUL')


    training_frame = ProcessData.trainDataToFrame(training_frame=training_frame, selected_column_names=selected_features, moving_k_closest_average=True, standard_deviation=True)
    testing_frame = ProcessData.testDataToFrame(testing_frame=testing_frame, selected_column_names=selected_features, moving_k_closest_average=True, standard_deviation=True)

    # Training data columns
    del training_frame['UnitNumber']
    del training_frame['Time']

    # Testing columns
    del testing_frame['UnitNumber']
    del testing_frame['Time']

    training_columns = list(training_frame.columns)
    training_columns.remove('RUL')
    response_column = 'RUL'

    # Set mapper
    df_mapper = DataFrameMapper([(training_columns, None), (response_column, None)])

    # Train data - pandas to sklearn
    data = df_mapper.fit_transform(training_frame)

    # Test data - pandas to sklearn
    test = df_mapper.fit_transform(testing_frame)

    # [row : column]
    column_count = len(data[0, :])

    # Sklearn data
    x_train = data[:, 0:column_count-1]
    y_train = data[:, column_count-1]
    x_test = test[:, 0:column_count-1]
    y_test = test[:, column_count-1]

    for i in xrange(5):
        print "N Features : ", num_features, "Iteration : ", i+1
        rf.fit(x_train,y_train)
        result = rf.predict(x_test)

        rmse = mean_squared_error(y_test, result) ** 0.5
        mae = mean_absolute_error(y_test, result)
        print "Root Mean Squared Error", rmse
        print "Mean Absolute Error", mae

        string = "Num Features" + "," + str(num_features) + "," + str(rmse) + "," + str(mae) + "\n"
        result_file.write(string)
result_file.close()







