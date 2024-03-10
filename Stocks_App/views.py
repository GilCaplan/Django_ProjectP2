from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'index.html')


def Add_Transaction(request):
    return render(request, 'Add_Transaction.html')


def Buy_Stocks(request):
    return render(request, 'Buy_Stocks.html')


def Query_results(request):
    return render(request, 'Query_results.html')


