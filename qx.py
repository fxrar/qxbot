from rich import print, print_json
import undetected_chromedriver as uc
import websocket

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
# from flask import Flask, request, jsonify

import requests
import json
import time
import yaml
import websocket
import json
import threading

STRATEGIES = {
    "martingale": {
        "multiply_on_loss": 2.25,
        "reset_on_win": True,
        "stop_on_profit": 20,
        "stop_on_loss": 15,
        "stop_on_trades": 50,
    },
}

SELECTED_STRATEGY = STRATEGIES["martingale"]
STARTING_AMOUNT = 5

email = "1"
password = "1"



def save_to_json(data, filename="trade_results.json"):
    try:
        # Try reading existing data
        with open(filename, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:  # If the file contains invalid JSON, reset to an empty list
                existing_data = []
    except FileNotFoundError:  # If file not found, initialize empty list
        existing_data = []

    # Append new data to the existing data
    existing_data.append(data)

    # Write updated data back to the file
    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=4)



class Quotex:
    
    def __init__(
        self,
        laravel_session: str,
        cf_clearance: str = None,
        __cf_bm: str = None,
        demo: bool = True,
    ) -> None: 
        global email, password
        self.demo = demo
        
        """
        # Session Validation
        self.profile = requests.get(
            "https://qxbroker.com/api/v1/user/profile",
            cookies={
                "lang": "en",
                "laravel_session": laravel_session,
            },
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
            },
        )

        if "<!DOCTYPE html>" in self.profile.text:
            self.print_error("Invalid session token passed or session expired.")
        else:
            self.profile = self.profile.text

        self.print_info("Logged in.")
        print_json(self.profile)
        """
        self.selected_stock_name = None
        # Open the selenium page to trade.
        chromeOptions = uc.ChromeOptions()
        chromeOptions.add_argument("--mute-audio")
        chromeOptions.add_argument('--ignore-certificate-errors')

        # chromeOptions.headless = True
        # cloudflare detects it idk why

        self.driver = uc.Chrome(options=chromeOptions)


        if demo:
            self.driver.get("https://qxbroker.com/en/demo-trade")
            self.add_cookies(laravel_session, cf_clearance, __cf_bm)
            self.driver.get("https://qxbroker.com/en/demo-trade")
            # Input email and password


            # Locate the email input box and type the email
            email_input = self.driver.find_element("css selector", "#tab-1 > form > div:nth-child(2) > input")
            email_input.send_keys(email)

            # Locate the password input box and type the password
            password_input = self.driver.find_element("css selector", "#tab-1 > form > div:nth-child(3) > input")
            password_input.send_keys(password)

            # Locate the sign-in button and click it
            sign_in_button = self.driver.find_element("css selector", "#tab-1 > form > button")
            sign_in_button.click()
           
            time.sleep(10)
            self.driver.get("https://qxbroker.com/en/demo-trade")




            if self.driver.title == "Just a moment...":
                self.print_info("Cloudflare Detected")
                was_cloudflare_solved = self.cloudflare_detected_solve()
            else:
                self.quotex_full_load_wait()


                
        else:
            self.driver.get("https://qxbroker.com/en/trade")
            self.add_cookies(laravel_session, cf_clearance, __cf_bm)
            self.driver.get("https://qxbroker.com/en/trade")
            # Input email and password
            

            # Locate the email input box and type the email
            email_input = self.driver.find_element("css selector", "#tab-1 > form > div:nth-child(2) > input")
            email_input.send_keys(email)

            # Locate the password input box and type the password
            password_input = self.driver.find_element("css selector", "#tab-1 > form > div:nth-child(3) > input")
            password_input.send_keys(password)

            # Locate the sign-in button and click it
            sign_in_button = self.driver.find_element("css selector", "#tab-1 > form > button")
            sign_in_button.click()
           





            if self.driver.title == "Just a moment...":
                self.print_info("Cloudflare Detected")
                was_cloudflare_solved = self.cloudflare_detected_solve()
            else:
                self.quotex_full_load_wait()           

        

    def stop(self):
        
            self.trading_active = False
            self.driver.quit()  # Close the Selenium driver
            print("Trading stopped and driver closed.")
       


    def get_balance(self) -> float:
        """
        Gets the current balance of the Quotex account.
        Returns:
            float: The current balance of the Quotex account.
        """
        try:
            balance = self.driver.find_element(
                By.CLASS_NAME, "usermenu__info-balance"
            ).text.replace("$", "").replace(",", "")
            return float(balance)
        except:
            self.print_error("Failed to fetch the balance.")
            return 0

    def place_trade(self, trade_time: int, amount: int, signal: bool) -> dict:

        global mx
        trade_start_time = time.time()
        balanceBeforeTrade = self.get_balance()
        # Set the trade time.

        if signal == True:
            self.print_info(
                f"Placing a [bold green]UP[/bold green] trade with time [bold yellow]{trade_time}sec[/bold yellow] and amount [bold yellow]{amount}$[/bold yellow]"
            )
        else:
            self.print_info(
                f"Placing a [bold red]DOWN[/bold red] trade with time [bold yellow]{trade_time}sec[/bold yellow] and amount [bold yellow]{amount}$[/bold yellow]"
            )

        time_label = self.driver.find_element(
            By.CSS_SELECTOR,
            "#root > div > div.page.app__page > main > div.page__sidebar > div.sidebar-section.sidebar-section--dark.sidebar-section--large > div > div.section-deal__form > div.section-deal__time.section-deal__input-black > label > span.input-control__label",
        )
        time_label.click()

        option_indices = {
            5: 1,
            10: 2,
            15: 3,
            30: 4,
            60: 5,
            120: 6,
            300: 7,
            600: 8,
            900: 9,
            1800: 10,
        }

        index = option_indices.get(trade_time)

        if index is not None:
            option = self.driver.find_element(
                By.CSS_SELECTOR,
                f"#root > div > div.page.app__page > main > div.page__sidebar > div.sidebar-section.sidebar-section--dark.sidebar-section--large > div > div.section-deal__form > div.section-deal__time.section-deal__input-black > label > div > div:nth-child({index})",
            )
            option.click()
        else:
            self.print_error("Invalid trade time provided.")

        self.driver.find_elements(By.CLASS_NAME, "input-control__input")[2].send_keys(
            Keys.CONTROL + "a"
        )

        self.driver.find_elements(By.CLASS_NAME, "input-control__input")[2].send_keys(
            round(amount)
        )

        if signal == True:
            self.driver.find_element(
                By.XPATH,
                '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[6]/div[1]',
            ).click()
        else:
            self.driver.find_element(
                By.XPATH,
                '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[6]/div[4]/button',
            ).click()

        self.print_info("Trade placed.")

        while True:
            time.sleep(0.2)
            result = self.check_for_win_or_lose()
            if result is not None:
                break

        if result == True:
            trade_end_time = time.time()
            profit_percentage = (
                (self.get_balance() - balanceBeforeTrade) / balanceBeforeTrade * 100
            )

            print(
                "[bold yellow]WIN[/bold yellow] Trade won. [conceal]LESGOO :)[/conceal]"
            )

           

            trade_details = {
                "result": "win",
                "timeTaken": round(trade_end_time - trade_start_time, 1),
                "tradeAmount": amount,
                "signal": "up" if signal else "down",
                "balanceBeforeTrade": balanceBeforeTrade,
                "balanceAfterTrade": self.get_balance(),
                "profitOrLoss": self.get_balance() - balanceBeforeTrade,
                "profitOrLossPercentage": round(profit_percentage, 3),  # x. 000
                "stock": self.selected_stock_name  # Add the stock pair name here
            }
            trade_details["mode"] = "demo" if self.demo else "live"
             
            if trade_details["result"] == "win" and (trade_details["profitOrLoss"] < 0):
                trade_details["profitOrLoss"] = trade_details["tradeAmount"] * 0.8

            save_to_json(trade_details)
            

            url = 'http://localhost:3000/updateTrade'

            try:
        
                response = requests.post(url, json={"trade": trade_details})

       
                if response.status_code == 200:
                    print('Trade updated successfully:', response.json())
                else:
                    print('Failed to update trade:', response.status_code, response.text)
    
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

            return trade_details
    
        else:
            trade_end_time = time.time()
            profit_percentage = (
                (self.get_balance() - balanceBeforeTrade) / balanceBeforeTrade * 100
            )

            print("[bold red]LOSS[/bold red] Trade lost. [conceal]RIP :([/conceal]")

            trade_details = {
                "result": "loss",
                "timeTaken": round(trade_end_time - trade_start_time, 1),
                "tradeAmount": amount,
                "signal": "up" if signal else "down",
                "balanceBeforeTrade": balanceBeforeTrade,
                "balanceAfterTrade": self.get_balance(),
                "profitOrLoss": self.get_balance() - balanceBeforeTrade,
                "profitOrLossPercentage": round(profit_percentage, 3),  # x. 000,
                "stock": self.selected_stock_name  # Add the selected stock name here

            }
            trade_details["mode"] = "demo" if self.demo else "live"

            
            save_to_json(trade_details)

            url = 'http://localhost:3000/updateTrade'

            try:
        
                response = requests.post(url, json={"trade": trade_details})

       
                if response.status_code == 200:
                    print('Trade updated successfully:', response.json())
                else:
                    print('Failed to update trade:', response.status_code, response.text)
    
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

            return trade_details

            
    def check_for_win_or_lose(self) -> bool:
        """
        Checks if the trade won or lost.
        Returns:
            bool: True if the trade won, False if the trade lost.
        """
        try:
            self.driver.find_element(
                By.CSS_SELECTOR, ".trades-notifications-item__total--up"
            )
            return True
        except:
            pass

        try:
            self.driver.find_element(
                By.CSS_SELECTOR, ".trades-notifications-item__total--down"
            )
            return False
        except:
            pass

        return None

    def quotex_full_load_wait(self):
        """
        Waits for the Quotex page to fully load by checking for the presence of the balance element.
        This method waits for up to 30 seconds for the element with the class name "usermenu__info-balance"
        to appear on the page. If the element is found within the timeout period, it logs a success message.
        If the element is not found within the timeout period, it logs a timeout error message.
        Raises:
            TimeoutException: If the balance element does not appear within 30 seconds.
        """
        # Wait for the balance element to appear.
        # FIXED timeout = 30 seconds
        self.print_info("Waiting for the page to load.")
        try:
            wait = WebDriverWait(self.driver, 30)
            wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "usermenu__info-balance")
                )
            )

            self.print_info("Quotex loaded.")
        except:
            self.print_error("Timeout error. Couldn't load the page.")

    def cloudflare_detected_solve(self) -> bool:
        if self.driver.title != "Just a moment...":
            return True

    def select_trade_pair(self, pair: str, minimum_return_percentage: int = 90) -> None:
        """
        Selects a trade pair based on the provided pair name and minimum return percentage.
        Args:
            pair (str): The name of the trade pair to select.
            minimum_return_percentage (int, optional): The minimum acceptable return percentage for the trade pair. Defaults to 90.
        Returns:
            None
        Raises:
            None
        Notes:
            - This method prints information about the selection process.
            - If the profit percentage of the selected trade pair is below the minimum return percentage, an error message is printed and the method returns without selecting the pair.
            - If the trade pair cannot be found, an error message is printed.
        """
        self.print_info(f"Selecting trade pair [bold yellow]{pair}[/bold yellow]")
        self.wait_for_element_to_appear_and_click("asset-select__button", By.CLASS_NAME)
        time.sleep(1)  # animation
        self.driver.find_element(By.CLASS_NAME, "asset-select__search-input").send_keys(
            pair
        )

        try:
            self.profit_percentage = int(
                self.driver.execute_script(
                    'return document.getElementsByClassName("assets-table__percent payoutOne text-center ")[0].childNodes[0].textContent'
                ).replace("%", "")
            )
            if self.profit_percentage < minimum_return_percentage:
                self.print_error(
                    f"Profit percentage is below [bold yellow]{minimum_return_percentage}%[/bold yellow]"
                )
                return
            else:
                time.sleep(0.5)
                self.driver.execute_script(
                    'document.getElementsByClassName("flags assets-table__flags flags")[0].childNodes[0].dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));'
                )

                # Wait until section-deal__name is the selected pair.
                try:
                    wait = WebDriverWait(self.driver, 5)
                    wait.until(
                        EC.text_to_be_present_in_element(
                            (By.CLASS_NAME, "section-deal__name"), pair.upper()
                        )
                    )
                except:
                    self.print_error(
                        f"Couldn't select the pair [bold yellow]{pair}[/bold yellow]"
                    )
                    return

                self.print_info(
                    f"Trade pair [bold yellow]{pair.upper()}[/bold yellow] selected, profit 1+ min: [bold yellow]{self.profit_percentage}%[/bold yellow]"
                )

                self.selected_stock_name = pair.upper()
        except:
            self.print_error(
                f"Couldn't find the pair [bold yellow]{pair}[/bold yellow]"
            )

    def add_cookies(self, laravel_session, cf_clearance, __cf_bm) -> None:
        """
        Adds cookies to the web driver session.

        This method adds three cookies to the web driver: 'laravel_session',
        'cf_clearance', and '__cf_bm'.

        Args:
            laravel_session (str): The value for the 'laravel_session' cookie.
            cf_clearance (str): The value for the 'cf_clearance' cookie.
            __cf_bm (str): The value for the '__cf_bm' cookie.

        Returns:
            None
        """
        self.driver.add_cookie({"name": "laravel_session", "value": laravel_session})
        self.driver.add_cookie({"name": "cf_clearance", "value": cf_clearance})
        self.driver.add_cookie({"name": "__cf_bm", "value": __cf_bm})

    def print_info(self, message: str) -> None:
    # HH:MM:SS
        current_time = time.strftime("%H:%M:%S", time.localtime())
        print(f"INFO [{current_time}] {message}")

    def print_error(self, message: str) -> None:
    # HH:MM:SS
        current_time = time.strftime("%H:%M:%S", time.localtime())
        print(f"ERROR [{current_time}] {message}")

    def wait_for_element_to_appear(self, element: str, by, timeout: int = 30) -> None:
        """
        Waits for a web element to appear on the page within a specified timeout.

        Args:
            element (str): The locator of the element to wait for.
            by: The method to locate the element (e.g., By.ID, By.XPATH).
            timeout (int, optional): The maximum time to wait for the element to appear. Defaults to 30 seconds.

        Raises:
            TimeoutException: If the element does not appear within the specified timeout.

        Returns:
            None
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, element)))
        except:
            self.print_error(f"Timeout error. Couldn't load find {element}.")

    def wait_for_element_to_appear_and_click(
        self, element: str, by: By, timeout: int = 30
    ) -> None:
        """
        Waits for a web element to appear on the page and clicks it.

        Args:
            element (str): The locator of the element to be found.
            by (By): The method to locate the element (e.g., By.ID, By.XPATH).
            timeout (int, optional): The maximum time to wait for the element to appear. Defaults to 30 seconds.

        Returns:
            None

        Raises:
            TimeoutException: If the element does not appear within the specified timeout.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            found = wait.until(EC.presence_of_element_located((by, element)))
            found.click()
        except:
            self.print_error(f"Timeout error. Couldn't load find {element}.")



