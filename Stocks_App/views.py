from django.shortcuts import render, redirect
from .models import Transactions, Stock, Buying, Company, Investor
from django.db import connection
from django import forms
from django.db.models import Max

# Create your views here.


def index(request):
    return render(request, 'index.html')


def errorPage(request):
    return render(request, 'errorPage.html')


def Add_Transaction(request):
    input_ID = request.POST.get('id')
    tsum = request.POST.get('transactionSum')
    try:
        tsum = int(tsum)
        flag = tsum <= 0
    except (ValueError, TypeError):
        # Handle the case where the input is not a valid integer or is None
        flag = False


    if input_ID is not None and not Transactions.objects.filter(id=input_ID).exists() or flag:
        return render(request, 'errorPage.html')  # Create a template for id_exists_error.html
    if input_ID is not None:
        transaction = Transactions()
        transaction.id_id = input_ID
        transaction.tamount = tsum
        transaction.tdate = Stock.objects.order_by('-tdate').first().tdate
        transaction.save()

    recent_transactions = Transactions.objects.order_by('-tdate')[:10]
    return render(request, 'Add_Transaction.html', {'recent_transactions': recent_transactions})


def Buy_Stocks(request):
    ID = request.POST.get('id')
    symbol = request.POST.get('company')
    BQuantity = request.POST.get('quantity')
    action = Buying.objects.order_by('-tdate')[:10]

    if ID is None or Company is None or BQuantity is None or not Investor.objects.filter(id=ID).exists() or not Company.objects.filter(symbol=symbol).exists() or int(BQuantity) <= 0:
        return render(request, 'buy_stocks.html', {'recent_transactions': action})
    company = Company.objects.get(pk=symbol)
    date = Stock.objects.order_by('-tdate').first().tdate
    try:
        stock = Stock.objects.get(symbol=company.symbol, tdate=date)
        price = stock.price
    except Stock.DoesNotExist:
        price = 0
    if Buying.objects.filter(id=ID, symbol=symbol, tdate=date).exists():
        error_message = "Investor cannot make multiple purchases for the same company on the same day"
        return render(request, 'buy_stocks.html', {'error_message': error_message, 'recent_transactions': action})
    investor = Investor._default_manager.get(id=ID)
    investor.amount = price * int(BQuantity)
    investor.save()

    purchase = Buying()
    purchase.bquantity = BQuantity
    purchase.id = investor
    purchase.pk = Stock.objects.get(symbol=company.symbol, tdate=date).pk
    purchase.tdate_id = date
    purchase.symbol_id = company

    purchase.symbol = Stock(symbol=Company.objects.get(pk=symbol))
    purchase.save()
    return render(request, 'buy_stocks.html', {'recent_transactions': action})

def Query_results(request):
    with connection.cursor () as cursor:
        with open('view_queries.sql', 'r') as sql_file:
            view_creation_commands = sql_file.read()

        cursor.execute(view_creation_commands)

        #Query a
        cursor.execute("""
            SELECT VarInv.Name, ROUND(SUM(Buying.BQuantity * Stock.Price), 3) AS spent
            FROM VarInv, Buying, Stock, Investor
            WHERE VarInv.Name = Investor.Name AND Investor.ID = Buying.ID
            AND Stock.Symbol = Buying.Symbol
            GROUP BY VarInv.Name
            ORDER BY spent DESC;
        """)
        query_result_a = dictfetchall(cursor)

        #Query b
        cursor.execute("""
        SELECT popQuantity.Symbol AS Symbol, Investor.Name as Name, popQuantity.quantity as Quantity
        FROM popQuantity, Investor
        WHERE popQuantity.ID = Investor.ID AND InvestorRank = 1
        ORDER BY popQuantity.Symbol
        """)

        query_result_b = dictfetchall(cursor)

        #Query c
        cursor.execute("""
            SELECT Company.Symbol AS Symbol, COUNT(DISTINCT Buying.ID) as BuyersNumber
            FROM Company
            JOIN Stock st1 ON Company.Symbol = st1.Symbol AND st1.tDate = (SELECT MIN(tDate) FROM StockDays)
            JOIN Stock st2 ON Company.Symbol = st2.Symbol AND st2.tDate = (SELECT MAX(tDate) FROM StockDays)
            LEFT JOIN Buying ON Buying.Symbol = Company.Symbol AND Buying.tDate = (SELECT MIN(tDate) FROM StockDays)
            WHERE st1.Price * 1.06 < st2.Price
            GROUP BY Company.Symbol
            ORDER BY Company.Symbol;
        """)

        query_result_c = dictfetchall(cursor)

    return render(request, 'Query_results.html', {
        'query_result_a': query_result_a,
        'query_result_b': query_result_b,
        'query_result_c': query_result_c,
    })


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

