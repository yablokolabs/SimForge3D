# Optional C++ acceleration

SimForge3D is Python-first. Heavy computations such as broad-phase collision checks, spatial indexing, or batched reward calculations can be moved into optional C++ extensions later.

A future extension should keep the Python API stable and expose accelerated functions behind interfaces such as `PhysicsSystem` or scenario reward helpers.
