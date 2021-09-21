import urllib.parse


# tutaj umieszczamy funkcje pomocnicze


# zwraca parametr GET umożliwiający powrót do strony
def get_current_page_back_url(request):
    back = request.META.get('QUERY_STRING')
    if back:
        back = f"{request.path}?{back}"
    else:
        back = f"{request.path}"
    return f"?back={urllib.parse.quote(back, safe='')}" if back else ""


# zwraca to samo, co funkcja get_current_page_back_url, tylko dane powrotu nie pobiera z requesta, a dostaje w
# parametrze
def get_back_url(text):
    return f"?back={urllib.parse.quote(text, safe='')}" if text else ""
