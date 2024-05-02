from django import template
from django.utils.html import mark_safe

from api import api_client
from api.models import TreeGoals


register = template.Library()


@register.simple_tag
def draw_goal_branch(user, sub_goals_list=None, sub_goal_id=False):

    result_html = '<div class="goal-progress-branch">'
    # Если передан sub_goal_id и request то вызываем функцию для получения списка подцелей
    if sub_goal_id and user:
        result_html = '<div class="sub-goal-progress-branch">'

        parent_goal = TreeGoals.objects.get(user=user, id=sub_goal_id)
        sub_goals_list = parent_goal.children.all()

    if sub_goals_list and user:
        parent_goal_id = sub_goals_list[0].parent.id
        parent_goal = TreeGoals.objects.get(user=user, id=parent_goal_id)
        check_completed_parent_goal(sub_goals_list, parent_goal=parent_goal)

    if sub_goals_list and len(sub_goals_list) > 1:
        last_goal_id = list(sub_goals_list)[-1].id
        for goal in sub_goals_list:

            result_html += f'<div class="branch-circle circle-weight-{goal.weight} circle-done-{goal.completed}"' \
                           f' title="{goal.name}"></div>'

            if goal.id != last_goal_id:
                result_html += '<div class="branch-line"></div>'

    result_html += '</div>'
    return mark_safe(result_html)


def check_completed_parent_goal(sub_goals_list, parent_goal):
    """
    Функция для проверки выполнения цели исходя из её подцелей
    :param parent_goal:
    :param sub_goals_list:
    :return:
    """
    goals_value_completed_list = [goal.completed for goal in sub_goals_list]

    # Если все подцели выполнены
    if all(goals_value_completed_list):
        # Делаем цель выполненной
        parent_goal.competed = True
        parent_goal.save()
