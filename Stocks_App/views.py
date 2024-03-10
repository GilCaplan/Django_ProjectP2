from django.shortcuts import render
from .models import Transactions, Stock
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
    return render(request, 'Buy_Stocks.html')


def Query_results(request):
    return render(request, 'Query_results.html')


