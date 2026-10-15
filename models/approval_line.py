from odoo import models, fields, api



# CATEGORY APPROVAL 

class ApprovalLine(models.Model):
    _name = 'approval.line'
    _description = 'Approval Line (Category Level)'
    _order = 'sequence'

    category_id = fields.Many2one(
        'approval.category',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(default=1)
    user_id = fields.Many2one(
        'res.users',
        required=True,
        string="User"
    )

    role = fields.Selection([
        ('approve', 'Approval Manager'),
        ('reject', 'Reject Manager')
    ], default='approve', string="Role")



# REQUEST APPROVAL 

class ApprovalRequestLine(models.Model):
    _name = 'approval.request.line'
    _description = 'Approval Request Line'
    _order = 'sequence'

    request_id = fields.Many2one(
        'approval.request',
        ondelete='cascade'
    )

    sequence = fields.Integer()
    user_id = fields.Many2one(
        'res.users',
        string="Approver"
    )

    approved = fields.Boolean(default=False)
    rejected = fields.Boolean(default=False)

    approved_date = fields.Datetime()
    rejected_date = fields.Datetime()

    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending', string="Status")

    # Helper field (optional but useful)
    is_current = fields.Boolean(
        compute='_compute_is_current',
        store=False
    )

    @api.depends('request_id')
    def _compute_is_current(self):
        for line in self:
            if line.request_id:
                pending_lines = line.request_id.approval_line_ids.filtered(
                    lambda l: l.state == 'pending'
                ).sorted('sequence')
                line.is_current = pending_lines and line == pending_lines[0]
            else:
                line.is_current = False