def send_trc20(symbol: str, to_address: str, amount: float) -> str:
    # TODO: Use tronpy/python-tronlib, send TRC-20 token
    # Return blockchain txid
    return f"TRC20TXID{int(amount*10000)}"
