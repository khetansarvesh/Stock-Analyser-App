import heapq

class StockMinHeap:
    """A min-heap implementation for tracking worst-performing stocks."""
    
    def __init__(self, max_size=10):
        self.heap = []
        self.max_size = max_size
        self.stock_index = {}  # Maps stock symbol to position in heap
    
    def push(self, stock_symbol, value, timestamp):
        """
        Add a stock to the min-heap or update its value.
        
        Args:
            stock_symbol (str): The stock ticker symbol
            value (float): The value to track (e.g., percentage change)
            timestamp (int/float): When this value was recorded
        """
        item = (value, stock_symbol, timestamp)
        
        if stock_symbol in self.stock_index:
            # Update existing stock
            old_idx = self.stock_index[stock_symbol]
            self.heap[old_idx] = item
            heapq.heapify(self.heap)
        else:
            # Add new stock
            if len(self.heap) < self.max_size:
                heapq.heappush(self.heap, item)
            elif value < self.heap[0][0]:
                # If heap is full, replace the smallest item if new value is smaller
                heapq.heappushpop(self.heap, item)
            else:
                return
                
        # Update index mapping
        self._update_index()
    
    def _update_index(self):
        """Update the index mapping after heap changes."""
        self.stock_index = {item[1]: idx for idx, item in enumerate(self.heap)}
    
    def get_top(self, n=None):
        """Get the top n stocks with smallest values."""
        if n is None:
            n = self.max_size
        
        return sorted(self.heap)[:min(n, len(self.heap))]
    
    def remove(self, stock_symbol):
        """Remove a stock from the heap."""
        if stock_symbol in self.stock_index:
            idx = self.stock_index[stock_symbol]
            self.heap[idx] = self.heap[-1]
            self.heap.pop()
            if self.heap:
                heapq.heapify(self.heap)
            del self.stock_index[stock_symbol]
            self._update_index()
            return True
        return False


class StockMaxHeap:
    """A max-heap implementation for tracking best-performing stocks."""
    
    def __init__(self, max_size=10):
        self.heap = []
        self.max_size = max_size
        self.stock_index = {}  # Maps stock symbol to position in heap
    
    def push(self, stock_symbol, value, timestamp):
        """
        Add a stock to the max-heap or update its value.
        For max-heap, we negate the value when storing.
        
        Args:
            stock_symbol (str): The stock ticker symbol
            value (float): The value to track (e.g., percentage change)
            timestamp (int/float): When this value was recorded
        """
        # Negate value for max-heap behavior
        item = (-value, stock_symbol, timestamp)
        
        if stock_symbol in self.stock_index:
            # Update existing stock
            old_idx = self.stock_index[stock_symbol]
            self.heap[old_idx] = item
            heapq.heapify(self.heap)
        else:
            # Add new stock
            if len(self.heap) < self.max_size:
                heapq.heappush(self.heap, item)
            elif -value > self.heap[0][0]:
                # If heap is full, replace the smallest item if new value is larger (negated)
                heapq.heappushpop(self.heap, item)
            else:
                return
                
        # Update index mapping
        self._update_index()
    
    def _update_index(self):
        """Update the index mapping after heap changes."""
        self.stock_index = {item[1]: idx for idx, item in enumerate(self.heap)}
    
    def get_top(self, n=None):
        """Get the top n stocks with largest values."""
        if n is None:
            n = self.max_size
        
        # Return sorted values, unnegating the values
        result = [(abs(val), symbol, ts) for val, symbol, ts in sorted(self.heap)]
        return result[:min(n, len(self.heap))]
    
    def remove(self, stock_symbol):
        """Remove a stock from the heap."""
        if stock_symbol in self.stock_index:
            idx = self.stock_index[stock_symbol]
            self.heap[idx] = self.heap[-1]
            self.heap.pop()
            if self.heap:
                heapq.heapify(self.heap)
            del self.stock_index[stock_symbol]
            self._update_index()
            return True
        return False
