import optuna


def objective(trial, X_train, y_train, X_val, y_val, train_lstm):
    # LSTM layers
    num_lstm_layers = trial.suggest_int("num_lstm_layers", 1, 3)
    chosen_lstm_units = []
    for i in range(num_lstm_layers):
        chosen_lstm_units.append(
            trial.suggest_int(f"lstm_units_{i+1}", 32, 256, step=32)
        )

    # Dense layers
    num_dense_layers = trial.suggest_int("num_dense_layers", 0, 3)
    chosen_dense_units = []
    for i in range(num_dense_layers):
        chosen_dense_units.append(
            trial.suggest_int(f"dense_units_{i+1}", 32, 256, step=32)
        )

    # other hyperparameters
    dropout_rate = trial.suggest_float("dropout_rate", 0.0, 0.5, step=0.1)
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])

    params = {
        "lstm_units": chosen_lstm_units,
        "dense_units": chosen_dense_units,
        "dropout_rate": dropout_rate,
        "learning_rate": learning_rate,
        "epochs": 100,
        "batch_size": batch_size,
    }

    # train
    model, history = train_lstm(X_train, y_train, X_val, y_val, params)
    val_loss = min(history.history["val_loss"])

    return val_loss


def tune_hyperparameters(X_train, y_train, X_val, y_val, train_lstm, n_trials=50):
    study = optuna.create_study(direction="minimize")
    study.optimize(
        lambda trial: objective(trial, X_train, y_train, X_val, y_val, train_lstm),
        n_trials=n_trials,
    )

    print("Best trial:")
    best_trial = study.best_trial
    print(f"  Value (val_loss): {best_trial.value}")
    print("  Params:")
    for key, value in best_trial.params.items():
        print(f"    {key}: {value}")

    return study
