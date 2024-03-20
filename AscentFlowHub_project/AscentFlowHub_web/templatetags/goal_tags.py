from django import template
from django.utils.html import mark_safe


register = template.Library()


@register.simple_tag
def draw_goal_branch(subgoals_list):
    result_html = '<div class="goal-progress-branch">'
    if len(subgoals_list) > 1:
        last_goal_id = subgoals_list[-1].get('id')
        for goal in subgoals_list:
            goal_weight = goal.get('weight')
            completed = goal.get('completed')
            result_html += f'<div class="branch-circle circle-weight-{goal_weight} circle-done-{completed}"></div>'
            if goal.get('id') != last_goal_id:
                result_html += '<div class="branch-line"></div>'

    result_html += '</div>'
    return mark_safe(result_html)
