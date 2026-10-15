from odoo import models, fields, api
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    
    # BASIC
    name = fields.Char(required=True)
    sequence = fields.Char(default='New', readonly=True)

    category_id = fields.Many2one('approval.category', required=True)

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    request_date = fields.Date(default=fields.Date.today)

    
    # AUTO NAME
    
    @api.onchange('category_id')
    def _onchange_category(self):
        if self.category_id:
            self.name = self.category_id.name

    
    # FIELDS
    
    product = fields.Char()
    qty = fields.Float()
    amount = fields.Float()
    partner = fields.Char()
    document = fields.Text()

    deadline = fields.Date(string="Deadline")

    description = fields.Text()
    internal_note = fields.Text()
    reject_reason = fields.Text(readonly=True)

    
    # STATE

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)

    
    
    
    approval_line_ids = fields.One2many('approval.request.line', 'request_id')
    current_approver = fields.Many2one('res.users')

    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', 'New') == 'New':
                vals['sequence'] = self.env['ir.sequence'].next_by_code('approval.request') or 'New'

        records = super().create(vals_list)

        for rec in records:
            rec._create_approval_lines()

        return records


    #  APPROVAL LINES
    
    def _create_approval_lines(self):
        for rec in self:
            rec.approval_line_ids = [(5, 0, 0)]

            if not rec.category_id.approval_line_ids:
                return

            lines = []
            for line in rec.category_id.approval_line_ids:
                lines.append((0, 0, {
                    'user_id': line.user_id.id,
                    'sequence': line.sequence,
                    'state': 'pending',
                }))

            rec.approval_line_ids = lines

    
    # CONFIRM
    
    def action_confirm(self):
        for rec in self:
            if not rec.approval_line_ids:
                raise UserError("No approval users configured!")

            rec.state = 'confirmed'
            rec._set_next_approver()

    
    # APPROVE (FINAL FIXED)
    
    def action_approve(self):
        for rec in self:

            # Prevent duplicate approve
            if rec.state == 'approved':
                raise UserError("Already approved.")

            # Allow re-approve if rejected
            if rec.state == 'rejected':
                rec.state = 'approved'
                rec.current_approver = False
                return

            line = rec.approval_line_ids.filtered(
                lambda l: l.user_id == self.env.user and l.state == 'pending'
            )

            if not line:
                raise UserError("No pending approval for you.")

            line.write({
                'state': 'approved',
                'approved': True,
                'approved_date': fields.Datetime.now(),
            })

            pending = rec.approval_line_ids.filtered(lambda l: l.state == 'pending')

            if pending:
                rec.current_approver = pending.sorted('sequence')[0].user_id
            else:
                rec.state = 'approved'
                rec.current_approver = False

    # REJECT
    
    def action_reject(self):
        for rec in self:

            # Prevent duplicate reject
            if rec.state == 'rejected':
                raise UserError("Already rejected.")

            line = rec.approval_line_ids.filtered(
                lambda l: l.user_id == self.env.user and l.state == 'pending'
            )

            if not line:
                # Allow reject anytime fallback
                rec.state = 'rejected'
                rec.current_approver = False
                return

            line.write({
                'state': 'rejected',
                'rejected': True,
                'rejected_date': fields.Datetime.now(),
            })

            rec.state = 'rejected'
            rec.current_approver = False

    
    
    
    def action_reset(self):
        for rec in self:
            rec.state = 'draft'
            rec.current_approver = False
            rec._create_approval_lines()

    
    #  REPORT
    
    def action_print_request(self):
        return self.env.ref('approval_request.action_report_approval_request').report_action(self)

    
    def _set_next_approver(self):
        for rec in self:
            first = rec.approval_line_ids.sorted('sequence')[:1]
            rec.current_approver = first.user_id if first else False