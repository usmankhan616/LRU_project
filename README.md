# Advanced Cache Algorithm Visualizer

An interactive, real-time visualizer that compares the performance of LRU, LFU, and LRU-K cache eviction policies. This tool allows users to see how different algorithms handle various data access patterns and helps in understanding their core mechanics and trade-offs.

### ✨ [Live Demo](https://cache-visualizer.onrender.com/) ✨

*(Replace the link above with your actual Render URL!)*

---

## Understanding the Algorithms

This project visualizes three key cache eviction algorithms:

* **LRU (Least Recently Used):** This is one of the most common caching algorithms. When the cache is full and a new item needs to be added, LRU discards the item that has not been used for the longest amount of time. It keeps track of access history by treating the cache like a queue, moving any accessed item to the back.

* **LFU (Least Frequently Used):** This algorithm evicts the item that has been accessed the fewest number of times. LFU assumes that items that have been accessed often are more likely to be accessed again. It's useful for workloads where some items are consistently popular.

* **LRU-K (Least Recently Used - Kth):** An improvement over standard LRU. Instead of looking at the most recent access, LRU-K considers the time of the K-th most recent access. This makes it more robust against "scan" workloads (where a large number of items are accessed once) and helps it make better decisions about which items are truly "hot" versus just being accessed recently.

---

## 🚀 Features

The visualizer is packed with interactive controls to let you customize the simulation:

* **Workload Types:**
    * **Realistic:** Simulates a real-world scenario where a small set of "hot" items are accessed frequently (the 80/20 rule).
    * **Scan:** Simulates accessing a long sequence of unique items, which is typically challenging for standard LRU.
    * **Random:** Accesses items in a completely random order.
    * **Custom:** Allows you to input your own sequence of page requests.

* **Cache Configuration:**
    * **Cache Capacity:** Set the total number of items the cache can hold.
    * **Speed:** Control the simulation speed with a simple slider.
    * **Adaptive-K:** An option for LRU-K that dynamically adjusts the 'K' value based on workload patterns.
    * **K-Value:** Manually set the 'K' for the LRU-K algorithm when not in adaptive mode.

* **Simulation Controls:**
    * **Start/Pause/Clear:** Full control over the simulation flow.
    * **Algorithm Toggles:** Enable or disable any of the three caches (LRU, LFU, LRU-K) to compare them head-to-head or focus on one.

* **Live Performance Graph:**
    * A real-time chart plots the **Hit Rate vs. Simulation Step** for each active algorithm, providing a clear visual comparison of their performance over time.

---

## 🛠️ Tech Stack

This project was built using a modern web stack:

* **Backend:**
    * **Python:** The core programming language.
    * **FastAPI:** A high-performance web framework for building the API and WebSocket server.
    * **Gunicorn:** A production-grade WSGI server to run the FastAPI application.

* **Frontend:**
    * **HTML5, CSS3, JavaScript:** The foundation of the user interface.
    * **Chart.js:** Used for rendering the live performance graph.

* **Deployment:**
    * **Render:** The cloud platform used for hosting the live application.