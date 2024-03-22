import time
import redis
import os
import json
from get_games import get_live_games

def update_live_games_cache(interval=10):  # Interval in seconds
    while True:
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            redis_store = redis.from_url(redis_url)
            # This part needs to be adjusted to how you plan to store and share data
            # between your worker and your web process. Options include using a database,
            # a cache like Redis, or an in-memory store if they are in the same memory space.
            cached_live_games = get_live_games()
            redis_store.set('cached_live_games',  json.dumps(cached_live_games))
            print("Cache updated!", cached_live_games)
        except Exception as e:
            print(f"Error updating cache: {e}")
        time.sleep(interval)

if __name__ == '__main__':
    update_live_games_cache(10)  # Or any other interval you'd prefer