"""Conexión a Aiven ClickHouse: señal del wearable y métricas. [Pedro / María]"""
import clickhouse_connect

from .. import config

_client = None


def client():
    global _client
    if _client is None:
        _client = clickhouse_connect.get_client(host=config.CH_HOST, port=config.CH_PORT, username=config.CH_USER,
                                                password=config.CH_PASSWORD, secure=True)
    return _client


def insert_samples(rows: list[tuple]):
    """rows: (user_id, ts, hr, eda, acc, activation, confidence)"""
    client().insert("wearable_samples", rows,
                    column_names=["user_id", "ts", "hr", "eda", "acc", "activation", "confidence"])


def log_metric(user_id, endpoint, latency_ms, cost_eur, cached):
    client().insert("metrics", [(user_id, endpoint, int(latency_ms), float(cost_eur), int(cached))],
                    column_names=["user_id", "endpoint", "latency_ms", "cost_eur", "cached"])


def recent_window(user_id, minutes=2):
    """Media de los últimos minutos (para get_state). TODO: usar en services/state.py."""
    q = ("SELECT avg(hr), avg(eda), avg(acc) FROM wearable_samples "
         "WHERE user_id = {u:String} AND ts > now64() - INTERVAL {m:UInt32} MINUTE")
    return client().query(q, parameters={"u": user_id, "m": minutes}).first_row
