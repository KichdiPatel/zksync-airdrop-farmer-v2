import json
from datetime import datetime

from eth_abi import abi
from web3 import AsyncHTTPProvider, AsyncWeb3

from helpers import approve, get_tx_data, getBalance, submitTx
from Wallets import Wallets

#    "MAV": "0x787c09494Ec8Bcb24DcAf8659E7d5D69979eE508",

TOKENS = {
    "ETH": "0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91",
    "USDC": "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4",
    "USDT": "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C",
    "DAI": "0x4B9eb6c0b6ea15176BBF62841C6B2A8a398cb656",
}

ROUTER = "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295"
CLASSIC_POOL = "0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb"

web3 = AsyncWeb3(AsyncHTTPProvider("https://mainnet.era.zksync.io"))

SLIPPAGE = 1


async def get_pool(from_token, to_token):
    # open ABI file
    with open(
        "./ABIs/syncswap/syncswap_classicPool.json", "r", encoding="utf-8"
    ) as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(address=CLASSIC_POOL, abi=abi)

    pool_address = await contract.functions.getPool(
        web3.to_checksum_address(TOKENS[from_token]),
        web3.to_checksum_address(TOKENS[to_token]),
    ).call()

    # print(pool_address)
    return pool_address


async def get_min_amt(pool_address, token, slippage, address, amount):
    # open ABI file
    with open("./ABIs/syncswap/syncswap_pool.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    contract = web3.eth.contract(pool_address, abi=abi)

    token_addr = TOKENS[token]
    address = web3.to_checksum_address(address)
    # balance = int(await web3.eth.get_balance(address) * 0.9)

    amt = await contract.functions.getAmountOut(token_addr, amount, address).call()

    return int(amt - (amt / 100 * slippage))


async def syncswap(address, from_token, to_token):
    # get private key
    w = Wallets()
    privKey = w.get_privKey(address)

    # establish contract addresses and any need variables
    from_token_addr = TOKENS[from_token]
    to_token_addr = TOKENS[to_token]

    wal_bal = int(await web3.eth.get_balance(address) * 0.8)

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


# asyncio.run(syncswap("0x...", "USDC", "ETH"))
