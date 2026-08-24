# config.py
from datetime import timezone, timedelta

# Telegram API
API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"
SESSION_STRING = "1ApWapzMBu53lyW3dwKs05w6mLe-ycWEcgzChNf4Ud4sDlWBbgrjI3jWvM_a7F4TKdUTsuojQpy7YTXV7NZCs2vOtkgkgPLIoj70wE84E3qZEEXkO5PdfjU9HX16waA1Gvw6dcfhoMe9htGEiEKzu7UiKGOsMy75dyp1Q5LVYkbh7FVk9655zfSehAXLSMyLiGp9M-XG3ybcoc5j_W-zooESNbGVGBnqok7pBXcculdVHi6_PqPpp_SB-dmJwQTNmvy7uafebwqaRk8Ed5Il0tRx9SKtozQAhAn-32cICUs8jb193coYHE20QcMwOmht3X7Ylso85dkU9Vf3xgBJQYPi7KYgnLbE="

# Группа и темы
GROUP_ID = 1004368107724
TOPIC_INCOMING = 2
TOPIC_REMINDERS = 3
TOPIC_STATS = 4
TOPIC_IMPORTANT = 5

# Время
MOSCOW_TZ = timezone(timedelta(hours=3))

# Твой ID
OWNER_ID = 542094552

# Фильтрация
FILTER_MODE = "bot_only"  # "all", "bot_only", "whitelist"