qx = None
ws = None

#### Listen for trades. ####

TRADES_MADE = 0
PROFIT = 0
LOSS = 0
TRADES_WON = 0
TRADES_LOST = 0
TOTAL_TRADES = 0
ALL_TRADES = []

def check_stoppers():
    if TRADES_MADE >= SELECTED_STRATEGY["stop_on_trades"]:
        qx.print_info(f"Maximum trades [[bold yellow]{SELECTED_STRATEGY['stop_on_trades']}[/bold yellow]] reached. Stopping.")
        return True
    
    if PROFIT >= SELECTED_STRATEGY["stop_on_profit"]:
        qx.print_info(f"[green]Profit [[bold yellow]{SELECTED_STRATEGY['stop_on_profit']}[/bold yellow]] reached. Stopping[/green]")
        return True
    
    if LOSS >= SELECTED_STRATEGY["stop_on_loss"]:
        qx.print_info(f"[red]Loss [[bold yellow]{SELECTED_STRATEGY['stop_on_loss']}[/bold yellow]] reached. Stopping[/red]")
        return True
    
    return False

def on_message(ws, message):
    global TRADES_MADE, PROFIT, LOSS, TRADES_WON, TRADES_LOST, TOTAL_TRADES, ALL_TRADES

    message_json = json.loads(message)

    if message_json["action"] == "trade":
        qx.print_info("Placing Trade")
        
        # Check if trading should be stopped.
        if check_stoppers():
            ws.close()
            return
        
        qx.select_trade_pair(message_json["market"], 40)
        
        if TRADES_MADE == 0:
            amount_to_trade = STARTING_AMOUNT
        else:
            # Check if previous trade was a win.
            if ALL_TRADES[-1]["result"] == "win":
                if SELECTED_STRATEGY["reset_on_win"] == True:
                    qx.print_info("Resetting amount to trade because previous trade was a win.")
                    amount_to_trade = STARTING_AMOUNT
                else:
                    qx.print_info("Keeping the trade amount the same because reset on win is False.")
                    amount_to_trade = ALL_TRADES[-1]["tradeAmount"]
            else: # previous trade was a loss
                qx.print_info("Multiplying the trade amount because previous trade was a loss.")

                multiplier = float(SELECTED_STRATEGY["multiply_on_loss"])
                amount_to_trade = ALL_TRADES[-1]["tradeAmount"] * multiplier
    
        trade = qx.place_trade(
            message_json["trade_time"],
            amount_to_trade,
            True if message_json["signal"] == "buy" else False,
        )

        print_json(data=trade)
        
        ALL_TRADES.append(trade)
        
        TRADES_MADE += 1 # i forgot before money

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed ", close_msg)

