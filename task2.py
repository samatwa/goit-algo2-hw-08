import time
from typing import Dict
import random


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.last_message_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """Перевіряє, чи може користувач надіслати повідомлення."""
        current_time = time.time()

        if user_id not in self.last_message_time:
            return True  # При першому повідомленні

        elapsed = current_time - self.last_message_time[user_id]
        return elapsed >= self.min_interval  # False, якщо менше 10 секунд

    def record_message(self, user_id: str) -> bool:
        """Записує повідомлення користувача, якщо це можливо."""
        if not self.can_send_message(user_id):
            return False
        self.last_message_time[user_id] = time.time()
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        """Повертає час до наступного дозволеного повідомлення для користувача."""
        current_time = time.time()

        if user_id not in self.last_message_time:
            return 0.0

        elapsed = current_time - self.last_message_time[user_id]
        wait_time = self.min_interval - elapsed
        return max(wait_time, 0.0)


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
