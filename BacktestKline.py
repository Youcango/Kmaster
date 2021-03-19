from binance.client import Client
import talib
import numpy as np
import config
import requests


def Notice_user(message, title):
    """

    :param message: text messages
    :return: None
    """
    print(message)
    keys = config.Notice_keys
    for k in keys:
        url = config.server_jiang_url.format(k, title, config.interval, message, )
        requests.get(url)


def Get_lines(limit, symbol, interval):
    """

    :param limit: max 1000
    :param symbol: Only in binance
    :param interval: 1m,5m,15m,20m,30m,1h,4h,1d
    :return:
     [
      [
        1499040000000,      // 开盘时间
        "0.01634790",       // 开盘价
        "0.80000000",       // 最高价
        "0.01575800",       // 最低价
        "0.01577100",       // 收盘价(当前K线未结束的即为最新价)
        "148976.11427815",  // 成交量
        1499644799999,      // 收盘时间
        "2434.19055334",    // 成交额
        308,                // 成交笔数
        "1756.87402397",    // 主动买入成交量
        "28.46694368",      // 主动买入成交额
        "17928899.62484339" // 请忽略该参数
      ]
    ]
    """
    requests_params = {
        'proxies': {
            'http': 'socks5h://127.0.0.1:7890',
            'https': 'socks5h://127.0.0.1:7890'
        }
    }

    api_key = 'tOMH3vfjL5wbeRD5B3AwWQr3vcchDN3ZHC5ZVmhmhIlgFGfuwUMliQB23iMKA14W'  # binance账户的api_key
    secret = 'JIvSmhJJNYOHR9ABPCkcwqhiTkCrfiIDjgFR4DWMtCYk6oiTHlbxCekWa5LxlULi'  # binance账户的secret
    client = Client(api_key, secret, requests_params=requests_params)
    Kdata = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    return Kdata


def str2float(data):
    """

    :param data: list contans str
    :return: list contans float
    """
    a = list()
    for x in data:
        a.append(list(map(float, x)))
    return a


def cci_cacul(Kline, timeperiod=20):
    data1 = dict()
    data1["high"] = Kline[:, 2][-timeperiod * 2:]
    data1["low"] = Kline[:, 3][-timeperiod * 2:]
    data1["close"] = Kline[:, 4][-timeperiod * 2:]
    cci = talib.CCI(data1["high"], data1["low"], data1["close"], timeperiod=timeperiod)
    print(cci[-1], cci[-2])
    return cci


# 定义画图函数
def can_vol(Kline, symbol):
    import numpy as np
    import plotly.graph_objects as go
    import time
    data1 = dict()
    data1["index"] = list(time.strftime("%Y-%m-%d %H:%M", time.localtime(x / 1000)) for x in Kline[:, 6])
    data1["open"] = Kline[:, 1]
    data1["high"] = Kline[:, 2]
    data1["low"] = Kline[:, 3]
    data1["close"] = Kline[:, 4]
    data1["volume"] = Kline[:, 5]
    cii20_data = cci_cacul(Kline, 20)
    ma20_data = talib.MA(data1["close"], timeperiod=20, )
    if cii20_data[-1] > 60:
        if (cii20_data[-1] > 95) and (cii20_data[-2] > 90) and (
                ma20_data[-1] < data1["close"][-1]) and config.position != config.position_option[1]:
            config.position = config.position_option[1]
            Notice_user(
                "{} 预计{}即将暴涨了！！！开多梭哈".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), symbol),
                "开多{}".format(symbol))
        if (cii20_data[-1] < 105) and (cii20_data[-2] < 110) and config.position != config.position_option[2]:
            config.position = config.position_option[2]
            Notice_user(
                "{} 预计{}即将下跌回调！！！速度平多".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), symbol),
                "平多{}".format(symbol))
    if cii20_data[-1] < -60:
        if (cii20_data[-1] < -100) and (cii20_data[-2] < -95) and (
                ma20_data[-1] > data1["close"][-1]) and config.position != config.position_option[3]:
            config.position = config.position_option[3]
            Notice_user(
                "{} 预计{}即将暴跌了！！！速度开空".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), symbol),
                "开空{}".format(symbol))
        if (cii20_data[-1] > -105) and (cii20_data[-2] > -110) and config.position != config.position_option[4]:
            config.position = config.position_option[4]
            Notice_user(
                "{} 预计{}即将上涨了！！！速度平空".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), symbol),
                "平空{}".format(symbol))
    print(
        "{} 当前状态：{}{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), config.position, symbol))

    layout = go.Layout(title_text=symbol, title_font_size=30, autosize=True, margin=go.layout.Margin(l=10, r=1, b=10),
                       xaxis=dict(title_text="Candlesticck", type='category'),
                       xaxis2=dict(title_text="CCI", type='linear'),
                       yaxis=dict(title_text="<b>Price</b>", type="log"),
                       yaxis2=dict(title_text="<b>Volume</b>", anchor="x", overlaying="y", side="right"),
                       height=1000)

    # layout的参数超级多，因为它用一个字典可以集成所有图的所有格式
    # 这个函数里layout值得注意的是 type='category'，设置x轴的格式不是candlestick自带的datetime形式，
    # 因为如果用自带datetime格式总会显示出周末空格，这个我找了好久才解决周末空格问题。。。
    candle = go.Candlestick(x=data1["index"],
                            open=data1["open"], high=data1["high"],
                            low=data1["low"], close=data1["close"], increasing_line_color='#7bc0a3',
                            decreasing_line_color='#f6416c', name="Price")
    MA20 = go.Scatter(x=data1["index"], y=ma20_data, name="MA20", marker_color="red")
    CCI = go.Scatter(x=data1["index"], y=cii20_data,
                     name="CCI20", marker_color="blue", mode='lines')

    # 这里一定要设置yaxis=2, 确保成交量的y轴在右边，不和价格的y轴在一起
    data = [candle, MA20, CCI]
    fig = go.Figure(data, layout)
    return fig


def get_fig():
    limit = config.kline_limit
    symbol = config.symbol
    interval = config.interval
    Karry = np.array(str2float(Get_lines(limit, symbol, interval)), dtype="double")
    fig = can_vol(Karry, symbol=symbol)
    return fig
