# Where to find the data shapes

Search for the marker, then read each match. Start with the database schema when one exists: it is
what is really stored, and classes can differ from it.

| Stack | Own table or collection (`class`) | `embedded` and `enum` | Relations | `referenceTypes` |
|---|---|---|---|---|
| Kotlin or Java, Spring Data Mongo | `@Document` | data classes in fields, `enum class` | `ObjectId` fields, `@DBRef` | `ObjectId` |
| Kotlin or Java, JPA and Hibernate | `@Entity`, `@Table` | `@Embeddable`, `@Enumerated` | `@ManyToOne`, `@OneToMany`, `@ManyToMany` | `Long`, `UUID` |
| Android Room, KMP | `@Entity` | `@Embedded`, `@TypeConverter` targets | `@ForeignKey`, `@Relation` | `Long`, `String` |
| TypeScript, Prisma | `model` in `schema.prisma` | `type`, `enum` | `@relation` | `String`, `Int` |
| TypeScript, TypeORM | `@Entity()` | `@Column(() => X)`, enums | `@ManyToOne`, `@OneToMany` | `string`, `number` |
| TypeScript, Mongoose | `new Schema`, `mongoose.model` | nested schemas | `ref:` | `ObjectId` |
| TypeScript, Drizzle | `pgTable`, `sqliteTable` | `pgEnum`, json columns | `references()`, `relations()` | `uuid`, `integer` |
| Python, SQLAlchemy | `Base` subclasses, `__tablename__` | composite types, `Enum` | `ForeignKey`, `relationship` | `UUID`, `int` |
| Python, Django | `models.Model` | `TextChoices`, `JSONField` | `ForeignKey`, `ManyToManyField` | `int`, `UUID` |
| Python, Beanie or SQLModel | `Document`, `SQLModel, table=True` | Pydantic `BaseModel`, `Enum` | `Link`, `Relationship` | `PydanticObjectId`, `UUID` |
| C#, EF Core | `DbSet<T>` in the `DbContext` | `[Owned]`, `OwnsOne`, enums | navigation properties, `OnModelCreating` | `Guid`, `int` |
| Go | GORM models, sqlc queries, `bson` tags | nested structs, const blocks | `foreignKey` tags, id fields | `uuid.UUID`, `uint`, `primitive.ObjectID` |
| Ruby on Rails | `db/schema.rb`, `app/models` | `enum`, `store_accessor` | `belongs_to`, `has_many` | `integer`, `uuid` |
| PHP, Laravel or Doctrine | migrations, Eloquent models, `#[Entity]` | casts, PHP enums | `belongsTo`, `hasMany`, `#[ManyToOne]` | `int`, `string` |
| Rust | Diesel `schema.rs`, SeaORM entities | `#[derive(DbEnum)]`, nested structs | `joinable!`, `Related` | `Uuid`, `i64` |
| Swift | SwiftData `@Model`, Core Data entities | `Codable` structs, enums | `@Relationship` | `UUID` |
| Plain SQL | `CREATE TABLE` in migrations | `CREATE TYPE`, check constraints | `REFERENCES` | `uuid`, `bigint` |

No database layer? Model what crosses the boundary instead: OpenAPI, GraphQL or Protobuf schemas,
or the request and response types. Say in the `--intro` text which of these the page shows.

Migrations can undo each other, so read the latest schema, not the first migration that matches.
A class that only maps a request or response is not part of the stored model.
