from web3 import Web3
from web3 import AsyncWeb3, AsyncHTTPProvider
import json
from Wallets import Wallets
import asyncio
from datetime import datetime, timedelta
from helpers import submitTx, get_tx_data, rand_string
import random
from hashlib import sha256
import time


web3 = AsyncWeb3(AsyncHTTPProvider("https://mainnet.era.zksync.io"))


async def kreatorland(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/kreatorland.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0x9161c622D6A8FA99555e82201987CC2574e4335D", abi=abi
    )

    # create the transaction
    transaction = await contract.functions.mint("", 1, 0).build_transaction(
        await get_tx_data(address, 0)
    )

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def reactor_fusion(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/reactorFusion.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6", abi=abi
    )
    value = random.choices(
        [100000000000000, 200000000000000, 300000000000000], weights=[1, 1, 1], k=1
    )[0]

    # create the transaction
    transaction = await contract.functions.mint().build_transaction(
        await get_tx_data(address, value)
    )

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def zerolend(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/zerolend.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0x767b4A087c11d7581Ac95eaFfc1FeBFA26bad3d2", abi=abi
    )

    value = random.choices(
        [100000000000000, 200000000000000, 300000000000000], weights=[1, 1, 1], k=1
    )[0]

    # create the transaction
    transaction = await contract.functions.depositETH(
        address, address, 0
    ).build_transaction(await get_tx_data(address, value))

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def dmail(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/dmail.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0x981F198286E40F9979274E0876636E9144B8FB8E", abi=abi
    )

    email = sha256(str(1e11 * random.random()).encode()).hexdigest()
    theme = sha256(str(1e11 * random.random()).encode()).hexdigest()

    # create the transaction
    transaction = await contract.functions.send_mail(email, theme).build_transaction(
        await get_tx_data(address, 0)
    )

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def eralend(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # choose random amount to supply
    value = random.choices(
        [100000000000000, 200000000000000, 300000000000000], weights=[1, 1, 1], k=1
    )[0]

    # create the transaction
    transaction = {
        "chainId": await web3.eth.chain_id,
        "from": address,
        "to": web3.to_checksum_address("0x22D8b71599e14F20a49a397b88c1C878c86F5579"),
        "gasPrice": await web3.eth.gas_price,
        "nonce": await web3.eth.get_transaction_count(address),
        "value": value,
        "data": "0x1249c58b",
    }

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def mint_ZKMarkets(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/zkMarkets.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0xB7a6154CE5c181a68f6a15d8C2E8aCA55AE86c91", abi=abi
    )

    # create the transaction
    transaction = await contract.functions.mint("").build_transaction(
        await get_tx_data(address, 0)
    )

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def mint_ZNS(address):
    async def is_available(name):
        return await contract.functions.available(name).call()

    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/zns.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0xCBE2093030F485adAaf5b61deb4D9cA8ADEAE509", abi=abi
    )

    # get a random name
    rand_name = rand_string(30)

    while not await is_available(rand_name):
        rand_name = rand_string(30)

    transaction = await contract.functions.register(
        rand_name,
        address,
        1,
    ).build_transaction(await get_tx_data(address, 0))

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def omnisea(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # open ABI file
    with open("./ABIs/omnisea.json", "r", encoding="utf-8") as file:
        abi = json.load(file)

    # create contract object
    contract = web3.eth.contract(
        address="0x8d25e53D707433122f051D7977f98dC615cBEb87", abi=abi
    )
    value = random.choices(
        [100000000000000, 200000000000000, 300000000000000], weights=[1, 1, 1], k=1
    )[0]

    end_time = int(
        (datetime.now() + timedelta(days=random.randint(10, 20))).timestamp()
    )

    # create the transaction
    transaction = await contract.functions.create(
        (
            rand_string(10),  # name
            rand_string(5),  # symbol
            rand_string(30),  # uri
            rand_string(30),  # token uri
            random.randint(100, 1000),  # max supply
            False,  # isZeroIndexed
            random.randint(2, 10),  # royalty amount
            end_time,  # end time
            True,  # isEdition
            False,  # isSBT
            0,  # premintQuantity
        )
    ).build_transaction(await get_tx_data(address, 0))

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


async def xBank(address):
    w = Wallets()
    privKey = w.get_privKey(address)

    # choose random amount to supply
    value = random.choices(
        [100000000000000, 200000000000000, 300000000000000], weights=[1, 1, 1], k=1
    )[0]

    # create the transaction
    transaction = {
        "chainId": await web3.eth.chain_id,
        "from": address,
        "to": web3.to_checksum_address("0xE4622A57Ab8F4168b80015BBA28fA70fb64fa246"),
        "gasPrice": await web3.eth.gas_price,
        "nonce": await web3.eth.get_transaction_count(address),
        "value": value,
        "data": "0x1249c58b",
    }

    # submit the Tx
    receipt = await submitTx(transaction, privKey)

    # return True if successful
    return True


def chooseEraTx():
    ERA_TX_LIST = [
        kreatorland,
        reactor_fusion,
        zerolend,
        dmail,
        eralend,
        mint_ZKMarkets,
        mint_ZNS,
        omnisea,
        xBank,
    ]

    TX_WEIGHTS = [1, 1, 1, 1, 1, 1, 1, 1, 1]

    random.choices(ERA_TX_LIST, TX_WEIGHTS, k=1)[0]


# asyncio.run(ERA_TX_LIST[9]("0x09F4E0028d76221CC714C2758c45480f75C76398"))
