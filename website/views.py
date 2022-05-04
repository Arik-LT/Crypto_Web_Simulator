from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . models import Note, Crypto
from . import db
import json
from keys import api_key

import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

from website.models import Note

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')

        else:
            # pass user id of current_user for note
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': "BTC,ETH,XRP,LTC,BCH,BNB,USDT,EOS,BSV,XLM,ADA,TRX,LUNA,DOGE,DOT",
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    try:
        json = requests.get(url, params=parameters, headers=headers).json()
        coins = json["data"]
        coin_list = []
        for coin in coins:
            dic = {
                'name': coins[coin][0]['name'], 'symbol': coin, 'price': coins[coin][0]['quote']['USD']['price'],
                'percent_change_24h': coins[coin][0]['quote']['USD']['percent_change_24h'], 'percent_change_7d': coins[coin][0]['quote']['USD']['percent_change_7d'],
                'percent_change_30d': coins[coin][0]['quote']['USD']['percent_change_30d']
            }
            coin_list.append(dic)

        return render_template('home.html', coin_list=coin_list, user=current_user)

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return jsonify({"status": "fail", "mensaje": str(e)})


@views.route('/transactions', methods=['GET', 'POST'])
@login_required
def transaction():
    if request.method == 'POST':

        coin_from = request.form.get('coin_from')
        coin_to = request.form.get('coin_to')
        amount = request.form.get('amount')
        if 'price' in request.form:

            url = 'https://pro-api.coinmarketcap.com/v2/tools/price-conversion'

            parameters = {
                'amount': amount,
                'symbol': coin_from,
                'convert': coin_to
            }

            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': api_key,
            }
            try:
                global price
                json = requests.get(url, params=parameters,
                                    headers=headers).json()
                price = json['data'][0]['quote'][f'{coin_to}']['price']
                price = round(float(price), 5)

                return render_template('transactions.html', user=current_user, price=price,
                                       coin_to=coin_to, amount=amount, coin_from=coin_from)
            except:

                pass

        if 'submit' in request.form:
            # pass user id of current_user for note
            new_transaction = Crypto(coin_sold=coin_from, amount_sold=amount,
                                     coin_bought=coin_to, amount_bought=price,
                                     user_id=current_user.id)
            db.session.add(new_transaction)
            db.session.commit()
            flash('Transaction Added', category='success')

    return render_template('transactions.html', user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:  # check if current user id matches the note id
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
