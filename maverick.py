from web3 import AsyncWeb3, AsyncHTTPProvider
from Wallets import Wallets
from helpers import submitTx, get_tx_data, rand_string, approve, getBalance
import json
import asyncio
from eth_abi import abi
import time
from datetime import datetime, timedelta


TOKENS = {
    "ETH": "0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91",
    "USDC": "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4",
    "USDT": "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C",
}

POOLS = {
    "USDC": "0x41C8cf74c27554A8972d3bf3D2BD4a14D8B604AB",
    "USDT": "0xC0622ACb4e15744A83Ecb64f661B1A119E2d11bf",
}

web3 = AsyncWeb3(AsyncHTTPProvider("https://mainnet.era.zksync.io"))

ROUTER = "0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4"
CLASSIC_POOL = "0x2C1a605f843A2E18b7d7772f0Ce23c236acCF7f5"
POOL_INFO = web3.to_checksum_address("0x57D47F505EdaA8Ae1eFD807A860A79A28bE06449")


SLIPPAGE = 5


async def get_pool(from_token, to_token):
    if from_token == "USDC" or to_token == "USDC":
        return POOLS["USDC"]
    elif from_token == "USDT" or to_token == "USDT":
        return POOLS["USDT"]


async def get_min_amt(pool_address, token_a_in, slippage, amt):
    # open ABI file
    with open("./ABIs/maverick/maverick_poolinfo.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    contract = web3.eth.contract(POOL_INFO, abi=abi)

    # address = web3.to_checksum_address(address)

    amount = await contract.functions.calculateSwap(
        web3.to_checksum_address(POOLS["USDC"]),
        amt,
        token_a_in,
        True,
        0,
    ).call()

    return int(amount - (amount / 100 * slippage))


async def syncswap(address, from_token, to_token):
    # get private key
    w = Wallets()
    privKey = w.get_privKey(address)

    # establish contract addresses and any need variables
    from_token_addr = TOKENS[from_token]
    to_token_addr = TOKENS[to_token]

    wal_bal = int(await web3.eth.get_balance(address) * 0.9)

    swap_pool = await get_pool(from_token, to_token)

    # as long as a swap_pool exists, try the swap
    if swap_pool == "0x0000000000000000000000000000000000000000":
        print("No swap path found")
    else:
        tx_data = await get_tx_data(address, 0)

        # adjust transaction data depending on the token we are swapping from
        if from_token == "ETH":
            tx_data.update({"value": wal_bal})
            amount_wei = wal_bal
        else:
            amount_wei = await getBalance(address, from_token_addr)

            await approve(
                address,
                amount_wei,
                from_token_addr,
                web3.to_checksum_address(ROUTER),
            )

        # get the min amount out - required for swap
        min_amount_out = await get_min_amt(
            swap_pool, from_token, SLIPPAGE, address, amount_wei
        )  # hardcoded the splippage value

        # establish steps and paths
        steps = [
            {
                "pool": swap_pool,
                "data": abi.encode(
                    ["address", "address", "uint8"], [from_token_addr, address, 1]
                ),
                "callback": "0x0000000000000000000000000000000000000000",
                "callbackData": "0x",
            }
        ]

        paths = [
            {
                "steps": steps,
                "tokenIn": (
                    "0x0000000000000000000000000000000000000000"
                    if from_token == "ETH"
                    else from_token_addr
                ),
                "amountIn": amount_wei,
            }
        ]

        # get deadline for swap
        # deadline = int(time.time()) + 1000000
        deadline = int(datetime.now().timestamp()) + 1800

        # get swap abi
        with open(
            "./ABIs/syncswap/syncswap_router.json", "r", encoding="utf-8"
        ) as file:
            swap_abi = json.load(file)

        # create contract object
        swap_contract = web3.eth.contract(address=ROUTER, abi=swap_abi)

        # create swap
        tx = await swap_contract.functions.swap(
            paths, min_amount_out, deadline
        ).build_transaction(tx_data)

        # # submit the Tx
        # # signed_txn = web3.eth.account.sign_transaction(tx, privKey)
        # # tx_hash = await web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        # # print(tx_hash)
        receipt = await submitTx(tx, privKey)

    # return True if successful
    return True


asyncio.run(get_min_amt(POOLS["USDC"], False, 5, 50000000000000000))
