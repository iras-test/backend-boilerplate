ALLOWED_FILE_EXTENSIONS = [
    "pdf",
    "png",
    "svg",
    "jpg",
    "jpeg",
    "docx",
    "zip",
    "kmz",
    "doc",
    "txt",
    "csv",
    "xls",
    "xlsx",
    "dot",
    "rar",
    "tar",
    "gz",
    "dwg",
    "rvt",
    "ifc",
    "skp",
    "3ds",
    "obj",
    "fbx",
    "dxf",
    "html",
    "json",
    "geojson",
]


# Document Types
DOCUMENT_TYPE_OTHER = "other"

DOCUMENT_TYPES = (
    (DOCUMENT_TYPE_OTHER, "Other"),
)

NOTIFICATION_CHANNEL_EMAIL = "email"
NOTIFICATION_CHANNEL_SMS = "sms"
NOTIFICATION_CHANNEL_SYSTEM_PUSH = "system_push"

NOTIFICATION_CHANNEL_CHOICES = [
    (NOTIFICATION_CHANNEL_EMAIL, "Email"),
    (NOTIFICATION_CHANNEL_SMS, "SMS"),
    (NOTIFICATION_CHANNEL_SYSTEM_PUSH, "System Push"),
]

WORKFLOW_ACTION_TYPE_FORWARD = "forward"
WORKFLOW_ACTION_TYPE_BACKWARD = "backward"
WORKFLOW_ACTION_TYPE_APPROVE = "approve"
WORKFLOW_ACTION_TYPE_REJECT = "reject"

WORKFLOW_ACTION_TYPE_CHOICES = [
    (WORKFLOW_ACTION_TYPE_FORWARD, "Forward"),
    (WORKFLOW_ACTION_TYPE_BACKWARD, "Send Back"),
    (WORKFLOW_ACTION_TYPE_APPROVE, "Approve"),
    (WORKFLOW_ACTION_TYPE_REJECT, "Reject"),
]