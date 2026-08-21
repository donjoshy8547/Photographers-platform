"""
Tests for Accounts App
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser, UserRole


class UserModelTest(TestCase):
    """Test CustomUser model"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=UserRole.CLIENT,
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, UserRole.CLIENT)
        self.assertTrue(self.user.is_active_account)
    
    def test_user_role_properties(self):
        """Test role property methods"""
        self.assertTrue(self.user.is_client)
        self.assertFalse(self.user.is_photographer)
        self.assertFalse(self.user.is_assistant)
    
    def test_full_name(self):
        """Test full name property"""
        self.assertEqual(self.user.full_name, 'Test User')


class AuthenticationServiceTest(TestCase):
    """Test authentication service"""
    
    def test_register_user(self):
        """Test user registration"""
        from apps.accounts.services import AuthenticationService
        
        user, error = AuthenticationService.register_user(
            username='newuser',
            email='new@example.com',
            password='securepass123',
            role=UserRole.PHOTOGRAPHER
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(user)
        self.assertEqual(user.role, UserRole.PHOTOGRAPHER)
    
    def test_duplicate_email(self):
        """Test duplicate email registration"""
        from apps.accounts.services import AuthenticationService
        
        # First registration
        AuthenticationService.register_user(
            username='user1',
            email='dup@example.com',
            password='pass123',
            role=UserRole.CLIENT
        )
        
        # Try duplicate
        user, error = AuthenticationService.register_user(
            username='user2',
            email='dup@example.com',
            password='pass456',
            role=UserRole.CLIENT
        )
        
        self.assertIsNotNone(error)
        self.assertIsNone(user)


class ViewsTest(TestCase):
    """Test account views"""
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_register_page(self):
        """Test register page loads"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')