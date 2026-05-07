from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    VENDOR = "vendor"


class VendorStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


class RouterStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class LogCategory(str, Enum):
    AUTH = "auth"
    USER_MANAGEMENT = "user_management"
    VENDOR_MANAGEMENT = "vendor_management"
    ROUTER_MANAGEMENT = "router_management"
    SETTINGS = "settings"
    PROFILE = "profile"


class LogStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class Permission(str, Enum):
    # Vendor permissions
    MANAGE_ROUTERS = "manage_routers"
    VIEW_ROUTERS = "view_routers"
    MANAGE_HOTSPOT_USERS = "manage_hotspot_users"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_PROFILE = "manage_profile"

    # SuperAdmin permissions
    MANAGE_VENDORS = "manage_vendors"
    VIEW_VENDORS = "view_vendors"
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    EXPORT_LOGS = "export_logs"
    MANAGE_SETTINGS = "manage_settings"


# Map roles to their default permissions
ROLE_PERMISSIONS: dict[UserRole, list[Permission]] = {
    UserRole.SUPERADMIN: [
        Permission.MANAGE_VENDORS,
        Permission.VIEW_VENDORS,
        Permission.MANAGE_USERS,
        Permission.VIEW_LOGS,
        Permission.EXPORT_LOGS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_ROUTERS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_PROFILE,
    ],
    UserRole.VENDOR: [
        Permission.MANAGE_ROUTERS,
        Permission.VIEW_ROUTERS,
        Permission.MANAGE_HOTSPOT_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_PROFILE,
    ],
}


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class EmailVerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
