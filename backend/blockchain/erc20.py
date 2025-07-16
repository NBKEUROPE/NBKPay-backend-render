def send_erc20(symbol: str, to_address: str, amount: float) -> str:
    # TODO: Use web3.py, load private key, estimate gas, send ERC-20 (USDT/USDC)
    # Return blockchain txid
    # For demo, return dummy txid
    return f"0xERC20TXID{int(amount*10000)}"
