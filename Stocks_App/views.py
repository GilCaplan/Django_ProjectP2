from django.shortcuts import render, redirect
from .models import Transactions, Stock, Buying, Company, Investor
from django.db import connection
from django import forms
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


class BuyStockForm(forms.Form):
    ID = forms.IntegerField()
    Company = forms.CharField()
    BQuantity = forms.IntegerField()

def Buy_Stocks(request):
    if request.method == 'POST':
        form = BuyStockForm(request.POST)
        if form.is_valid():
            ID = form.cleaned_data['ID']
            Company = form.cleaned_data['Company']
            BQuantity = form.cleaned_data['BQuantity']

            investor = Investor.objects.get(pk=ID)
            company = Company.objects.get(pk=Company)
            stock_object = Stock.objects.latest('tdate')

            if investor.amount < stock_object.price * BQuantity:
                error_message = "Not enough founds"
                return render(request, 'buy_stocks.html', {'form':form, 'error_message': error_message})
            if Buying.objects.filter(ID=ID, Company=Company, date=stock_object.date).exists():
                error_message = "Investor cannot make multiple purchases for the same company on the same day"
                return render(request, 'buy_stocks.html', {'form':form, 'error_message': error_message})

            investor.amount -= stock_object.price *BQuantity
            investor.save()

            Buying.objects.create(ID=ID, Company=Company, BQuantity=BQuantity)

            return render(request, 'buy_stocks.html', {'form': form, 'success_message': 'Purchased Successfully'})

    else:
        form = BuyStockForm()

    return render(request, 'buy_stocks.html', {'form': form})


def Query_results(request):
    with connection.cursor () as cursor:
        with open('view_queries.sql', 'r') as sql_file:
            view_creation_commands = sql_file.read()

        cursor.execute(view_creation_commands)

        #Query a
        cursor.execute("""
            SELECT Investor.Name AS Investor_Name, ROUND(SUM(Buying.BQuantity * Stock.Price), 3) AS Total_Amount
            FROM Buying
            JOIN Company ON Buying.Symbol = Company.Symbol
            JOIN Investor ON Buying.ID = Investor.ID
            JOIN Stock ON Buying.Symbol = Stock.Symbol AND Buying.tDate = Stock.tDate
            JOIN (
                SELECT Buying.ID, Buying.tDate
                FROM Buying
                JOIN Company ON Buying.Symbol = Company.Symbol
                GROUP BY Buying.ID, Buying.tDate
                HAVING COUNT(DISTINCT Company.Sector) >= 6
            ) AS DiverseInvestors ON Buying.ID = DiverseInvestors.ID AND Buying.tDate = DiverseInvestors.tDate
            GROUP BY Investor.ID, Investor.Name
            ORDER BY Total_Amount DESC;
        """)
        query_result_a = dictfetchall(cursor)

        #Query b
        cursor.execute("""
            SELECT popQuantity.Symbol AS Symbol, popQuantity.ID, Investor.Name as Name, popQuantity.quantity as Quantity
            FROM popQuantity, Investor
            WHERE popQuantity.ID = Investor.ID AND InvestorRank = 1
            ORDER BY popQuantity.Symbol
        """)

        query_result_b = dictfetchall(cursor)

        #Query c
        cursor.execute("""
            SELECT Company.Symbol, COUNT(DISTINCT Buying.ID) AS distinct_id_count
            FROM Company, Stock st1, Stock st2, Buying
            WHERE Company.Symbol = st1.Symbol AND Company.Symbol = st2.Symbol
            AND Buying.Symbol = Company.Symbol AND Buying.tDate = (SELECT MIN (tDate) FROM StockDays)
            AND st1.tDate = (SELECT MIN(tDate) FROM StockDays) AND st2.tDate = (SELECT MAX(tDate) FROM StockDays)
            AND st1.Price * 0.06 < st2.Price
            GROUP BY Company.Symbol
            ORDER BY Company.Symbol
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

