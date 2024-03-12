from Wallets import Wallets
from DataQueue import Queue
import random
from datetime import datetime, timedelta
import time
import EraTxs as era
import syncswap as s
import zkswap as z
import asyncio

EXECUTOR_DELAY = 120

ERA_TX_LIST = {
    "kreatorland": era.kreatorland,
    "reactor_fusion": era.reactor_fusion,
    "zerolend": era.zerolend,
    "dmail": era.dmail,
    "eralend": era.eralend,
    "mint_ZKMarkets": era.mint_ZKMarkets,
    "mint_ZNS": era.mint_ZNS,
    "omnisea": era.omnisea,
    "xBank": era.xBank,
    "syncswap": s.syncswap,
    "zkswap": z.zkswap,
}

TX_WEIGHTS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 2]


def addToQueue(nextTx, address, new_date, param):
    q = Queue()
    q.insert(nextTx, address, new_date, param)


def randDay(start, end):
    start = start * 24
    end = end * 24
    current_date = datetime.now()
    hours_to_add = random.randint(start, end)
    new_date = current_date + timedelta(hours=hours_to_add)

    return new_date


# update with 'params' logic
def chooseNextTx(address):

    # choosing the Tx
    nextTx = random.choices(list(ERA_TX_LIST.keys()), TX_WEIGHTS, k=1)[0]

    # choosing the time of the Tx
    new_date = randDay(5, 10)

    param = ""

    if nextTx == "syncswap" or nextTx == "zkswap":
        swap_token = random.choices(["USDC", "USDT", "DAI"], [1, 1, 1], k=1)[0]
        param = "ETH " + swap_token

    addToQueue(nextTx, address, new_date, param)


async def runTx(address, txFunc, param):
    # w = Wallets()
    # priv_key = w.get_privKey()
    func = ERA_TX_LIST[txFunc]
    param = param.split()

    if func == s.syncswap:
        try:
            # First attempt
            print(f"{address}: Running {txFunc}({param[0]} {param[1]})...")
            await s.syncswap(address, param[0], param[1])
        except Exception as first_attempt_error:
            print(
                f"First attempt failed with error: {first_attempt_error}, trying one more time..."
            )
            try:
                # Second attempt
                time.sleep(20)
                await s.syncswap(address, param[0], param[1])
            except Exception as second_attempt_error:
                print(
                    f"Second attempt failed with error: {second_attempt_error}, handling error..."
                )
                # Handle the error here if the second attempt also fails

    elif func == z.zkswap:
        print(f"{address}: Running {txFunc}({param[0]} {param[1]})...")
        await z.zkswap(address, param[0], param[1])
    else:
        print(f"{address}: Running {txFunc}()...")
        await func(address)
    print(f"{address}: Completed {txFunc}")

    # chooseNextTx(address)


def add_tx_to_all():
    q = Queue()
    w = Wallets()
    wals = w.get_all_addresses()

    for addr in wals:
        if q.exists_for_address(addr) == False:
            chooseNextTx(addr)


def runBot():
    add_tx_to_all()

    q = Queue()
    nextTx = q.pop()
    while nextTx != None:
        add_tx_to_all()

        addr = nextTx[1]
        tx = nextTx[0]
        # Check if gas is below a certain threshhold
        date = nextTx[2]
        param = nextTx[3]
        if datetime.now() < date:
            print("Waiting for next Tx...")
            time.sleep(EXECUTOR_DELAY)
        else:
            asyncio.run(runTx(addr, tx, param))
            p = param.split()
            if tx == "syncswap" and p[0] == "ETH":
                addToQueue("syncswap", addr, randDay(5, 8), f"{p[1]} {p[0]}")
            elif tx == "zkswap" and p[0] == "ETH":
                addToQueue("zkswap", addr, randDay(0, 0), f"{p[1]} {p[0]}")
            else:
                chooseNextTx(addr)
            print("Waiting for next Tx...")
            time.sleep(EXECUTOR_DELAY)

        nextTx = q.pop()


# addToQueue(
#     "zkswap",
#     "0xBfF1759579b01efF642382AB813E4155e0d22D32",
#     datetime.now(),
#     "ETH USDT",
# )

# q = Queue()
# nextTx = q.pop()
# nextTx = nextTx[3]
# nextTx = nextTx.split("_")
# print(nextTx)