def on_open(ws):
    qx.print_info("Successfully connected to WealthWize. Listening for trades.")
    qx.print_info(f"Balance: [bold yellow]{qx.get_balance()}$[/bold yellow]")

def start_ws():
    global ws
    ws = websocket.WebSocketApp(
        "wss://wize.money:4096",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    ws.run_forever()












email = "help@wize.lol"
password = "Veni Vedi Veci"
# Enter Your Own Paassword Here 

thread = threading.Thread(target=start_ws)
thread.start()


def get_balance():
    return qx.get_balance()






# if __name__ == '__main__':
    


qx = Quotex(
    "eyJpdiI6IjFJNHQvT0pJWEZnNnBSMkIxTTY1YUE9PSIsInZhbHVlIjoiSzRwbGtBR1Z6UXh1SDY1QWFjV2JrNUhHSFpyRmRoMDRpSko5WElSUUFPL2t3ajdWcEFlT2VlM1hDZU92ekh5UnhleXZzb1I4M0dPay9kOUs2Y1V5WUZQb0o2aGNWdmZ1QXNpK3grbk15WSs4aXhuaTFrZ0xFZTdFMzNEaEtSTy8iLCJtYWMiOiJkN2JiNjVjNGQxMTFmZmYxMjUxZDJjOWY3M2U4NjMxODI2ZjJhYThkMmNjNWQ1NjNjNmVhZjZmMjk3OTJhZjFkIiwidGFnIjoiIn0%3D",
    "SOxHMS0SDkXDviPJV_xadbfS5R77YkrjBt.8qhj68ho-1726734083-1.2.1.1-0lIZiWCEjPL048bS_jE_Lzwbrcpqg4KWJtO4jZXMPJZiA5f2leJDR068XV0u4ogDfctFuMNU2OlAuS07RRA8w_dIB9aTxoIC.HFhAbpVs15hAdpJd5lrDbsRTfYxxJHIdO1hKulgp7W3F_ZQMqafEE5D2_9GAt8YCQJfHEc_FJREgI_NQFtQQVfB4Qy0rl6smxuwEUy6OgWOs474z.mzUVozHlB2ONDefm.w0J_dj0yoSHi_0UG44PvyQgAhBH_F8qJR8ThjyV66ErFnSOeAQoyKKE4oIIylK1cgp9.3Prr.OcPGUTCOngwINY.a0N8QqJ2PDKNqA9UawR5JJHvyao77oiTpW64.yw6x02P77IoMtgZ5UiaCtInCOmVQJZMG",
    "kjSlfzFT96c6bjNuaJvVejnGYDeNxwoE9OocA83xulo-1726734081-1.0.1.1-C4Y070hF.EFIcFCdfElhWWIeYuDH6JWw4QKjJP6QjhaeV21HqeDrG9D.MRVvtHZ0ViTY8FuPNmvUNGtWArPpXA",
    demo=True)
