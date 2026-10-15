from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ApprovalCategory(models.Model):
    _name = 'approval.category'
    _description = 'Approval Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    
    # BASIC FIELDS

    name = fields.Char(string="Category Name", required=True, tracking=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer(default=10)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company)
    
    
    show_product = fields.Boolean(string="Show Product")
    show_qty = fields.Boolean(string="Show Quantity")
    show_amount = fields.Boolean(string="Show Amount")
    show_partner = fields.Boolean(string="Show Partner")
    show_document = fields.Boolean(string="Show Document")

    
    # APPROVAL LINES 
    approval_line_ids = fields.One2many(
        'approval.line',
        'category_id',
        string="Approval Lines"
    )

    
    # BUTTON
    
    request_count = fields.Integer(
        compute="_compute_request_count"
    )

    def _compute_request_count(self):
        for rec in self:
            rec.request_count = self.env['approval.request'].search_count([
                ('category_id', '=', rec.id)
            ])

    
    # VALIDATION (FIXED)
    @api.constrains('approval_line_ids')
    def _check_approvers(self):
        for rec in self:
            if not rec.approval_line_ids:
                raise ValidationError("Please add at least one Approval Line!")

    # ACTION
    
    def action_view_requests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requests',
            'res_model': 'approval.request',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.id)],
        }