from web3 import Web3
import asyncio
from web3 import AsyncWeb3
from web3 import AsyncWeb3, AsyncHTTPProvider
import secrets
import string
import json
from Wallets import Wallets

web3 = AsyncWeb3(AsyncHTTPProvider("https://mainnet.era.zksync.io"))

w3 = Web3(Web3.HTTPProvider("https://mainnet.era.zksync.io"))


async def get_tx_data(address, value: int = 0):

    tx = {
        "chainId": await web3.eth.chain_id,
        "from": address,
        "value": value,
        "gasPrice": await web3.eth.gas_price,
        "nonce": await web3.eth.get_transaction_count(address, "latest"),
    }

    return tx


async def submitTx(tx, privKey):
    gas = await web3.eth.estimate_gas(tx)
    tx.update({"gas": gas})

    signed_txn = web3.eth.account.sign_transaction(tx, privKey)
    tx_hash = await web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt


def rand_string(len):
    characters = string.ascii_letters + string.digits
    rand_string = "".join(secrets.choice(characters) for i in range(len))
    return rand_string


async def check_allowance(address, token_address, contract_address) -> float:
    token_address = web3.to_checksum_address(token_address)
    contract_address = web3.to_checksum_address(contract_address)

    # open ABI file
    with open("./ABIs/ERC20.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    contract = web3.eth.contract(address=token_address, abi=abi)

    amount_approved = await contract.functions.allowance(
        address, contract_address
    ).call()
    # print(amount_approved)
    return amount_approved


async def approve(user_address, amount, token_address, contract_address):
    token_address = web3.to_checksum_address(token_address)
    contract_address = web3.to_checksum_address(contract_address)
    user_address = web3.to_checksum_address(user_address)

    w = Wallets()
    privKey = w.get_privKey(user_address)

    # open ABI file
    with open("./ABIs/ERC20.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    contract = web3.eth.contract(address=token_address, abi=abi)

    allowance_amount = await check_allowance(
        user_address, token_address, contract_address
    )
    # print(allowance_amount)

    if amount > allowance_amount or amount == 0:

        approve_amount = (
            2**128 if amount > allowance_amount else 0
        )  # amount - allowance_amount

        tx_data = await get_tx_data(user_address, 0)

        transaction = await contract.functions.approve(
            contract_address, approve_amount
        ).build_transaction(tx_data)

        receipt = await submitTx(transaction, privKey)

        await asyncio.sleep(20)


async def getBalance(address, token):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/ERC20.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(address=token, abi=abi)

    balance = await contract.functions.balanceOf(address).call()
    decimals = await contract.functions.decimals().call()
    # print(balance)
    return int(balance)  # int(balance / 10**decimals)


# asyncio.run(
#     approve(
#         "0x09F4E0028d76221CC714C2758c45480f75C76398",
#         10,
#         "0xd45ab0E1dc7F503Eb177949c2Fb2Ab772B4B6CFC",
#         web3.to_checksum_address("0x3f39129e54d2331926c1E4bf034e111cf471AA97"),
#     )
# )

# asyncio.run(
#     getBalance(
#         "0x09F4E0028d76221CC714C2758c45480f75C76398",
#         "0xd45ab0E1dc7F503Eb177949c2Fb2Ab772B4B6CFC",
#     )
# )
