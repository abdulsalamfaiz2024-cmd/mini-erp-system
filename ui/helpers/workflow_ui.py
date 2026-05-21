"""
Workflow UI Helper
Centralized logic for workflow state visualization and action guidance
"""

class WorkflowUI:
    """Helper for consistent workflow UI states"""
    
    # Standard colors for states
    COLORS = {
        'draft': '#808080',      # Gray
        'pending': '#FFA500',    # Orange
        'approved': '#28a745',   # Green
        'rejected': '#dc3545',   # Red
        'completed': '#17a2b8',  # Teal
        'posted': '#6f42c1',     # Purple
        'paid': '#28a745',       # Green
        'invoiced': '#007bff',   # Blue
        'active': '#28a745',     # Green
        'inactive': '#6c757d',   # Gray
        'retired': '#343a40',    # Dark Gray
    }
    
    # Next action mapping
    NEXT_ACTIONS = {
        'draft': 'Submit for Approval',
        'pending': 'Approve or Reject',
        'approved': 'Finalize / Process',
        'rejected': 'Revise and Resubmit',
        'completed': 'No Actions Required',
        'posted': 'No Actions Required',
        'paid': 'No Actions Required',
        'invoiced': 'Record Payment',
        'active': 'Active Monitor',
        'inactive': 'Archive or Reactivate',
    }
    
    @staticmethod
    def get_state_color(status):
        """Get color hex for status"""
        if not status:
            return '#000000'
        return WorkflowUI.COLORS.get(status.lower(), '#000000')
    
    @staticmethod
    def get_next_action(status, document_type="Document"):
        """Get human readable next action"""
        if not status:
            return "Unknown State"
        
        action = WorkflowUI.NEXT_ACTIONS.get(status.lower())
        if action:
            return action
            
        # Default fallbacks
        if 'submitted' in status.lower():
            return "Approve or Reject"
        if 'wait' in status.lower():
            return "Wait for Process"
            
        return "View Details"
    
    @staticmethod
    def get_visible_actions(status, all_actions):
        """
        Filter actions based on status
        
        Args:
            status: Current item status
            all_actions: Dict of {action_key: {config}}
            
        Returns:
            List of visible action configs
        """
        # This logic is usually implementation specific
        # but common patterns can be here
        pass
