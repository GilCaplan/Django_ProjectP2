from django.shortcuts import render
from .models import Transactions
# Create your views here.


def index(request):
    return render(request, 'index.html')


def errorPage(request):
    return render(request, 'errorPage.html')


def Add_Transaction(request):
    input_ID = request.POST.get('id')

    if not Transactions.objects.filter(ID=input_ID).exists():
        return render(request, 'errorPage.html')  # Create a template for id_exists_error.html

    # If the ID doesn't exist, create a new transaction
    transaction = Transactions()
    transaction.id = input_ID
    transaction.tamount = request.POST.get('transactionSum')
    transaction.save()

    recent_transactions = Transactions.objects.order_by('-tDate')[:10]
    return render(request, 'Add_Transaction.html', {'recent_transactions': recent_transactions})


def Buy_Stocks(request):
    return render(request, 'Buy_Stocks.html')


def Query_results(request):
    return render(request, 'Query_results.html')


