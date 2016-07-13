from django.conf import settings
from niuauth.models import ReputationStat

def user_reward(user, reward_type, topic_id=None, node_id=None):
    amount = settings.REP_GET_SETTING[reward_type]
    total = user.profile.reputation + amount
    stat = ReputationStat(user=user, stat_type=reward_type, amount=amount, total=total,
                          topic_id=topic_id, node_id=node_id)
    stat.save()
    user.profile.reputation = total

