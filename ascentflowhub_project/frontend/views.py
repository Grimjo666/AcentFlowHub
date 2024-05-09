from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User

from frontend import forms
from .mixins import HttpResponseMixin
from .models import UserTraining, UserSettings, UserProfilePhoto
from api.models import LifeCategory, TreeGoals
from api.api_client import UserApiError, TreeGoalsAPI
from ascentflowhub_project.constants import BASE_LIFE_CATEGORY_DATA


def page_not_found(request):
    return render(request, 'frontend/page_not_found.html')


def index_page(request):
    return render(request, 'frontend/index.html')


def test_page(request):
    return render(request, 'frontend/test_page.html')


class LogoutView(View, HttpResponseMixin):
    domain = settings.DOMAIN_NAME

    def get(self, request):
        try:

            logout(request)
            messages.success(request, 'Вы вышли из системы')

        except Exception as e:

            messages.error(request, f'Произошла ошибка при выходе из системы: {e}')
            return redirect('index_page')

        else:
            return redirect('index_page')


class LoginPageView(View, HttpResponseMixin):
    template_name = 'frontend/login.html'
    domain = settings.DOMAIN_NAME

    def get(self, request, context=None):
        form = forms.UserAuthenticationForm()
        if not context:
            context = {
                'form': form
            }
        return render(request, self.template_name, context)

    def post(self, request):
        form = forms.UserAuthenticationForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                return redirect('index_page')

        return self.get(request, context={'form': form})


def registration_page(request):

    if request.method == 'POST':
        try:
            form = forms.RegistrationForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                User.objects.create_user(username=username, password=password, email=email)

                messages.success(request, 'Вы успешно зарегистрировались')

                return LoginPageView().post(request)

            else:
                raise ValueError('Форма: RegistrationForm не валидна')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('index_page')
    else:
        form = forms.RegistrationForm()
    return render(request, 'frontend/registration.html', context={'form': form})


class MyProgressPageView(View):
    template_name = 'frontend/my_progress.html'

    def get(self, request):
        try:
            life_category_list = LifeCategory.objects.filter(user=request.user)

            context = {
                'life_category_list': life_category_list,
                'modal_window': False,
                'life_category_form': forms.LifeCategoryForm
            }

            user_training = UserTraining.objects.filter(user=request.user.id)[0]

            # Получаем инфу о том, создавал ли пользователь сферы жизни
            already_created_categories = user_training.creating_base_categories
            if not already_created_categories:
                context['modal_window'] = True
                user_training.creating_base_categories = True
                user_training.save()

            return render(request, self.template_name, context=context)

        except Exception as e:
            messages.error(request, str(e))
            return redirect('index_page')

    def post(self, request):
        try:
            form_type = request.POST.get('form_type')

            #  Создание базовых сфер жизни
            if form_type == 'create_base_category_form' and request.POST.get('button') == 'create':

                self.create_base_life_categories(request.user)
                messages.success(request, 'Созданы базовые сферы жизни')

            #  Обработка формы изменения сфер жизни
            elif form_type == 'edit_categories_form':

                delete_category_id = request.POST.get('delete_category')
                if delete_category_id:
                    LifeCategory.objects.get(id=delete_category_id).delete()
                    messages.success(request, 'Сфера жизни удалена')

            # Обработка формы добавления новых сфер жизни
            if form_type == 'create_new_category_form':
                form = forms.LifeCategoryForm(request.POST)
                if form.is_valid():
                    LifeCategory(name=form.cleaned_data['name'],
                                 first_color=form.cleaned_data['first_color'],
                                 second_color=form.cleaned_data['second_color'],
                                 user=request.user).save()

                    messages.success(request, 'Сфера жизни добавлена')

            return redirect('my_progress_page')

        except Exception as e:
            messages.error(request, f'Произошла непредвиденная ошибка: {e}')
            return redirect('my_progress_page')

    @staticmethod
    def create_base_life_categories(user):
        """
        Создаём базовые сферы жизни на основе BASE_LIFE_CATEGORY_DATA
        :return: None
        """
        for category_data in BASE_LIFE_CATEGORY_DATA:
            LifeCategory(user=user, **category_data).save()


