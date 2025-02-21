from pathos.multiprocessing import ProcessingPool
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from sklearn.cluster import Birch
import gc


def default_evaluate(rst_lst):
    return np.hstack([ctt[1] for ctt in rst_lst])


def rolling_test(model, X, y, train_count, evaluate_func=default_evaluate):
    _Pool = ProcessingPool()

    def _task(args):
        try:
            model, X_train_mat, y_train_mat, X_test_mat = args

            #cl_model = Birch(n_clusters=5)
            #X_train_mat = np.hstack((X_train_mat, cl_model.fit_predict(X_train_mat).reshape(-1, 1)))
            #X_test_mat = np.hstack((X_test_mat, cl_model.predict(X_test_mat).reshape(-1, 1)))
            #del cl_model

            model.fit(X_train_mat, y_train_mat)
            
            gc.collect()
            return model.predict(X_train_mat), model.predict(X_test_mat)
        except:
            gc.collect()
            return np.ones(X_train_mat.shape[0], ) * np.nan, np.ones(X_test_mat.shape[0], ) * np.nan

    rst_lst = _Pool.map(_task, ((deepcopy(model), X[i - train_count:i, :], y[i - train_count:i], X[i, :].reshape(1, -1)) for i in range(train_count, len(y))))

    return np.hstack((np.zeros(train_count, ), evaluate_func(rst_lst)))


def rolling_test_single(model, X, y, train_count, evaluate_func=default_evaluate):

    def _task(args):
        model, X_train_mat, y_train_mat, X_test_mat = args
        model.fit(X_train_mat, y_train_mat)
        return model.predict(X_train_mat), model.predict(X_test_mat)

    rst_lst = list(map(_task, ((deepcopy(model), X[i - train_count:i, :], y[i - train_count:i], X[i, :].reshape(1, -1)) for i in range(train_count, len(y)))))

    return np.hstack((np.zeros(train_count, ), evaluate_func(rst_lst)))


if __name__ == "__main__":
    import numpy as np
    from sklearn.tree import DecisionTreeClassifier

    X = np.random.rand(80000, 100)
    y = np.random.randint(-1, 1, (80000, 1))

    model = DecisionTreeClassifier()

    tt = rolling_test_single(model, X, y, 100)
    print(tt)

    print(1)