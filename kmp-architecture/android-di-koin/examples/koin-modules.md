# Koin Modules — Examples

Prefer the constructor-reference overloads (`singleOf`, `viewModelOf`, `factoryOf`) — they are more concise and let Koin resolve parameters automatically. Only fall back to the lambda overloads (`single { ... }`, `viewModel { ... }`, `factory { ... }`) when constructor injection alone is not enough, e.g. when you need to call a factory method, pass a named/qualified dependency, or do post-construction setup.

## Datasource module (all data-layer singletons)

```kotlin
val datasourceModule = module {
    single<AppDatabase> { CreateAppDatabase(get()).getDatabase() }
    single { get<AppDatabase>().noteDao() }
    singleOf(::Preferencemanager)
    singleOf(::NoteRepository)
}
```

## Binding an implementation to its interface

When a class implements a domain interface, bind it so injection sites can depend on the interface:

```kotlin
val datasourceModule = module {
    singleOf(::RoomNoteDataSource) { bind<NoteLocalDataSource>() }
    singleOf(::OfflineFirstNoteRepository) { bind<NoteRepository>() }
}
```

## Presentation module (all ViewModels in one module)

```kotlin
val presentationModule = module {
    viewModelOf(::NoteListViewModel)
    viewModelOf(::NoteDetailViewModel)
    viewModelOf(::SettingsViewModel)
}
```

## Platform-specific module

```kotlin
// androidMain
val androidPlatformModule = module {
    single<RoomDatabase.Builder<AppDatabase>> { androidAppDatabaseBuilder(androidContext()) }
    single<LocationTracker> { AndroidLocationTracker(androidContext()) }
    single<DataStore<Preferences>> { createAndroidDataStore(androidContext()) }
}
```

## Assembly in `:app`

Register all modules in the `Application` class:

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@App)
            modules(
                androidPlatformModule,
                datasourceModule,
                presentationModule
            )
        }
    }
}
```

## Injecting in Composables

Always use `koinViewModel()` in Root composables:

```kotlin
@Composable
fun NoteListRoot(
    onNavigateToDetail: (String) -> Unit,
    viewModel: NoteListViewModel = koinViewModel()
) { ... }
```

Never pass ViewModels down the composable tree — inject at the Root level only.
