def send_btc(to_address: str, amount: float) -> str:
    # TODO: Use bit library, send BTC
    # Return blockchain txid
    return f"BTCTXID{int(amount*100000)}"
