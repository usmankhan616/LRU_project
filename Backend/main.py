import time
from collections import OrderedDict, defaultdict
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import random
from typing import Dict, List, Any

# --------------------------------------------------------------------------
# --- ALL CACHE LOGIC IS NOW INCLUDED DIRECTLY IN THIS FILE ---
# --- LFUCACHE HAS BEEN COMPLETELY REWRITTEN FOR STABILITY ---
# --------------------------------------------------------------------------

class LRUCache:
    """A robust LRU Cache implemented with Python's built-in OrderedDict."""
    def __init__(self, capacity: int):
        if capacity <= 0: raise ValueError("Capacity must be a positive integer.")
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: str) -> Any:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def get_state(self) -> List[str]:
        return list(reversed(self.cache.keys()))

class LRUKCache:
    """An LRU-K Cache built on the robust LRUCache."""
    def __init__(self, capacity: int, k: int = 2, adaptive: bool = False):
        if capacity <= 0 or k <= 0: raise ValueError("Capacity and K must be positive integers.")
        self.k, self.initial_k, self.capacity, self.adaptive = k, k, capacity, adaptive
        self._history_cache, self._main_cache = LRUCache(capacity), LRUCache(capacity)
        self._ops_counter, self._history_hits, self._promotions = 0, 0, 0

    def _adapt(self):
        if not self.adaptive or self._history_hits == 0: return
        promo_ratio = self._promotions / self._history_hits
        if promo_ratio < 0.1 and self.k < 5: self.k += 1
        elif promo_ratio > 0.4 and self.k > self.initial_k: self.k -= 1
        self._ops_counter, self._history_hits, self._promotions = 0, 0, 0

    def get(self, key: str) -> any:
        return self._main_cache.get(key)

    def put(self, key: str, value: any) -> dict:
        self._ops_counter += 1
        if self._ops_counter >= 20: self._adapt()
        event = {"key": key, "location": "none", "promoted": False, "evicted": None}
        if self._main_cache.get(key) is not None:
            event["location"] = "main_cache"
            return event
        history_timestamps = self._history_cache.get(key)
        if history_timestamps is not None:
            self._history_hits += 1
            event["location"] = "history_cache"
            history_timestamps.append(time.time())
            if len(history_timestamps) >= self.k:
                self._promotions += 1
                event["promoted"] = True
                self._main_cache.put(key, value)
            else:
                self._history_cache.put(key, history_timestamps)
            return event
        event["location"] = "new"
        self._history_cache.put(key, [time.time()])
        return event

    def get_state(self):
        return {"history_cache": self._history_cache.get_state(), "main_cache": self._main_cache.get_state(), "current_k": self.k}

class LFUCache:
    """A robust Least Frequently Used (LFU) Cache."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.vals = {}
        self.counts = defaultdict(int)
        self.lists = defaultdict(OrderedDict)
        self.min_count = 0

    def get(self, key: str) -> Any:
        if key not in self.vals:
            return None
        
        count = self.counts[key]
        # Move key from old frequency list to new one
        del self.lists[count][key]

        # if the list at min_count is now empty, increment min_count
        if not self.lists[count] and self.min_count == count:
            self.min_count += 1

        new_count = count + 1
        self.counts[key] = new_count
        self.lists[new_count][key] = None
        
        return self.vals[key]

    def put(self, key: str, value: any) -> None:
        if self.capacity == 0: return

        if key in self.vals:
            self.vals[key] = value
            self.get(key) # This handles the frequency update
            return

        if len(self.vals) >= self.capacity:
            # Evict from the list with the minimum frequency
            evict_key, _ = self.lists[self.min_count].popitem(last=False)
            del self.vals[evict_key]
            del self.counts[evict_key]

        # Add new item
        self.vals[key] = value
        self.counts[key] = 1
        self.lists[1][key] = None
        self.min_count = 1

    def get_state(self):
        all_items = []
        # Sort by frequency to display
        for count in sorted(self.lists.keys()):
            # Within the same frequency, they are ordered by recent use
            for key in reversed(self.lists[count]):
                all_items.append(key)
        return all_items

# --------------------------------------------------------------------------
# --- FASTAPI SERVER LOGIC ---
# --------------------------------------------------------------------------

app = FastAPI()

class SimulationConfig(BaseModel):
    k_value: int
    capacity: int
    workload_type: str
    workload_size: int
    adaptive_k: bool
    speed: float
    custom_workload: str
    active_caches: Dict[str, bool]

def generate_workload(workload_type: str, custom_text: str, size: int) -> List[str]:
    if workload_type == "custom":
        items = [item.strip() for item in custom_text.replace(',', ' ').replace('\n', ' ').split() if item.strip()]
        return items if items else []
    if workload_type == "scan":
        return [f"item-{i}" for i in range(size)]
    if workload_type == "realistic":
        hot_items = [f"item-{i}" for i in range(5)]
        cold_items = [f"item-{i}" for i in range(5, size)]
        return [random.choice(hot_items) if random.random() < 0.8 else random.choice(cold_items) for _ in range(size)]
    return [f"item-{random.randint(1, 20)}" for _ in range(size)]

@app.websocket("/ws/simulation")
async def simulation_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        config_data = await websocket.receive_json()
        config = SimulationConfig(**config_data)
        workload = generate_workload(config.workload_type, config.custom_workload, config.workload_size)
        if not workload:
            await websocket.close(code=1000, reason="Empty workload")
            return

        caches = {
            'lru': LRUCache(config.capacity) if config.active_caches.get('lru') else None,
            'lfu': LFUCache(config.capacity) if config.active_caches.get('lfu') else None,
            'lruk': LRUKCache(config.capacity, config.k_value, config.adaptive_k) if config.active_caches.get('lruk') else None
        }
        hits = {'lru': 0, 'lfu': 0, 'lruk': 0}

        for i, key in enumerate(workload):
            state_to_send = {"step": i + 1, "total_steps": len(workload), "current_key": key}
            
            if caches['lru']:
                if caches['lru'].get(key) is not None: hits['lru'] += 1
                else: caches['lru'].put(key, f"v-{key}")
                state_to_send['lru_cache'] = {"state": caches['lru'].get_state(), "hits": hits['lru'], "hit_rate": hits['lru'] / (i + 1)}

            if caches['lfu']:
                if caches['lfu'].get(key) is not None: hits['lfu'] += 1
                else: caches['lfu'].put(key, f"v-{key}")
                state_to_send['lfu_cache'] = {"state": caches['lfu'].get_state(), "hits": hits['lfu'], "hit_rate": hits['lfu'] / (i + 1)}

            if caches['lruk']:
                lruk_event = caches['lruk'].put(key, f"v-{key}")
                if lruk_event['location'] == 'main_cache': hits['lruk'] += 1
                state_to_send['lruk_cache'] = {"state": caches['lruk'].get_state(), "hits": hits['lruk'], "hit_rate": hits['lruk'] / (i + 1), "last_event": lruk_event}
            
            await websocket.send_json(state_to_send)
            await asyncio.sleep(config.speed)

        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.close(code=1011, reason=str(e))
