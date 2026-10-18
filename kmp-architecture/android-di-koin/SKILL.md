---
name: android-di-koin
description: |
  Koin dependency injection setup for Android/KMP - module definitions per layer, ViewModel injection, assembling modules in :app, and koinViewModel() in composables. Use this skill whenever setting up Koin, defining a DI module, providing a repository or ViewModel, injecting a dependency, or wiring modules in the Application class. Trigger on phrases like "set up Koin", "add a Koin module", "inject a dependency", "DI module", "koinViewModel", "provide a ViewModel", "startKoin", or "single/viewModel/factory".
---

# Android / KMP Dependency Injection (Koin)

## Principles

- **Two shared modules**: one `datasourceModule` for all data-layer singletons (DB, DAOs, repositories, preferences) and one `presentationModule` for all ViewModels. Plus one platform-specific module per platform.
- Modules are assembled in `:app`, never in feature modules themselves.
- In Compose root composables, always inject ViewModels via `koinViewModel()`.
- Prefer constructor-reference overloads (`singleOf`, `viewModelOf`, `factoryOf`); lambda overloads only when constructor injection alone is not enough (factory methods, named qualifiers, post-construction setup).
- Never pass ViewModels down the composable tree — inject at the Root level only.

---

## Examples

Full code examples live in `examples/`:

| Topic | File |
|---|---|
| Module definitions, interface binding, platform modules, `startKoin` assembly, `koinViewModel()` | `examples/koin-modules.md` |

---

## Scoping Rules

| Scope | Preferred form | Fallback form | When to use |
|---|---|---|---|
| Singleton | `singleOf(::Impl) { bind<Interface>() }` | `single { ... }` | One instance for the app lifetime (repositories, HttpClient, DB) |
| ViewModel | `viewModelOf(::MyViewModel)` | `viewModel { ... }` | ViewModel instances scoped to their lifecycle |
| Factory | `factoryOf(::Impl)` | `factory { ... }` | New instance on every injection (rare — prefer singleton or ViewModel) |

Use the `*Of` constructor-reference form by default. Only use the lambda form when you cannot express the binding with a constructor reference.

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Koin module | `<layer>Module` | `datasourceModule`, `presentationModule` |
| Platform module | `android*Module` / `ios*Module` | `androidUserDatabaseModule`, `iosDatabaseModule` |

---

## Checklist: Adding DI for a New Feature

- [ ] Add repository singletons to `datasourceModule`
- [ ] Add ViewModel to `presentationModule`
- [ ] Add platform-specific bindings to the platform module if needed
- [ ] Use `koinViewModel()` in all Root composables
