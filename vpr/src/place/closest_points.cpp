#include "closest_points.h"
#include <cmath>

ClosestPointsIterator::ClosestPointsIterator() : origin{0, 0} {
    // Initialize with the origin (0, 0)
    to_visit.push({0, 0, 0});
    visited.insert({0, 0});
}

ClosestPointsIterator::ClosestPointsIterator(int x, int y) : origin{x, y} {
    // Initialize with the given point (x, y)
    to_visit.push({0, x, y});
    visited.insert({x, y});
}

std::pair<int, int> ClosestPointsIterator::operator*() const {
    return {std::get<1>(to_visit.top()), std::get<2>(to_visit.top())};
}

ClosestPointsIterator& ClosestPointsIterator::operator++() {
    auto [dist, x, y] = to_visit.top();
    to_visit.pop();

    // Add the neighboring points (x ± 1, y) and (x, y ± 1)
    for (const auto& [dx, dy] : directions) {
        int nx = x + dx, ny = y + dy;
        if (!visited.count({nx, ny})) { // Check if the point is visited
            int newDist = abs(nx - origin.first) + abs(ny - origin.second);
            to_visit.push({newDist, nx, ny});
            visited.insert({nx, ny});
        }
    }

    return *this;
}