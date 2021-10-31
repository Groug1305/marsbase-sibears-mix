import requests
import operator
#from operator import itemgetter


#def get_info(): # список всех торгующихся пар с ценами и комиссиями
#    response = requests.get(url="https://yobit.net/api/3/info")
#
#    with open("info.txt", "w") as file:
#        file.write(response.text)
#
#    return response.text


def get_ticker(coin1="btc", coin2="usd"): # информация о паре 
    # response = requests.get(url="https://yobit.net/api/3/ticker/eth_btc-xrp_btccc?ignore_invalid=1")
    response = requests.get(url=f"https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1")
    with open("ticker.txt", "w") as file:
        file.write(response.text)

    return response


def get_depth(coin1="btc", coin2="usd", limit=150):# возвращает информацию о выставленных на продажу ордерах. лимит - глубина для вывода
    response = requests.get(url=f"https://yobit.net/api/3/depth/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")

    with open("depth.txt", "w") as file:
        file.write(response.text)

    bids = response.json()[f"{coin1}_usd"]["bids"]

    total_bids_amount = 0
    for item in bids:
        price = item[0]
        coin_amount = item[1]

        total_bids_amount += price * coin_amount

    return f"Total bids: {total_bids_amount} $"


def get_trades(coin1="btc", coin2="usd", limit=150, amount=0, flag = True): # совершенные сделки
    response = requests.get(url=f"https://yobit.net/api/3/trades/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")
    price = 0
    items = sorted(response.json()[f"{coin1}_{coin2}"], key=lambda x: x['price'])
    if flag == True:
        for i in range(len(items)-1,0,-1):
            if items[i]["type"] == "bid":
                if amount - items[i]['amount'] < 0:
                    price += items[i]['price'] * amount
                    amount = 0
                    print("We sell all coins")
                    break
                price += items[i]['price'] * items[i]['amount']
                amount -= items[i]['amount']
        if amount != 0:
            print("There was not enough supply on the market. We have", amount, " tokens left")                
    else:
        for i in range(len(items)):
            if items[i]["type"] == "ask":
                if amount - items[i]['amount'] < 0:
                    price += items[i]['price'] * amount
                    amount = 0
                    print("We bought all coins")
                    break
                price += items[i]['price'] * items[i]['amount']
                amount -= items[i]['amount']
        if amount != 0:
            print("There was not enough supply on the market. We need", amount, " tokens left")

    total_trade_ask = 0
    total_trade_bid = 0
                
    for item in response.json()[f"{coin1}_{coin2}"]:
        if item["type"] == "ask":
            total_trade_ask += item["price"] * item["amount"]
        else:
            total_trade_bid += item["price"] * item["amount"]

    print(f"[-] TOTAL {coin1} SELL: {round(total_trade_ask, 2)} $\n[+] TOTAL {coin1} BUY: {round(total_trade_bid, 2)} $")

    return price

def discount(real, avg, flag = True, flag1 = True):
    if flag1 == True:
        if flag==True:
            return (1 - real/avg + 0.05)
        else:
            return (real/avg + 0.2)
    else:
        if flag==True:
            return (1 - real/avg + 0.2)
        else:
            return (real/avg + 0.05)

def main():
    print('Coin1 -> coin2 or coin1 <- coin2?(enter 1 or 2)')
    if int(input()) == 1:
        flag1 = True
    else:
        flag1 = False
    print('Enter coin1')
    coin1 = input()
    print('Enter coin2')
    coin2 = input()
    limit = 2000
    print('Enter amount of coin1')
    amount = int(input())
    coin_info = get_ticker(coin1)
    print(coin_info.text)
    #print(get_depth(coin1))
    real_price = get_trades(coin1, coin2, limit, amount, flag1)
    if amount == 0:
        flag = True
    else:
        flag = False
    avg = coin_info.json()[f"{coin1}_usd"]["avg"]
    avg_price = amount*avg
    percents = discount(real_price, avg_price, flag, flag1)
    print("discount: ", percents*100, "%")
    print(f"Average price: {avg_price}")
    if flag1 == True:
        print(f"Average price with discount: {avg_price*(1-percents)}")
        print(f"Price of 1 token: {avg_price*(1-percents)/amount}")
    else:
        print(f"Average price with discount: {avg_price*(1+percents)}")
        print(f"Price of 1 token: {avg_price*(1+percents)/amount}")
    print(f"Real price: {real_price}")

if __name__ == '__main__':
    main()

