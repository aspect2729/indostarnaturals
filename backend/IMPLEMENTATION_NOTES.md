# Task 2.1 Implementation Notes

## Completed: Create User and Address Models

### Files Created/Modified:

1. **backend/app/models/user.py** - User model implementation
   - Implements User model with all required fields
   - Includes role enum (consumer, distributor, owner)
   - Has relationships to Address model
   - Includes timestamps (created_at, updated_at)
   - Supports both password and OAuth authentication

2. **backend/app/models/address.py** - Address model implementation
   - Implements Address model with all required fields
   - Includes relationship back to User model
   - Has is_default flag for default address selection
   - Includes timestamps (created_at, updated_at)
   - Default country set to "India"

3. **backend/app/models/__init__.py** - Updated to export models
   - Exports User and Address models
   - Exports all enum types
   - Provides clean import interface

4. **backend/alembic/versions/2024_01_15_1203-004_create_addresses_table.py** - Migration for addresses table
   - Creates addresses table with all required fields
   - Adds foreign key constraint to users table with CASCADE delete
   - Creates index on user_id for performance
   - Follows existing migration pattern

5. **backend/tests/test_models.py** - Unit tests for models
   - Tests User model creation
   - Tests all three user roles (consumer, distributor, owner)
   - Tests Google OAuth integration
   - Tests Address model creation
   - Tests optional fields handling
   - Tests default values

### Requirements Satisfied:

✅ **Requirement 2.1**: User model with role enum (consumer, distributor, owner)
- User model includes role field with UserRole enum
- Supports all three roles: CONSUMER, DISTRIBUTOR, OWNER

✅ **Requirement 6.2**: Address model with all required fields
- Address model includes: name, phone, address_line1, address_line2, city, state, postal_code, country
- Includes is_default flag for default address selection
- Has proper relationship to User model

✅ Database migration for users and addresses tables
- Users table migration already exists (002_create_users_table.py)
- Created new migration for addresses table (004_create_addresses_table.py)
- Migration includes foreign key constraint with CASCADE delete

✅ Indexes on user email and phone fields
- Email index: ix_users_email (already in migration 002)
- Phone index: ix_users_phone (already in migration 002)
- Additional index on user_id in addresses table for performance

### Model Features:

**User Model:**
- Primary key: id (Integer)
- Authentication: email, phone, hashed_password, google_id
- Profile: name
- Authorization: role (UserRole enum)
- Verification: is_email_verified, is_phone_verified
- Status: is_active
- Timestamps: created_at, updated_at
- Relationships: addresses (one-to-many)

**Address Model:**
- Primary key: id (Integer)
- Foreign key: user_id (references users.id with CASCADE delete)
- Contact: name, phone
- Location: address_line1, address_line2, city, state, postal_code, country
- Flags: is_default
- Timestamps: created_at, updated_at
- Relationships: user (many-to-one)

### Database Schema:

**users table:**
- Indexes: email, phone, google_id
- Unique constraints: email, phone
- Enum type: user_role

**addresses table:**
- Indexes: user_id
- Foreign key: user_id → users.id (CASCADE delete)
- Default value: country = 'India'

### Migration Chain:
001 (initial_schema) → 002 (create_users_table) → 003 (create_initial_owner) → **004 (create_addresses_table)**

### Testing:
- Created comprehensive unit tests in test_models.py
- Tests cover all model fields and relationships
- Tests verify default values and optional fields
- Tests verify all three user roles can be assigned

### Next Steps:
To apply the migration:
```bash
cd backend
alembic upgrade head
```

To verify the models work:
```bash
cd backend
python -m pytest tests/test_models.py -v
```