class SphereOfLifePageView(View):
    template_name = 'frontend/sphere_of_life.html'

    def get(self, request, category_name):

        site_settings = request.session['user_site_settings']
        hide_subgoals = site_settings['hide_subgoals']

        new_goal_form = forms.TreeGoalsForm()

        context = {
            'new_goal_form': new_goal_form,
            'hide_subgoals': hide_subgoals
        }

        life_category = LifeCategory.objects.filter(slug_name=category_name, user=request.user)[0]

        if life_category:
            context['current_life_category'] = life_category

            goals_list = TreeGoals.objects.filter(user=request.user, life_category=life_category.id, parent=None)

            # Добавляем кверисет с подцелями к каждой цели
            for goal in goals_list:
                goal.sub_goals = goal.children.all()

            if len(goals_list) > 0:
                # Фильтруем разбиваем данные на два массива (активные цели и завершённые)
                active_goals_list = filter(lambda g: g.completed is False, goals_list)
                completed_goals_list = filter(lambda g: g.completed is True, goals_list)

                context['active_goals_list'] = active_goals_list
                context['completed_goals_list'] = completed_goals_list

        else:
            messages.error(request, 'Не удалось получить текущую сферу жизни')

        return render(request, self.template_name, context=context)

    def post(self, request, category_name):
        form_type = request.POST.get('form_type')

        try:
            # Обработка формы добавления новой цели
            if form_type == 'new_goal_from':
                self.new_goal_form_handler(request, category_name)

            elif form_type == 'site_settings_form':
                button = request.POST.get('button')

                bool_value = False
                if button == 'hide_subgoals':
                    bool_value = True
                UserSettings.objects.filter(user=request.user).update(hide_subgoals=bool_value)

            # Обработка формы выполнения\изменения\удаления цели
            elif form_type == 'manage_goal_form':
                self.button_processing_process(request)

            elif form_type == 'checkbox_form':
                self.checkbox_form_handler(request)

            # Обновляем процент выполненных целей пользователя
            self.update_life_category_percent(request, slug_name=category_name)

        except Exception as e:
            messages.error(request, f'Ошибка при обработке формы: {form_type} - {e}')

        return redirect('sphere_of_life_page', category_name=category_name)

    def checkbox_form_handler(self, request):
        checkbox_list = request.POST.getlist('checkbox')
        # Проходим по списку и достаём ID цели
        if checkbox_list:
            for goal_id in checkbox_list:
                # Вызываем процесс обработки кнопок
                self.button_processing_process(request, int(goal_id))

    def new_goal_form_handler(self, request, category_name=None, life_category=None):
        goal_form = forms.TreeGoalsForm(request.POST)

        if goal_form.is_valid():
            # Получаем parent_id из скрытого поля формы
            parent_id = request.POST.get('parent_id')
            # Если parent_id пустое, то мы добавляем основную цель, если нет, то подцель
            if parent_id == '':
                parent_goal = None

            else:
                parent_goal = TreeGoals.objects.get(id=parent_id)

            self.create_new_goal_process(request, goal_form, category_name, parent_goal, life_category)
            messages.success(request, 'Цель добавлена')

    def button_processing_process(self, request, goal_id=None):
        """
        Обработчик нажатия кнопок из присылаемой от клиента формы
        :param request:
        :param goal_id: ID текущей цели, для которой нужно выполнить действие, по умолчанию берётся из request
        :return:
        """

        # Узнаём на какую кнопку нажал пользователь
        button = request.POST.get('button')

        if button == 'done':
            self.switch_goal_process(request, goal_id=goal_id)
            messages.success(request, 'Цель выполнена')

        elif button == 'edit':
            pass

        elif button == 'make_active':
            self.switch_goal_process(request, completed=False, goal_id=goal_id)
            messages.success(request, 'Цель снова активна')

        elif button == 'delete':
            self.delete_goal_process(request, goal_id)
            messages.success(request, 'Цель удалена')

        else:
            messages.warning(request, 'Не зарегистрированная кнопка')

    def update_life_category_percent(self, request, slug_name=None, life_category_id=None):
        """
        Обновляем информацию о проценте выполнения в модели LifeCategoryModel
        :param life_category_id: ID категории сфер жизни
        :param request:
        :param slug_name:
        :return:
        """
        if not life_category_id:
            life_category_id = LifeCategory.objects.get(user=request.user, slug_name=slug_name).id

        # Получаем текущий процент выполнения
        percent = self.calculate_completion_percentage(request, life_category_id)
        # Обновляем процент в модели
        LifeCategory.objects.filter(id=life_category_id).update(percent=percent)

    @staticmethod
    def create_new_goal_process(request, goal_form, category_name=None, parent=None, life_category=None):
        name = goal_form.cleaned_data['name']
        weight = goal_form.cleaned_data['weight']
        description = goal_form.cleaned_data['description']

        if not life_category:
            # Получаем текущую категорию
            life_category = LifeCategory.objects.filter(user=request.user, slug_name=category_name)[0]

            if life_category is None:
                raise UserApiError('Ошибка во время создания цели')

        tree_goal = TreeGoals(name=name,
                              weight=weight,
                              description=description,
                              user=request.user,
                              parent=parent)

        tree_goal.save()
        tree_goal.life_category.add(life_category)

    @staticmethod
    def delete_goal_process(request, goal_id=None):
        if not goal_id:
            goal_id = request.POST.get('goal_id')

        if goal_id:
            TreeGoals.objects.filter(id=goal_id).delete()

        else:
            raise Exception('Отсутствует goal_id')

    @staticmethod
    def switch_goal_process(request, completed=True, goal_id=None):
        """
        Обработчик переключения цели (выполнена / активна)
        :param request:
        :param completed: по умолчанию True (делает цель завершённой)
        :param goal_id: ID цели
        """

        if not goal_id:
            goal_id = request.POST.get('goal_id')

        if goal_id:
            TreeGoals.objects.filter(id=goal_id).update(completed=completed)

        else:
            raise Exception('Отсутствует goal_id')

    @staticmethod
    def calculate_subgoals_completion_percentage(subgoals_data, parent_weight):
        """"""
        total_subgoals_weight = sum(subgoal.weight for subgoal in subgoals_data)
        total_subgoals_completion_percentage = 0

        for subgoal in subgoals_data:
            if subgoal.completed:
                total_subgoals_completion_percentage += subgoal.weight

        if total_subgoals_weight > 0:
            return (total_subgoals_completion_percentage / total_subgoals_weight) * parent_weight
        return 0

    def calculate_completion_percentage(self, request, life_category_id):
        """
        Функция для подсчёта процента выполненных целей в сфере жизни
        :param request:
        :param life_category_id: ID сферы жизни
        :return: float или 0
        """

        goals_data = TreeGoals.objects.filter(user=request.user, life_category=life_category_id)

        total_weight = sum(goal.weight for goal in goals_data if goal.parent is None)

        total_completion_percentage = 0

        for goal in goals_data:

            if goal.parent is None:
                goal_weight = goal.weight

                if goal.completed:
                    total_completion_percentage += goal_weight
                else:
                    total_completion_percentage += self.calculate_subgoals_completion_percentage(goal.children.all(),
                                                                                                 goal_weight)

        result = 0
        if total_weight > 0:
            result = round((total_completion_percentage / total_weight) * 100, 1)

        return result


