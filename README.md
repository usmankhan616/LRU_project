# Advanced Cache Algorithm Visualizer

A real-time visualization tool for comparing LRU, LFU, and LRU-K cache eviction policies.

## 🔧 Fixed Issues

### Problem Description
The original project had visualization issues where:
- ✅ When Standard LRU and Standard LFU are both selected, only LRU works, LFU graph doesn't appear. **FIXED**
- ✅ When LFU is used with LRU-K, LFU works fine. **WORKING** 
- ✅ When all three selected: LRU and LRU-K work, LFU doesn't show. **FIXED**

### Root Cause
The issue was in the JavaScript frontend code (`frontend/index.html`) in the `updateList` function call for the LRU-K main cache. The function parameters were in the wrong order:

**Before (Broken):**
```javascript
updateList(ui.lruk.main, data.lruk_cache.state.main_cache, data.lruk_cache.last_event, 'lruk');
```

**After (Fixed):**
```javascript
updateList(ui.lruk.main, data.lruk_cache.state.main_cache, data.current_key, data.lruk_cache.last_event, 'lruk');
```

The `currentKey` parameter was missing, which caused the LFU visualization to fail when all three caches were selected.

## 🚀 How to Run

### Prerequisites
- Python 3.7+
- Modern web browser

### Setup & Run
1. **Install Python dependencies:**
   ```bash
   cd Backend
   pip install fastapi uvicorn websockets
   ```

2. **Start the backend server:**
   ```bash
   cd Backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

3. **Open the frontend:**
   - Navigate to `frontend/index.html` 
   - Open it in your web browser
   - The application will connect to the backend automatically

## 🎮 How to Use

### Basic Controls
- **Cache Capacity**: Set the maximum number of items each cache can hold
- **Workload Type**: Choose from:
  - **Realistic**: 80% hot data, 20% cold data (simulates real-world usage)
  - **Scan**: Sequential access pattern
  - **Random**: Random access pattern  
  - **Custom**: Define your own access sequence
- **Speed**: Control simulation speed
- **K-Value**: Set the K parameter for LRU-K algorithm
- **Adaptive-K**: Enable dynamic K adjustment

### Toggle Caches
- Use the **ON/OFF** buttons to enable/disable individual caches
- You can compare any combination of the three algorithms
- Charts will automatically update to show only active caches

### What to Watch For
- **Cache Contents**: Real-time view of what's stored in each cache
- **Hit/Miss Statistics**: Track performance metrics
- **Hit Rate Chart**: Visual comparison of algorithm performance over time
- **LRU-K History/Main**: Observe the two-tier structure of LRU-K

## 🏗️ Architecture

### Backend (`Backend/main.py`)
- **FastAPI** WebSocket server
- **LRUCache**: Standard LRU using OrderedDict
- **LFUCache**: Frequency-based eviction with robust implementation
- **LRUKCache**: Two-tier cache with history and main sections

### Frontend (`frontend/index.html`)
- **Pure JavaScript** with Chart.js for visualizations
- **WebSocket** connection for real-time updates
- **Responsive Design** with dark theme

## 🧪 Testing

Run the test suite to verify everything works:
```bash
python test_fix.py
```

This will test all three cache implementations individually.

## 🎯 Cache Algorithm Details

### LRU (Least Recently Used)
- Evicts the item that was accessed longest ago
- Uses Python's `OrderedDict` for O(1) operations
- Simple and widely used in practice

### LFU (Least Frequently Used)  
- Evicts the item with the lowest access frequency
- Maintains frequency counters and frequency lists
- Better for workloads with clear hot/cold data patterns

### LRU-K
- Hybrid approach with history and main cache
- Item must be accessed K times to be promoted to main cache
- **Adaptive-K**: Automatically adjusts K based on promotion success rate
- Good for filtering out one-time accesses

## 🎨 Visualization Features

- **Real-time Updates**: See cache states change with each access
- **Color Coding**: Different colors for each algorithm and access types
- **Interactive Charts**: Toggle algorithms on/off
- **Performance Metrics**: Hit rates, miss counts, and trends
- **Hover Effects**: Enhanced interactivity

## 📊 Performance Comparison

The visualizer helps you understand when each algorithm performs best:

- **LRU**: Good for temporal locality (recent items accessed again)
- **LFU**: Good for frequency patterns (popular items stay popular) 
- **LRU-K**: Good for filtering noise while maintaining recency benefits

## 🐛 Troubleshooting

### Common Issues
1. **WebSocket Connection Failed**: Ensure backend is running on port 8000
2. **No Data Showing**: Check browser console for JavaScript errors
3. **Charts Not Updating**: Verify at least one cache is toggled ON

### Browser Compatibility
- Chrome/Edge: Fully supported
- Firefox: Fully supported  
- Safari: Supported (may need local server for WebSocket)

## 🔄 Future Enhancements

Potential improvements:
- More cache algorithms (FIFO, Random, etc.)
- Export simulation data
- Batch testing with multiple workloads
- Cache size optimization recommendations
- Memory usage visualization

## 📝 License

This project is for educational purposes. Feel free to modify and extend!
