"""Unit tests for UserService"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.user_service import UserService
from app.models import User, Address
from app.models.enums import UserRole
from app.core.exceptions import ValidationException, NotFoundException
from decimal import Decimal


@pytest.mark.unit
class TestUserService:
    """Unit tests for UserService methods"""

    @pytest.fixture
    def user_service(self, db_session):
        """Create UserService instance"""
        return UserService(db_session)

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, db_session):
        """Test successful user creation"""
        user_data = {
            'email': 'newuser@example.com',
            'phone': '+919876543210',
            'name': 'New User',
            'role': UserRole.CONSUMER
        }
        
        user = await user_service.create_user(**user_data)
        
        assert user.email == user_data['email']
        assert user.phone == user_data['phone']
        assert user.name == user_data['name']
        assert user.role == user_data['role']
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, test_user):
        """Test user creation with duplicate email fails"""
        user_data = {
            'email': test_user.email,
            'phone': '+919876543211',
            'name': 'Duplicate User',
            'role': UserRole.CONSUMER
        }
        
        with pytest.raises(ValidationException):
            await user_service.create_user(**user_data)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service, test_user):
        """Test getting user by ID"""
        user = await user_service.get_user_by_id(test_user.id)
        
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service):
        """Test getting non-existent user"""
        with pytest.raises(NotFoundException):
            await user_service.get_user_by_id(99999)

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_service, test_user):
        """Test getting user by email"""
        user = await user_service.get_user_by_email(test_user.email)
        
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_phone_success(self, user_service, test_user):
        """Test getting user by phone"""
        user = await user_service.get_user_by_phone(test_user.phone)
        
        assert user.id == test_user.id
        assert user.phone == test_user.phone

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, test_user):
        """Test updating user information"""
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com'
        }
        
        updated_user = await user_service.update_user(test_user.id, **update_data)
        
        assert updated_user.name == update_data['name']
        assert updated_user.email == update_data['email']

    @pytest.mark.asyncio
    async def test_update_user_role_with_audit(self, user_service, test_user, test_owner, db_session):
        """Test updating user role creates audit log"""
        new_role = UserRole.DISTRIBUTOR
        
        updated_user = await user_service.update_user_role(
            user_id=test_user.id,
            new_role=new_role,
            actor_id=test_owner.id
        )
        
        assert updated_user.role == new_role
        
        # Check audit log was created
        from app.models import AuditLog
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.actor_id == test_owner.id,
            AuditLog.object_id == test_user.id,
            AuditLog.action_type == 'ROLE_UPDATED'
        ).first()
        
        assert audit_log is not None
        assert audit_log.details['old_role'] == UserRole.CONSUMER.value
        assert audit_log.details['new_role'] == new_role.value

    @pytest.mark.asyncio
    async def test_add_address_success(self, user_service, test_user):
        """Test adding address to user"""
        address_data = {
            'name': 'Test User',
            'phone': '+919876543210',
            'address_line1': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '123456',
            'country': 'India'
        }
        
        address = await user_service.add_address(test_user.id, **address_data)
        
        assert address.user_id == test_user.id
        assert address.address_line1 == address_data['address_line1']

    @pytest.mark.asyncio
    async def test_get_user_addresses(self, user_service, test_user, test_address):
        """Test getting all user addresses"""
        addresses = await user_service.get_user_addresses(test_user.id)
        
        assert len(addresses) > 0
        assert addresses[0].user_id == test_user.id

    @pytest.mark.asyncio
    async def test_update_address_success(self, user_service, test_address):
        """Test updating address"""
        update_data = {
            'city': 'Updated City',
            'state': 'Updated State'
        }
        
        updated_address = await user_service.update_address(
            test_address.id,
            test_address.user_id,
            **update_data
        )
        
        assert updated_address.city == update_data['city']
        assert updated_address.state == update_data['state']

    @pytest.mark.asyncio
    async def test_delete_address_success(self, user_service, test_address):
        """Test deleting address"""
        result = await user_service.delete_address(test_address.id, test_address.user_id)
        
        assert result is True
        
        # Verify address is deleted
        with pytest.raises(NotFoundException):
            await user_service.get_address_by_id(test_address.id, test_address.user_id)

    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_service, test_user):
        """Test deactivating user"""
        deactivated_user = await user_service.deactivate_user(test_user.id)
        
        assert deactivated_user.is_active is False

    @pytest.mark.asyncio
    async def test_activate_user(self, user_service, test_user):
        """Test activating user"""
        # First deactivate
        await user_service.deactivate_user(test_user.id)
        
        # Then activate
        activated_user = await user_service.activate_user(test_user.id)
        
        assert activated_user.is_active is True
