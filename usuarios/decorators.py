# usuarios/decorators.py
from django.shortcuts import redirect

def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect(f'/usuarios/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper
