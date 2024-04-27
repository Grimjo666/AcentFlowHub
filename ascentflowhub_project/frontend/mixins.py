from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.urls import reverse


class HttpResponseMixin:

    @staticmethod
    def set_cookie_and_redirect(cookie_dict: dict, redirect_path_name: str, httponly=True):
        """
        redirect_path_name - это имя, указанное в аргументе name, функции path, обычный путь эта функция не принимает
        """
        try:
            url = reverse(redirect_path_name)
            redirect_response = HttpResponseRedirect(url)
            for key, value in cookie_dict.items():
                redirect_response.set_cookie(key=key, value=value, httponly=httponly)

            return redirect_response

        except Exception as e:
            print(f"Error setting cookie: {str(e)}")

            return HttpResponseServerError("Внутрення ошибка сервера")

    @staticmethod
    def delete_cookie_and_redirect(cookie_arr,  redirect_path_name: str):
        try:
            url = reverse(redirect_path_name)
            redirect_response = HttpResponseRedirect(url)
            for key in cookie_arr:
                redirect_response.delete_cookie(key=key)

            return redirect_response

        except Exception as e:
            print(f"Error deleting cookie: {str(e)}")

            return HttpResponseServerError("Внутрення ошибка сервера")
