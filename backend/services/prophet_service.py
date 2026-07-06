"""Prophet ML 30일 주가 예측"""
import logging
import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


def run_forecast(ticker_yf: str) -> dict:
    from prophet import Prophet

    df = yf.download(ticker_yf, period="2y", progress=False, auto_adjust=True)
    if df is None or df.empty:
        raise ValueError("예측용 데이터를 가져올 수 없습니다.")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    prophet_df = pd.DataFrame({"ds": df.index.to_list(), "y": df["Close"].values.tolist()})

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05,
        interval_width=0.8,
    )
    model.fit(prophet_df)

    future   = model.make_future_dataframe(periods=30, freq="B")
    forecast = model.predict(future)
    fut      = forecast[forecast["ds"] > prophet_df["ds"].max()]

    curr_price = float(df["Close"].iloc[-1])
    pred_price = float(fut["yhat"].iloc[-1])
    chg        = (pred_price - curr_price) / curr_price * 100

    return {
        "current_price":   round(curr_price, 2),
        "predicted_price": round(pred_price, 2),
        "change_pct":      round(chg, 2),
        "forecast": [
            {
                "date":      r["ds"].strftime("%Y-%m-%d"),
                "predicted": max(round(float(r["yhat"]),       2), 0),
                "upper":     max(round(float(r["yhat_upper"]), 2), 0),
                "lower":     max(round(float(r["yhat_lower"]), 2), 0),
            }
            for _, r in fut.iterrows()
        ],
    }
