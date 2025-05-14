import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Очищає застарілі запити, які вийшли за межі часового вікна."""

        if user_id in self.user_requests:
            window = self.user_requests[user_id]
            while window and (current_time - window[0]) > self.window_size:
                window.popleft()

            if not window:
                del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Перевіряє, чи може користувач надіслати повідомлення."""

        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_requests:
            return True  # При першому повідомленні

        return (
            len(self.user_requests[user_id]) < self.max_requests
        )  # False, якщо кількість повідомлень у вікні перевищує ліміт

    def record_message(self, user_id: str) -> bool:
        """Записує повідомлення користувача, якщо це можливо."""

        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(current_time)
            return True

        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Повертає час до наступного дозволеного повідомлення для користувача."""

        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id in self.user_requests and self.user_requests[user_id]:
            wait_time = self.window_size - (
                current_time - self.user_requests[user_id][0]
            )
            return max(wait_time, 0.0)

        return 0.0


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
