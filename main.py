
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas_ta as ta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calc_strength(ticker, period='3mo'):
    data = yf.download(ticker, period=period)
    data['ADX'] = ta.adx(data['High'], data['Low'], data['Close'])['ADX_14']
    data['VPT'] = ta.vpt(data['Close'], data['Volume'])
    data['OBV'] = ta.obv(data['Close'], data['Volume'])
    recent_data = data.tail(5)
    adx_latest = recent_data['ADX'].iloc[-1]
    adx_score = min((adx_latest / 50) * 100, 100)
    vpt_trend = recent_data['VPT'].iloc[-1] - recent_data['VPT'].iloc[0]
    vpt_score = 100 if vpt_trend > 0 else 0
    obv_trend = recent_data['OBV'].iloc[-1] - recent_data['OBV'].iloc[0]
    obv_score = 100 if obv_trend > 0 else 0
    final_score = round((adx_score * 0.4 + vpt_score * 0.3 + obv_score * 0.3), 2)
    return {"ticker": ticker, "adx": round(adx_score,2), "vpt": vpt_score, "obv": obv_score, "total_score": final_score}

@app.get("/strength/{ticker}")
async def strength(ticker: str):
    return calc_strength(ticker)
