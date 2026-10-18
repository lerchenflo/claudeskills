# Project Init Plan Template

Present this structured plan for approval after the interview:

```
## Project Init Plan: [Project Name]

**Package**: `[package.name]`
**Platforms**: [Android, iOS, Desktop]
**Module strategy**: [Multi-module / Single-module]

### Infrastructure

| Component | Include | Details |
|---|---|---|
| Dependencies | Yes | [what goes into libs.versions.toml] |
| Module structure | [Yes/No] | [modules to create, or "package-based in :composeApp"] |
| Navigation | [Yes/No] | [Nav 3, type-safe routes] |
| Networking | [Yes/No] | [auth client, non-auth client, WebSockets] |
| Database | [Yes/No] | [Room + KSP] |
| Preferences | [Yes/No] | [DataStore, encrypted?] |
| Error handling | [Yes/No] | [Result + DataError] |
| Image loading | [Yes/No] | [Coil] |
| DI | Yes | [Koin modules] |
| Testing | [Yes/No] | [JUnit5, Turbine, AssertK] |

### Features to Scaffold

| Feature | Screens | Layers |
|---|---|---|
| [name] | [screens] | [domain/data/presentation] |

### Generation Order

1. Version catalog (libs.versions.toml)
2. Module structure (if multi-module)
3. Error handling (Result, DataError)
4. Networking infrastructure (HttpClient, safe call helpers, token storage)
5. Database infrastructure (Room DB class, base config)
6. Preferences (DataStore setup, encrypted storage)
7. DI wiring (Koin modules, startKoin)
8. Navigation (routes, nav graphs, NavHost)
9. Feature scaffolding (domain -> data -> presentation per feature)
10. Testing infrastructure (test deps, base test setup)

Does this plan look correct? Say "go" to generate, or tell me what to change.
```

Wait for explicit approval before generating any code.
