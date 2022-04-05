""" PUMP USING THE TELEGRAM API """

from threading import Thread
from config import kc_client, tel_client
from kucoin.client import Client
from telethon import events
from rsrcs.useful_funcs import extract_coin_name, time_notification
from rsrcs.coin_lib_pumps import sell_on_target, keyboard_sell

# ESSENTIAL TUNABLE PARAMETERS!
CHANNEL_NAME = 'kucoin_pump_group'  # kucoin_pumps OR MonacoPumpGroup OR kucoin_pump_group

COIN_AMOUNT = '10000000'  # coin amount to buy. Set this a high value to buy all of your current USDT
COIN_PAIRING = 'USDT'  # type of pairing used for listing. either USDT or BTC

# NON-ESSENTIAL
TARGET_SELL_PERCENTAGE = 100


def tel_main(sell_target=False):
    @tel_client.on(events.NewMessage(chats=CHANNEL_NAME))
    async def my_event_handler(event):
        print(event.raw_text)

        c_name = extract_coin_name(event.raw_text, pairing_type=COIN_PAIRING)
        order = kc_client.create_market_order(c_name + f'-{COIN_PAIRING}', Client.SIDE_BUY, size=COIN_AMOUNT)
        entry_price = kc_client.get_fiat_prices(symbol=c_name)[c_name]  # or take from bid?
        print(f"{order} --- {entry_price}")

        Thread(target=time_notification, args=[6]).start()  # starting a thread which prints time elapsed every n secs

        ord_bk_fa = kc_client.get_order_book(c_name + f'-{COIN_PAIRING}')['bids'][0]  # order book first order
        num_decimals_price = ord_bk_fa[0][::-1].find('.')
        num_decimals_amount = ord_bk_fa[1][::-1].find('.')

        deal_amount = f'%.{num_decimals_amount}f' % (float(kc_client.get_order(order['orderId'])['dealSize']) * 0.998)
        # multiply by 0.999 to make sure we have enough balance to sell!
        keyboard_sell(coin_name=c_name,
                      coin_amount=deal_amount,
                      pairing_type=COIN_PAIRING)  # enable keypress sell option. "pg up" for market and "pg down" for limit

        if sell_target:
            target_price = f'%.{num_decimals_price}f' % (float(entry_price) * ((TARGET_SELL_PERCENTAGE / 100) + 1))
            # the '%.2f' % is to limit decimals!
            sell_on_target(coin_name=c_name, target_price=target_price, coin_amount=deal_amount, time_to_check=0.8,
                           pairing_type=COIN_PAIRING)

    tel_client.start()
    tel_client.run_until_disconnected()


if __name__ == "__main__":
    tel_main(sell_target=False)