class SubGoalPageView(View):
    template_name = 'frontend/sub_goal_page.html'

    def get(self, request, sub_goal_id):

        try:
            current_goal = TreeGoals.objects.filter(id=sub_goal_id)[0]
            life_category_slug_name = current_goal.life_category.all()[0].slug_name

            # Добавляем кверисет с подцелями
            current_goal.sub_goals = current_goal.children.all()

            new_goal_form = forms.TreeGoalsForm()

            context = {
                'new_goal_form': new_goal_form,
                'life_category': life_category_slug_name
            }

            if current_goal:
                context['goal'] = current_goal
            else:
                messages.error(request, 'Ошибка при получении текущей цели')

            return render(request, self.template_name, context=context)

        except IndexError as ie:
            return redirect('my_progress_page')

    def post(self, request, sub_goal_id):
        form_type = request.POST.get('form_type')
        sphere_of_life_view = SphereOfLifePageView()

        try:
            current_goal = TreeGoals.objects.filter(id=sub_goal_id)[0]
            life_category = current_goal.life_category.all()[0]

            if form_type == 'manage_goal_form':
                sphere_of_life_view.button_processing_process(request, sub_goal_id)

            elif form_type == 'new_goal_from':
                sphere_of_life_view.new_goal_form_handler(request, life_category=life_category)

            elif form_type == 'checkbox_form':
                sphere_of_life_view.checkbox_form_handler(request)

            # Обновляем процент выполненных целей пользователя
            sphere_of_life_view.update_life_category_percent(request, life_category_id=life_category.id)

        except Exception as e:
            messages.error(request, f'Ошибка при обработке формы: {form_type} - {e}')

        url = reverse('sub_goal_page', kwargs={'sub_goal_id': sub_goal_id})
        return redirect(url)


