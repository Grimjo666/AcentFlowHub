from .models import UserSettings


class UserSiteSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        self.create_or_write_data(request)

        response = self.get_response(request)

        return response

    @staticmethod
    def create_or_write_data(request):
        """
        Создаём если нет экземпляр модели и записываем его в сессию
        :param request:
        :return:
        """
        user_settings = UserSettings.objects.filter(user=request.user)

        if not user_settings.exists():
            UserSettings(user=request.user).save()

        settings_dict = {
            'hide_subgoals': user_settings[0].hide_subgoals
        }

        request.session['user_site_settings'] = settings_dict

