import okx.PublicData as PublicData
import okx.Account as Account

# Твои данные ключа blisada
api_key = "860da3e2-0ed8-400c-a0eb-44d2d3da321e"
secret_key = "0484BB44D177ACC799EF9DA179802C5D"
passphrase = "Innate37#"

# 0 — боевой режим (Live), 1 — демо-режим
flag = "0"

def test():
    print("Проверка подключения к OKX...")
    
    # Публичный API (проверка связи)
    pub_api = PublicData.PublicAPI(flag=flag)
    res = pub_api.get_instruments(instType="SPOT")
    print("Публичный запрос — код ответа:", res.get("code"))

    # Приватный API (проверка ключа)
    acc_api = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
    balance = acc_api.get_account_balance()
    print("Ответ баланса по ключу:", balance)

if __name__ == "__main__":
    test()