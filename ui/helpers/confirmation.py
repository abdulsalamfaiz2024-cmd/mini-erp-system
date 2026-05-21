"""
Confirmation Dialog Helpers
Centralized confirmation patterns for destructive actions
"""

from tkinter import messagebox


def confirm_delete(item_name, item_type="item"):
    """
    Show confirmation dialog for delete action
    
    Args:
        item_name: Name/ID of item to delete
        item_type: Type of item (e.g., "order", "employee", "asset")
    
    Returns:
        True if user confirms, False otherwise
    """
    return messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete {item_type} '{item_name}'?\n\n"
        "This action cannot be undone.",
        icon='warning'
    )


def confirm_approve(item_name, item_type="item"):
    """
    Show confirmation dialog for approve action
    
    Args:
        item_name: Name/ID of item to approve
        item_type: Type of item
    
    Returns:
        True if user confirms, False otherwise
    """
    return messagebox.askyesno(
        "Confirm Approval",
        f"Approve {item_type} '{item_name}'?\n\n"
        "This will move the item to the next workflow state.",
        icon='question'
    )


def confirm_reject(item_name, item_type="item", reason_required=False):
    """
    Show confirmation dialog for reject action
    
    Args:
        item_name: Name/ID of item to reject
        item_type: Type of item
        reason_required: Whether to show note about reason
    
    Returns:
        True if user confirms, False otherwise
    """
    message = f"Reject {item_type} '{item_name}'?\n\n"
    if reason_required:
        message += "You will be asked to provide a reason."
    else:
        message += "This will send the item back for revision."
    
    return messagebox.askyesno(
        "Confirm Rejection",
        message,
        icon='warning'
    )


def confirm_post(item_name, item_type="item"):
    """
    Show confirmation dialog for post/finalize action
    
    Args:
        item_name: Name/ID of item to post
        item_type: Type of item
    
    Returns:
        True if user confirms, False otherwise
    """
    return messagebox.askyesno(
        "Confirm Post",
        f"Post {item_type} '{item_name}'?\n\n"
        "Once posted, this item cannot be modified.",
        icon='warning'
    )


def confirm_submit(item_name, item_type="item"):
    """
    Show confirmation dialog for submit action
    
    Args:
        item_name: Name/ID of item to submit
        item_type: Type of item
    
    Returns:
        True if user confirms, False otherwise
    """
    return messagebox.askyesno(
        "Confirm Submit",
        f"Submit {item_type} '{item_name}' for approval?\n\n"
        "The item will be sent to the next approval stage.",
        icon='question'
    )


def confirm_action(action_name, item_name, warning_message=None):
    """
    Generic confirmation dialog for any action
    
    Args:
        action_name: Name of action (e.g., "Dispose", "Archive")
        item_name: Name/ID of item
        warning_message: Optional additional warning
    
    Returns:
        True if user confirms, False otherwise
    """
    message = f"{action_name} '{item_name}'?"
    if warning_message:
        message += f"\n\n{warning_message}"
    
    return messagebox.askyesno(
        f"Confirm {action_name}",
        message,
        icon='warning'
    )
