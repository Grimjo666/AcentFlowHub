from django import template
from django.utils.html import mark_safe

from api import api_client


register = template.Library()


@register.simple_tag
def draw_goal_branch(sub_goals_list=None, sub_goal_id=False, request=None):

    result_html = '<div class="goal-progress-branch">'
    # Если передан sub_goal_id и request то вызываем функцию для получения списка подцелей
    if sub_goal_id and request:
        result_html = '<div class="sub-goal-progress-branch">'

        api_tree_goal_requests = api_client.TreeGoalsAPI(request)
        sub_goals_list = api_tree_goal_requests.get_sub_goals(sub_goal_id)

    if sub_goals_list and request:
        check_completed_parent_goal(sub_goals_list, request)

    if sub_goals_list and len(sub_goals_list) > 1:
        last_goal_id = sub_goals_list[-1].get('id')
        for goal in sub_goals_list:
            goal_weight = goal.get('weight')
            completed = goal.get('completed')
            name = goal.get('name')
            result_html += f'<div class="branch-circle circle-weight-{goal_weight} circle-done-{completed}"' \
                           f' title="{name}"></div>'
            if goal.get('id') != last_goal_id:
                result_html += '<div class="branch-line"></div>'

    result_html += '</div>'
    return mark_safe(result_html)


def check_completed_parent_goal(sub_goals_list, request):
    """
    Функция для проверки выполнения цели исходя из её подцелей
    :param request:
    :param sub_goals_list:
    :return:
    """
    goals_value_completed_list = [goal.get('completed') for goal in sub_goals_list]
    sub_goals_parent_id = sub_goals_list[0].get('parent')
    api_tree_goal_requests = api_client.TreeGoalsAPI(request)

    # Если все подцели выполнены
    if all(goals_value_completed_list):
        # Делаем цель выполненной
        api_tree_goal_requests.partially_update(pk=sub_goals_parent_id, data={'completed': True})


