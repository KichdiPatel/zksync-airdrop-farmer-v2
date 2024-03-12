from web3 import AsyncWeb3, AsyncHTTPProvider
from Wallets import Wallets
from helpers import submitTx, get_tx_data, rand_string, approve, getBalance
import json
import asyncio
from eth_abi import abi
import time
from datetime import datetime, timedelta


TOKENS = {
    "ETH": "0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91",  # 0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91
    "USDC": "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4",
    "USDT": "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C",
    "DAI": "0x4B9eb6c0b6ea15176BBF62841C6B2A8a398cb656",
}

ROUTER = "0x18381c0f738146Fb694DE18D1106BdE2BE040Fa4"

web3 = AsyncWeb3(AsyncHTTPProvider("https://mainnet.era.zksync.io"))

SLIPPAGE = 1


async def get_min_amt(from_token, to_token, slippage, amount):
    # open ABI file
    with open("./ABIs/zkswap.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    contract = web3.eth.contract(ROUTER, abi=abi)

    min_amount_out = await contract.functions.getAmountsOut(
        amount,
        [
            web3.to_checksum_address(from_token),
            web3.to_checksum_address(to_token),
        ],
    ).call()

    return int(min_amount_out[1] - (min_amount_out[1] / 100 * slippage))


async def zkswap(address, from_token, to_token):
    # get private key
    w = Wallets()
    privKey = w.get_privKey(address)

    # establish contract addresses and any need variables
    from_token_addr = web3.to_checksum_address(TOKENS[from_token])
    to_token_addr = web3.to_checksum_address(TOKENS[to_token])

    wal_bal = int(await web3.eth.get_balance(address) * 0.8)

    # get deadline for swap
    deadline = int(datetime.now().timestamp()) + 1800

    # open ABI file
    with open("./ABIs/zkswap.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    contract = web3.eth.contract(ROUTER, abi=abi)

    if from_token == "ETH":
        tx_data = await get_tx_data(address, wal_bal)

        min_amount_out = await get_min_amt(
            from_token_addr, to_token_addr, SLIPPAGE, wal_bal
        )

        transaction = await contract.functions.swapExactETHForTokens(
            min_amount_out,
            [
                from_token_addr,
                to_token_addr,
            ],
            address,
            deadline,
        ).build_transaction(tx_data)

    else:
        amount_wei = await getBalance(address, from_token_addr)

        await approve(
            address,
            amount_wei,
            from_token_addr,
            web3.to_checksum_address(ROUTER),
        )

        tx_data = await get_tx_data(address, 0)

        min_amount_out = await get_min_amt(
            from_token_addr, to_token_addr, SLIPPAGE, amount_wei
        )

        transaction = await contract.functions.swapExactTokensForETH(
            amount_wei,
            min_amount_out,
            [
                web3.to_checksum_address(from_token_addr),
                web3.to_checksum_address(to_token_addr),
            ],
            address,
            deadline,
        ).build_transaction(tx_data)

    receipt = await submitTx(transaction, privKey)

    return True


# asyncio.run(zkswap("0xBd67F84758f8A873b81b247bd53866106ECf205f", "USDT", "ETH"))
