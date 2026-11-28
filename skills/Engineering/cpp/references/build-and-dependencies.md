# Build, CMake, Dependencies, and Toolchains

Read this reference for CMake, compiler configuration, packages, CI build matrices, installation, cross-compilation, or reproducibility.

## CMake model

Use target-based CMake. Model real dependencies on targets rather than relying on directory-global flags/includes/definitions.

- `PRIVATE`: needed only to build the target.
- `PUBLIC`: needed by the target and by consumers of its public interface.
- `INTERFACE`: needed only by consumers.

Use `target_link_libraries`, `target_include_directories`, `target_compile_definitions`, `target_compile_options`, and `target_compile_features` with correct visibility.

Do not create a library target solely because a conceptual layer exists. Create targets for compilation/reuse/deployment/ownership boundaries that benefit from independent build properties.

## Standards and warnings

- Express the C++ standard through target compile features/project configuration, not scattered flags.
- Preserve the repository's compiler matrix.
- Enable strong warnings and treat project-owned warnings as errors where the repository supports it; avoid forcing `-Werror` onto third-party code.
- Keep platform/compiler-specific flags localized.
- Separate sanitizer/debug instrumentation from production release flags.

## Presets and configurations

Prefer checked-in CMake Presets for reproducible developer/CI configuration when the repository uses modern CMake. Keep configure/build/test presets aligned with supported platforms.

Use meaningful configurations such as Debug, RelWithDebInfo, and Release according to project policy. For performance investigation, prefer optimized builds with symbols.

## Dependencies

Prefer the repository's package manager and versioning strategy.

For Conan-style workflows:

- distinguish build and host profiles for cross-compilation;
- use generated CMake toolchain/dependency integration rather than hand-coded package paths;
- pin or lock dependency resolution where reproducibility matters.

For vcpkg-style workflows:

- prefer manifest mode for project dependencies;
- use version constraints/baselines/registries according to repository policy;
- avoid depending on developer-global mutable package state.

Do not add a third-party dependency for functionality the standard library or an existing dependency adequately provides unless the tradeoff is justified.

## FetchContent/submodules/vendor code

Choose deliberately:

- package manager: reproducible versioned external dependency;
- vendored source/submodule: tight patch/control requirement or repository policy;
- `FetchContent`: acceptable when network/configuration policy and reproducibility are controlled.

Keep third-party warnings/formatting/static analysis separated from project-owned code where practical.

## Install/package/export

For reusable libraries, decide whether consumers build in-tree or consume installed packages. When installation is required, maintain coherent export sets, namespaced targets, headers, package config/version files, and runtime dependencies.

## Cross-compilation

Treat build machine and target machine separately. Use toolchain files/profiles rather than embedding target assumptions in source CMake. Verify endianness, word size, architecture, system libraries, and emulator/test limitations when relevant.

## Build performance

For slow builds, measure causes before applying unity builds/PCH/modules. Improve include hygiene, target boundaries, generated code behavior, template instantiation, and dependency fan-out first. Use PCH/unity/modules only when compatible with repository goals and measured to help.