class UserProfileView(View):
    template_name = 'frontend/profile/user_profile.html'

    def get(self, request):

        photo_form = forms.UploadUserPhotoForm()
        info_form = forms.UserProfileInfoFrom(instance=request.user)
        change_pass_form = forms.ChangeProfilePasswordFrom()

        context = {
            'photo_form': photo_form,
            'info_form': info_form,
            'change_pass_form': change_pass_form
        }

        return render(request, self.template_name, context=context)

    def post(self, request):
        upload_form = forms.UploadUserPhotoForm(request.POST, request.FILES)
        info_form = forms.UserProfileInfoFrom(request.POST)
        change_pass_form = forms.ChangeProfilePasswordFrom(request.POST)
        form_button = request.POST.get('button')

        if upload_form.is_valid():
            self.process_upload_photo(request, upload_form)

        elif info_form.is_valid() and form_button == 'change_info':
            self.process_change_user_info(request, info_form)
            messages.success(request, 'Изменено')

        elif change_pass_form.is_valid():
            self.process_change_user_password(request, change_pass_form)
            messages.success(request, 'Пароль успешно изменён')
            return redirect('user_profile')

        context = {
            'upload_form': upload_form,
            'info_form': info_form,
            'change_pass_form': change_pass_form,
        }

        return render(request, self.template_name, context=context)

    @staticmethod
    def process_upload_photo(request, form):
        photo = form.cleaned_data['photo']

        # Получаем старое фото и переключаем метку main_photo в False
        old_main_photo = UserProfilePhoto.objects.filter(user=request.user, main_photo=True)
        old_main_photo.update(main_photo=False)

        # Создаём новое основное фото профиля
        new_photo = UserProfilePhoto(photo=photo, user=request.user, main_photo=True)
        new_photo.save()

    @staticmethod
    def process_change_user_info(request, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']

        User.objects.filter(id=request.user.id).update(first_name=first_name, last_name=last_name, email=email)

    @staticmethod
    def process_change_user_password(request, form):
        password = form.cleaned_data['password']
        password_repeat = form.cleaned_data['password_repeat']
        if password == password_repeat:
            user = User.objects.get(id=request.user.id)
            user.set_password(password)
            user.save()
            login(request, user)


class ChangeProfilePhotoView(View):
    def get(self, request):
        user_photo_data = UserProfilePhoto.objects.filter(user=request.user)

        contex = {'user_photos': user_photo_data}
        return render(request, 'frontend/profile/choice_profile_photo.html', contex)

    def post(self, request):
        photo_id = request.POST.getlist('photo_id')
        form_button = request.POST.get('button')

        if photo_id:
            if form_button == 'change_photo':
                user_photo_data = UserProfilePhoto.objects.filter(user=request.user)
                user_photo_data.update(main_photo=False)

                user_photo = user_photo_data.filter(id=photo_id[-1])
                user_photo.update(main_photo=True)

            elif form_button == 'delete_photo':
                for id in photo_id:
                    UserProfilePhoto.objects.filter(user=request.user, id=id).delete()
                return redirect('change_profile_photo')

        return redirect('user_profile')
