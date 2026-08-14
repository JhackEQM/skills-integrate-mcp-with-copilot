# Database Setup Guide

This project uses SQLAlchemy ORM with MySQL for persistent data storage and Alembic for database migrations.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MySQL database (if not using dev environment):
```sql
CREATE DATABASE mergington_school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'merging_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON mergington_school.* TO 'merging_user'@'localhost';
FLUSH PRIVILEGES;
```

3. Configure database connection via environment variable:
```bash
export DATABASE_URL="mysql+mysqlconnector://merging_user:your_secure_password@localhost:3306/mergington_school"
```

4. Initialize the database with migrations:
```bash
python init_db.py
```

To also load sample data:
```bash
python init_db.py --seed
```

## Project Structure

```
src/
├── app.py              # FastAPI application with endpoints
├── database.py         # SQLAlchemy setup and session management
├── models.py           # SQLAlchemy ORM models (Activity, Student)
├── schemas.py          # Pydantic schemas for API validation
└── static/             # Frontend files

alembic/
├── versions/           # Database migration scripts
├── env.py              # Alembic environment configuration
├── script.py.mako      # Migration template
└── README              # Alembic documentation

init_db.py             # Database initialization script
alembic.ini            # Alembic configuration
```

## Database Migrations

This project uses Alembic for version control of database schema changes.

### Initial Setup

The initial migration (`001_initial.py`) creates:
- **activities** table: Stores activity details (name, description, schedule, capacity)
- **students** table: Stores student information (email, name)
- **student_activity** table: Join table for many-to-many relationship

### Running Migrations

To upgrade to the latest migration:
```bash
alembic upgrade head
```

To downgrade to a specific revision:
```bash
alembic downgrade -1        # Go back one revision
alembic downgrade 001_initial  # Go to a specific revision
```

### Creating New Migrations

When you modify the models (src/models.py), create a new migration:

1. **With database connection** (recommended):
```bash
alembic revision --autogenerate -m "Description of changes"
```

2. **Manually** (when database isn't available):
```bash
alembic revision -m "Description of changes"
```

Then edit the generated file in `alembic/versions/` to add the `upgrade()` and `downgrade()` functions.

### Migration Best Practices

- Always create a migration after model changes
- Use descriptive message names
- Test migrations on a copy of your database first
- Keep migrations reversible with proper `downgrade()` functions
- Never modify existing migration files - create new ones instead

## Key Features

- **Activity Model**: Stores activity details (name, description, schedule, capacity)
- **Student Model**: Stores student information (email, name)
- **Many-to-Many Relationship**: Links students to activities via `student_activity` table
- **Automatic Initialization**: Database tables created on startup
- **Sample Data**: Initial activities and participants loaded on first run
- **Session Management**: FastAPI dependency injection for database sessions

## API Endpoints

### Activities
- `GET /activities` - Get all activities as a dictionary
- `GET /activities/{activity_id}` - Get specific activity details
- `POST /activities` - Create a new activity
- `PUT /activities/{activity_id}` - Update an activity
- `POST /activities/{activity_name}/signup` - Sign up for an activity
- `DELETE /activities/{activity_name}/unregister` - Unregister from activity

### Health
- `GET /health` - Health check endpoint

## Data Persistence

✅ All data is now persisted in the MySQL database
✅ Data survives server restarts
✅ No more in-memory storage limitations
✅ Supports unlimited growth of activities and students

## Development

For development, the application uses MySQL connection. Ensure MySQL server is running before starting the application.

Run the application:
```bash
uvicorn app:app --reload
```

Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
