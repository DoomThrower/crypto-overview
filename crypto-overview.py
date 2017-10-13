import requests
import json

import smtplib

wallet = 'change-me'

sender_gmail_account = 'change-me@gmail.com'
sender_gmail_password = 'change-me'
email_recipients = ['change@me-1.com', 'change@me-1.com']


class Overview:
    def __init__(self, wallet, cost_of_kWh_in_pln=0.55, rig_kilowatt_usage=1.050):
        self.wallet = wallet

        self.usd_to_pln_ratio = Overview._get_usd_to_pln_ratio()
        self.cost_of_kWh_in_pln = cost_of_kWh_in_pln
        self.rig_kilowatt_usage = rig_kilowatt_usage

        response = requests.get('https://api-zcash.flypool.org/miner/' + wallet + '/currentStats')
        self.json_data = json.loads(response.text)

        self.average_hash_rate = self.json_data['data']['averageHashrate']
        self.usd_per_min = self.json_data['data']['usdPerMin']
        self.btc_per_min = self.json_data['data']['btcPerMin']
        self.coins_per_min = self.json_data['data']['coinsPerMin']

    @staticmethod
    def _get_usd_to_pln_ratio():
        response = requests.get('http://api.fixer.io/latest?base=USD')
        return json.loads(response.text)['rates']['PLN']

    def __str__(self):
        output = ''
        output += 'CurrentStats for wallet: ' + self.wallet + '\n'
        output += 'Average HashRate: ' + str(self.average_hash_rate) + ' H/s\n'
        output += '\nIncome:\n'
        output += Overview._print_income('USD', self.usd_per_min)
        output += Overview._print_income('BTC', self.btc_per_min)
        output += Overview._print_income('ZEC', self.coins_per_min)
        output += Overview._print_income('PLN', self.usd_per_min * self.usd_to_pln_ratio)
        output += '\n'
        output += Overview._print_income('Clean PLN', self._clean_pln_income_per_min())
        return output

    @staticmethod
    def _print_income(name, base_per_min):
        output = ''
        output += '-' + name + ':\n'
        output += '\tPer min:\t\t' + str(base_per_min) + '\n'
        output += '\tPer hour:\t\t' + str(60 * base_per_min) + '\n'
        output += '\tPer day:\t\t' + str(24 * 60 * base_per_min) + '\n'
        output += '\tPer week:\t\t' + str(7 * 24 * 60 * base_per_min) + '\n'
        output += '\tPer 30 days:\t' + str(30 * 24 * 60 * base_per_min) + '\n'
        output += '\tPer 365 days:\t' + str(365 * 24 * 60 * base_per_min) + '\n'

        return output

    def _clean_pln_income_per_min(self):
        return self.usd_per_min * self.usd_to_pln_ratio - (self.cost_of_kWh_in_pln * self.rig_kilowatt_usage) / 60

    def send_mail(self):
        gmail_user = sender_gmail_account
        gmail_password = sender_gmail_password

        sent_from = gmail_user
        to = email_recipients
        subject = 'Crypto state'
        body = str(self)

        email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print 'Email sent!'


if __name__ == "__main__":
    overview = Overview(wallet=wallet)
    print overview
    overview.send_mail()
