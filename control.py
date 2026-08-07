import okx.Account as Account
import okx.PublicData as PublicData

# Твои данные ключа blisada
api_key = "860da3e2-0ed8-400c-a0eb-44d2d3da321e"
secret_key = "0484BB44D177ACC799EF9DA179802C5D"
passphrase = "Innate37#"

# Флаг для реальной торговли/данных (0 — боевой режим / Live)
flag = "0" 

def test_connection():
    print("Проверка соединения с OKX...")
    
    # Инициализация клиента публичных данных (проверка связи без авторизации)
    public_api = PublicData.PublicAPI(flag=flag)
    result = public_api.get_instruments(instType="SPOT")
    
    if result.get("code") == "0":
        print(" Успешно! Биржа доступна, получены данные по спотовым инструментам.")
    else:
        print(f" Ошибка подключения: {result}")
        return

    # Инициализация клиентского аккаунта (проверка нашего API-ключа)
    account_api = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
    balance_result = account_api.get_account_balance()
    
    if balance_result.get("code") == "0":
        print(" Авторизация по API-ключу 'blisada' прошла успешно!")
        print("Баланс аккаунта получен:")
        print(balance_result)
    else:
        print(f" Ошибка авторизации: {balance_result}")

if __name__ == "__main__":
    test_connection()