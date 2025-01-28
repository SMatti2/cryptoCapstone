import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error


def evaluate_and_plot(actual_df, predicted_df, actual_col, predicted_col, title):
    comparison_df = pd.DataFrame(
        {
            "Actual": actual_df[actual_col],
            "Predicted": predicted_df[predicted_col],
        }
    )

    # calculate MSE and MAE
    mse = mean_squared_error(comparison_df["Actual"], comparison_df["Predicted"])
    mae = mean_absolute_error(comparison_df["Actual"], comparison_df["Predicted"])

    print(f"{title} - MSE: {mse:.4f}")
    print(f"{title} - MAE: {mae:.4f}")

    # plot
    plt.figure(figsize=(15, 5))
    plt.plot(comparison_df.index, comparison_df["Actual"], label="Actual", color="blue")
    plt.plot(
        comparison_df.index,
        comparison_df["Predicted"],
        label="Predicted",
        color="red",
        alpha=0.7,
    )
    plt.title(f"{title} - Actual vs. Predicted Log Price Change")
    plt.xlabel("Date")
    plt.ylabel("Log Price Change")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return mse, mae
