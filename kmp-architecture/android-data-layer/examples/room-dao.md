# Room DAO — Examples

## Query Naming Pattern

Every DAO query should exist in two forms: a **one-shot suspend** version and a **reactive Flow** version.

| Query type | Naming | Return type |
|---|---|---|
| One-shot (suspend) | `getById`, `getAll`, `getByPassengerId` | `suspend fun getById(id: Long): Entity?` |
| Reactive (Flow) | `getByIdAsFlow`, `getAllAsFlow`, `getByPassengerIdAsFlow` | `fun getByIdAsFlow(id: Long): Flow<Entity?>` |

The one-shot version is the base name. The Flow version appends `AsFlow`.

```kotlin
@Dao
interface NoteDao {
    // One-shot — used for single reads, checks, or inside transactions
    @Query("SELECT * FROM notes WHERE id = :id")
    suspend fun getById(id: Long): NoteEntity?

    @Query("SELECT * FROM notes")
    suspend fun getAll(): List<NoteEntity>

    // Reactive — used for observing changes in the UI layer
    @Query("SELECT * FROM notes WHERE id = :id")
    fun getByIdAsFlow(id: Long): Flow<NoteEntity?>

    @Query("SELECT * FROM notes")
    fun getAllAsFlow(): Flow<List<NoteEntity>>

    // Write operations — suspend only, no Flow version needed
    @Insert
    suspend fun insert(note: NoteEntity): Long

    @Update
    suspend fun update(note: NoteEntity)

    @Delete
    suspend fun delete(note: NoteEntity)
}
```

**Rules:**
- Always create both versions for every read query.
- Always create `@Insert`, `@Update`, `@Delete` functions, which are suspend-only — no Flow version.
- Flow functions are **not** `suspend` — Room returns a cold Flow that emits on table changes.

## Migrations

Prefer `@Database(autoMigrations = [AutoMigration(from = 1, to = 2)])`. Use manual `Migration` objects when the schema change is too complex for auto-migration. Before using a heavy manual migration, ask the user if they want to do so or drop the database.

```kotlin
// Auto-migration — preferred
@Database(
    entities = [NoteEntity::class],
    version = 2,
    autoMigrations = [AutoMigration(from = 1, to = 2)]
)
abstract class AppDatabase : RoomDatabase() { ... }
```
