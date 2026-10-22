"""Features de ventana de muñeca (WESAD / Empatica E4). [María] — TODO: pegar aquí la lógica del TFG."""


def window_features(bvp, eda, acc, fs_bvp=64, fs_eda=4, fs_acc=32) -> dict:
    """TODO(María): FC y RMSSD desde BVP (neurokit2.ppg_process), EDA tónica y nº de picos SCR (neurokit2.eda_process),
    |ACC| media. Devolver dict con nombres fijos (los usa train_state.py y estimate.py)."""
    raise NotImplementedError
