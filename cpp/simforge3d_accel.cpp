// Optional extension sketch. Not built by default.
//
// Intended use:
// - Broad-phase collision checks
// - Spatial hashing / nearest-neighbor queries
// - Batched reward computations
//
// Keep Python fallback implementations authoritative until this extension is wired
// into pyproject.toml with pybind11 or scikit-build-core.

#include <cmath>

extern "C" double simforge3d_distance_xy(double ax, double ay, double bx, double by) {
    const double dx = ax - bx;
    const double dy = ay - by;
    return std::sqrt(dx * dx + dy * dy);
}
