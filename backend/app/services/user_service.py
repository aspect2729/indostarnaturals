"""User Service

Handles user management operations including creation, authentication, and role management.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.enums import UserRole, DistributorStatus
from app.models.audit_log import AuditLog
from app.services.auth_service import token_service, password_service
from app.services.otp_service import otp_service
from app.services.email_service import email_service
from app.services.oauth_service import google_oauth_service


class UserService:
    """Service for user management operations"""
    
    @staticmethod
    def create_user(
        phone: str,
        name: str,
        role: UserRole,
        email: Optional[str] = None,
        password: Optional[str] = None,
        google_id: Optional[str] = None,
        db: Session = None
    ) -> User:
        """
        Create a new user with role assignment.
        
        Args:
            phone: User's phone number
            name: User's name
            role: User role (consumer, distributor, or owner)
            email: User's email address (optional)
            password: Plain text password (optional, will be hashed)
            google_id: Google OAuth ID (optional)
            db: Database session
            
        Returns:
            Created User object
        """
        # Hash password if provided
        hashed_password = None
        if password:
            hashed_password = password_service.hash_password(password)
        
        # Create user
        user = User(
            phone=phone,
            name=name,
            email=email,
            role=role,
            hashed_password=hashed_password,
            google_id=google_id,
            is_phone_verified=False,
            is_email_verified=False,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_with_otp(
        phone: str,
        otp: str,
        db: Session
    ) -> Optional[Tuple[User, str, str]]:
        """
        Authenticate user with OTP and return JWT tokens.
        
        Args:
            phone: User's phone number
            otp: OTP code to verify
            db: Database session
            
        Returns:
            Tuple of (User, access_token, refresh_token) if successful, None otherwise
        """
        # Verify OTP
        if not otp_service.verify_otp(phone, otp):
            return None
        
        # Find user by phone
        user = db.query(User).filter(User.phone == phone).first()
        
        if not user:
            # Create new consumer user if doesn't exist
            user = UserService.create_user(
                phone=phone,
                name=f"User {phone[-4:]}",  # Default name
                role=UserRole.CONSUMER,
                db=db
            )
        
        # Mark phone as verified
        if not user.is_phone_verified:
            user.is_phone_verified = True
            db.commit()
            db.refresh(user)
        
        # Generate JWT tokens
        tokens = token_service.create_token_pair(
            user_id=user.id,
            email=user.email,
            phone=user.phone,
            role=user.role.value
        )
        
        return user, tokens['access_token'], tokens['refresh_token']
    
    @staticmethod
    def authenticate_with_google(
        google_token: str,
        db: Session
    ) -> Optional[Tuple[User, str, str]]:
        """
        Authenticate user with Google OAuth and return JWT tokens.
        
        Args:
            google_token: Google OAuth ID token
            db: Database session
            
        Returns:
            Tuple of (User, access_token, refresh_token) if successful, None otherwise
        """
        # Verify Google token
        google_info = google_oauth_service.verify_google_token(google_token)
        
        if not google_info:
            return None
        
        # Get or create user
        user = google_oauth_service.get_or_create_user_from_google(google_info, db)
        
        if not user:
            return None
        
        # Generate JWT tokens
        tokens = token_service.create_token_pair(
            user_id=user.id,
            email=user.email,
            phone=user.phone,
            role=user.role.value
        )
        
        return user, tokens['access_token'], tokens['refresh_token']
    
    @staticmethod
    def send_otp(phone: str) -> bool:
        """
        Generate and send OTP to phone number.
        
        Args:
            phone: Phone number to send OTP to
            
        Returns:
            True if OTP was sent successfully
        """
        return otp_service.create_and_send_otp(phone)
    
    @staticmethod
    def verify_email(token: str, db: Session) -> Optional[User]:
        """
        Verify email with verification token.
        
        Args:
            token: Email verification token
            db: Database session
            
        Returns:
            User object if verification successful, None otherwise
        """
        # Verify token and get email
        email = email_service.verify_token(token)
        
        if not email:
            return None
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        # Mark email as verified
        user.is_email_verified = True
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_user_role(
        user_id: int,
        new_role: UserRole,
        actor_id: int,
        db: Session
    ) -> Optional[User]:
        """
        Update user role with audit logging.
        
        Args:
            user_id: ID of user to update
            new_role: New role to assign
            actor_id: ID of user performing the action
            db: Database session
            
        Returns:
            Updated User object if successful, None otherwise
        """
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Store old role for audit log
        old_role = user.role
        
        # Update role
        user.role = new_role
        
        # Create audit log entry
        audit_log = AuditLog(
            actor_id=actor_id,
            action_type="USER_ROLE_UPDATED",
            object_type="USER",
            object_id=user_id,
            details={
                "old_role": old_role.value,
                "new_role": new_role.value,
                "user_email": user.email,
                "user_phone": user.phone
            }
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_all_users(
        db: Session,
        role_filter: Optional[UserRole] = None,
        status_filter: Optional[bool] = None,
        distributor_status_filter: Optional[DistributorStatus] = None
    ) -> list[User]:
        """
        Get all users with role and status filtering.
        
        Args:
            db: Database session
            role_filter: Filter by user role (optional)
            status_filter: Filter by active status (optional)
            distributor_status_filter: Filter by distributor status (optional)
            
        Returns:
            List of User objects matching the filters
        """
        query = db.query(User)
        
        # Apply role filter
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        # Apply status filter
        if status_filter is not None:
            query = query.filter(User.is_active == status_filter)
        
        # Apply distributor status filter
        if distributor_status_filter:
            query = query.filter(User.distributor_status == distributor_status_filter)
        
        return query.order_by(User.created_at.desc()).all()
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_phone(phone: str, db: Session) -> Optional[User]:
        """
        Get user by phone number.
        
        Args:
            phone: Phone number
            db: Database session
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.phone == phone).first()
    
    @staticmethod
    def get_user_by_email(email: str, db: Session) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address
            db: Database session
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def register_distributor(
        phone: str,
        email: str,
        name: str,
        business_name: str,
        db: Session
    ) -> User:
        """
        Register a new distributor with pending status.
        
        Args:
            phone: Phone number
            email: Email address
            name: User's name
            business_name: Business name
            db: Database session
            
        Returns:
            Created User object with pending distributor status
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.phone == phone) | (User.email == email)
        ).first()
        
        if existing_user:
            raise ValueError("User with this phone or email already exists")
        
        # Create user with consumer role and pending distributor status
        user = User(
            phone=phone,
            email=email,
            name=name,
            role=UserRole.CONSUMER,  # Start as consumer until approved
            distributor_status=DistributorStatus.PENDING,
            is_phone_verified=False,
            is_email_verified=False,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send confirmation email that application is pending
        email_service.send_email(
            to_email=email,
            subject="Distributor Application Received",
            body=f"Dear {name},\n\nYour distributor application for {business_name} has been received and is pending approval. You will receive an email once your application is reviewed.\n\nThank you,\nIndoStar Naturals Team"
        )
        
        return user
    
    @staticmethod
    def approve_distributor(
        user_id: int,
        approved: bool,
        actor_id: int,
        db: Session
    ) -> Optional[User]:
        """
        Approve or reject a distributor application.
        
        Args:
            user_id: ID of user to approve/reject
            approved: True to approve, False to reject
            actor_id: ID of owner performing the action
            db: Database session
            
        Returns:
            Updated User object if successful, None otherwise
        """
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Check if user has pending distributor status
        if user.distributor_status != DistributorStatus.PENDING:
            raise ValueError("User does not have pending distributor status")
        
        # Store old status for audit log
        old_status = user.distributor_status
        old_role = user.role
        
        if approved:
            # Approve distributor
            user.distributor_status = DistributorStatus.APPROVED
            user.role = UserRole.DISTRIBUTOR
            
            # Send approval email
            if user.email:
                email_service.send_email(
                    to_email=user.email,
                    subject="Distributor Application Approved",
                    body=f"Dear {user.name},\n\nCongratulations! Your distributor application has been approved. You now have access to distributor pricing and features.\n\nYou can log in to your account to start placing orders at wholesale prices.\n\nThank you,\nIndoStar Naturals Team"
                )
        else:
            # Reject distributor
            user.distributor_status = DistributorStatus.REJECTED
            
            # Send rejection email
            if user.email:
                email_service.send_email(
                    to_email=user.email,
                    subject="Distributor Application Status",
                    body=f"Dear {user.name},\n\nThank you for your interest in becoming a distributor. Unfortunately, we are unable to approve your application at this time.\n\nIf you have any questions, please contact our support team.\n\nThank you,\nIndoStar Naturals Team"
                )
        
        # Create audit log entry
        audit_log = AuditLog(
            actor_id=actor_id,
            action_type="DISTRIBUTOR_APPROVAL" if approved else "DISTRIBUTOR_REJECTION",
            object_type="USER",
            object_id=user_id,
            details={
                "old_status": old_status.value if old_status else None,
                "new_status": user.distributor_status.value,
                "old_role": old_role.value,
                "new_role": user.role.value,
                "user_email": user.email,
                "user_phone": user.phone,
                "approved": approved
            }
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(user)
        
        return user


# Create singleton instance
user_service = UserService()
