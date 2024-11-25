#ifndef CLOSEST_POINTS_H
#define CLOSEST_POINTS_H

#include <queue>
#include <unordered_set>
#include <vector>
#include <tuple>

// Hash function for std::pair<int, int>
struct local_pair_hash {
    template <class T1, class T2>
    std::size_t operator()(const std::pair<T1, T2>& p) const noexcept {
        auto hash1 = std::hash<T1>{}(p.first);
        auto hash2 = std::hash<T2>{}(p.second);
        return hash1 ^ hash2;
    }
};

class ClosestPointsIterator {
public:
    // Constructor to initialize the iterator
    ClosestPointsIterator();
    ClosestPointsIterator(int x, int y);

    // Dereference to get the current closest point
    std::pair<int, int> operator*() const;

    // Advance to the next closest point
    ClosestPointsIterator& operator++();

private:
    // Priority queue to store points by distance (min-heap)
    std::pair<int, int> origin;
    using Entry = std::tuple<int, int, int>;  // {distance^2, x, y}
    std::priority_queue<Entry, std::vector<Entry>, std::greater<>> to_visit;

    std::unordered_set<std::pair<int, int>, local_pair_hash> visited;
    std::vector<std::pair<int, int>> directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
};

#endif // CLOSEST_POINTS_H